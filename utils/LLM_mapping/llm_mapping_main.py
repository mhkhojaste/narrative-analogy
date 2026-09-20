from itertools import combinations, chain
from typing import List, Tuple, Dict, Set
from tqdm import tqdm
import openai
import re
from collections import defaultdict
from sklearn import metrics
import sklearn
from sklearn.covariance import LedoitWolf
import sys
import json
import numpy as np
import os
import time
import base64
import requests
import ast
import pickle
from transformers import AutoModelForCausalLM, AutoTokenizer
import random
import pandas as pd
import copy
import torch
from sentence_transformers.util import normalize_embeddings
from hungarian_algorithm import algorithm
from scipy.optimize import linear_sum_assignment
import networkx as nx
import matplotlib.pyplot as plt
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Sequence

from utils.helper_utils import *
from Data.Prompts import prompts_llm_event_mapping

random.seed(309)

RESULTS_DIR = "results/"
os.makedirs(RESULTS_DIR, exist_ok=True)
RESULTS_PATH = RESULTS_DIR + "results_llm_mapping.csv"


INVALID_ANSWER_INDEX = 5
ARN_CATEGORIES = ["low-near", "low-far","high-near", "high-far",]
LLM_RESULTS_COLUMNS = ["id", "model", "unit", "config", "MCQ accuracy", "ARN accuracy", "arn low-near", "arn low-far", "arn high-near", "arn high-far",]


def split_story_into_sentences(story):
    story = re.sub(r"\s+", " ", str(story)).strip()
    if not story:
        return []
    sentences = re.split(r"(?<=[.!?])\s+(?=[\"'([{]*[A-Z0-9])", story)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def prepare_story_by_unit(story, unit, events=None):
    unit = unit.strip().lower()

    if unit == "story":
        return str(story).strip()

    if unit == "sentence":
        sentences = split_story_into_sentences(story)
        return "\n".join(
            [f"{index + 1}. {sentence}" for index, sentence in enumerate(sentences)]
        )

    if unit == "event":
        if events is None:
            raise ValueError("Events must be provided when unit is 'event'.")

        return "\n".join(
            [f"{index + 1}. {event}" for index, event in enumerate(events)]
        )

    raise ValueError(f"Unknown unit: {unit}")


def load_event_data(args):
    model_name = model_short_dict.get(args.model)

    dataset_name = args.dataset.lower()

    path = (
        f"Data_new/Units/"
        f"{model_name}events_{dataset_name}.pkl"
    )

    with open(path, "rb") as file:
        return pickle.load(file)

def parse_mcq_choices(choices):
    if isinstance(choices, (list, tuple)):
        return [str(choice).strip() for choice in choices]

    if isinstance(choices, str):
        try:
            parsed_choices = json.loads(choices)
        except json.JSONDecodeError:
            parsed_choices = ast.literal_eval(choices)

        if not isinstance(parsed_choices, (list, tuple)):
            raise ValueError("MCQ choices must be a list.")

        return [str(choice).strip() for choice in parsed_choices]

    raise ValueError(f"Unknown MCQ choices format: {type(choices)}")


def get_llm_mapping_stories(main_data, index, args):
    if args.dataset == "ARN":
        row = main_data.iloc[index]
        base_story = row["query_narrative"].strip()
        target_stories = [
            row["first_choice"].strip(),
            row["second_choice"].strip(),
        ]

    elif args.dataset == "MCQ":
        sample = main_data[index]
        base_story = sample["source"].strip()
        target_stories = parse_mcq_choices(sample["choices"])

        if len(target_stories) != 4:
            raise ValueError(f"MCQ sample {index} has {len(target_stories)} targets instead of 4.")

    else:
        raise ValueError(f"Unknown dataset: {args.dataset}")

    return base_story, target_stories


def get_llm_mapping_prompt(args):
    prompt_name = args.config.get("prompt")

    valid_prompts = ["prompt_event_mapping_ARN_zs", "prompt_event_mapping_ARN_cot", "prompt_event_mapping_MCQ_zs", "prompt_event_mapping_MCQ_cot"]

    if prompt_name not in valid_prompts:
        raise ValueError(f"Unknown prompt: {prompt_name}")

    if f"_{args.dataset}_" not in prompt_name:
        raise ValueError(f"Prompt {prompt_name} does not match dataset {args.dataset}.")

    return getattr(prompts_llm_event_mapping, prompt_name)


def prepare_llm_mapping_prompts(main_data, args):
    unit = args.unit.strip().lower()

    event_data = None
    if unit == "event":
        event_data = load_event_data(args)

    prompt_template = get_llm_mapping_prompt(args)
    prompts = []
    target_counts = []

    for index in tqdm(range(len(main_data)), desc=f"Preparing {args.dataset} prompts"):
        base_story, target_stories = get_llm_mapping_stories(main_data, index, args)

        base_events = None
        if unit == "event":
            base_events = event_data[index]["base"]

        base_story = prepare_story_by_unit(base_story, unit, base_events)

        prepared_targets = []
        for target_index, target_story in enumerate(target_stories):
            target_events = None

            if unit == "event":
                target_key = f"target{target_index + 1}"
                target_events = event_data[index][target_key]

            prepared_target = prepare_story_by_unit(target_story, unit, target_events)

            prepared_targets.append(prepared_target)

        prompt_values = {"base_story": base_story}

        for target_index, target_story in enumerate(prepared_targets):
            prompt_values[f"target_{target_index}"] = target_story

        prompt = prompt_template.format(**prompt_values)

        prompts.append(prompt)
        target_counts.append(len(prepared_targets))

    return prompts, target_counts


def get_valid_answer(value, target_count):
    if isinstance(value, bool):
        return None

    if isinstance(value, int):
        answer = value

    elif isinstance(value, float) and value.is_integer():
        answer = int(value)

    elif isinstance(value, str):
        value = value.strip()

        if re.fullmatch(r"\d+", value):
            answer = int(value)

        else:
            target_match = re.fullmatch(r"(?:target|choice|option)\s*(\d+)", value, re.IGNORECASE)

            if target_match is None:
                return None

            answer = int(target_match.group(1))

    else:
        return None

    if 0 <= answer < target_count:
        return answer

    return None


def find_answer_in_json(data, target_count):
    answer_keys = ["answer", "final_answer", "choice", "prediction", "target"]

    if isinstance(data, dict):
        for key, value in data.items():
            if str(key).lower() in answer_keys:
                answer = get_valid_answer(value, target_count)

                if answer is not None:
                    return answer

        for value in data.values():
            if isinstance(value, (dict, list)):
                answer = find_answer_in_json(value, target_count)

                if answer is not None:
                    return answer

    elif isinstance(data, list):
        for value in data:
            answer = find_answer_in_json(value, target_count)

            if answer is not None:
                return answer

    return None


def parse_json_answer(text, target_count):
    text = text.strip()

    if not text:
        return None

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        try:
            data = ast.literal_eval(text)
        except (ValueError, SyntaxError):
            return None

    answer = find_answer_in_json(data, target_count)

    if answer is not None:
        return answer

    return get_valid_answer(data, target_count)


def extract_llm_answer(raw_answer, target_count):
    if raw_answer is None:
        return INVALID_ANSWER_INDEX

    text = str(raw_answer).strip()

    if not text:
        return INVALID_ANSWER_INDEX

    json_blocks = re.findall(r"<JSON>\s*(.*?)\s*</JSON>", text, re.IGNORECASE | re.DOTALL)

    for json_block in reversed(json_blocks):
        answer = parse_json_answer(json_block, target_count)

        if answer is not None:
            return answer

    code_blocks = re.findall(r"```(?:json)?\s*(.*?)\s*```", text, re.IGNORECASE | re.DOTALL)

    for code_block in reversed(code_blocks):
        answer = parse_json_answer(code_block, target_count)

        if answer is not None:
            return answer

    answer = parse_json_answer(text, target_count)

    if answer is not None:
        return answer

    answer_patterns = [
        r'["\'](?:answer|final_answer|choice|prediction|target)["\']\s*[:=]\s*["\']?(?:target\s*)?(\d+)',
        r"\b(?:final\s+answer|answer|choice|prediction)\s*(?:is|:|=)\s*(?:target\s*)?(\d+)\b",
        r"\btherefore\s*,?\s*target\s+(\d+)\b",
    ]

    for pattern in answer_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)

        for match in reversed(matches):
            answer = get_valid_answer(match, target_count)

            if answer is not None:
                return answer

    visible_answer = text.rsplit("</think>", 1)[-1].strip()
    answer = get_valid_answer(visible_answer, target_count)

    if answer is not None:
        return answer

    lines = [line.strip() for line in visible_answer.splitlines() if line.strip()]

    if lines:
        answer = get_valid_answer(lines[-1], target_count)

        if answer is not None:
            return answer

    return INVALID_ANSWER_INDEX


def get_llm_result_config(args):
    result_config = args.config.copy()
    prompt_name = result_config.get("prompt", "")
    prompt_name = prompt_name.replace("_ARN_", "_{dataset}_")
    prompt_name = prompt_name.replace("_MCQ_", "_{dataset}_")
    result_config["prompt"] = prompt_name

    return json.dumps(result_config, sort_keys=True)


def save_llm_mapping_result(args, accuracy, category_dict):
    if os.path.exists(RESULTS_PATH):
        results = pd.read_csv(RESULTS_PATH)

        for column in LLM_RESULTS_COLUMNS:
            if column not in results.columns:
                results[column] = None

        results = results[LLM_RESULTS_COLUMNS]

    else:
        results = pd.DataFrame(columns=LLM_RESULTS_COLUMNS)

    result_config = get_llm_result_config(args)

    if len(results) == 0:
        matching_rows = []

    else:
        matching_rows = results[
            (results["model"].astype(str) == str(args.model))
            & (results["unit"].astype(str) == str(args.unit))
            & (results["config"].astype(str) == result_config)
        ].index.tolist()

    if len(matching_rows) > 1:
        raise ValueError("More than one result row has the same model, unit, and config.")

    if matching_rows:
        row_index = matching_rows[0]
        result_id = int(results.loc[row_index, "id"])

    else:
        existing_ids = pd.to_numeric(results["id"], errors="coerce").dropna()
        result_id = 1 if len(existing_ids) == 0 else int(existing_ids.max()) + 1
        row_index = len(results)

        results.loc[row_index, "id"] = result_id
        results.loc[row_index, "model"] = args.model
        results.loc[row_index, "unit"] = args.unit
        results.loc[row_index, "config"] = result_config

    if args.dataset == "MCQ":
        results.loc[row_index, "MCQ accuracy"] = accuracy

    elif args.dataset == "ARN":
        results.loc[row_index, "ARN accuracy"] = accuracy

        for category in ARN_CATEGORIES:
            results.loc[row_index, f"arn {category}"] = category_dict[category]

    results.to_csv(RESULTS_PATH, index=False)
    print(f"LLM mapping result saved under ID {result_id}")


def get_correct_answer(main_data, index, args):
    if args.dataset == "ARN":
        row = main_data.iloc[index]
        correct_answer = int(row["correct_answer"]) - 1
        category = f'{row["distractor_similarity"]}-{row["analogy_level"]}'

    elif args.dataset == "MCQ":
        correct_answer = int(main_data[index]["answer"])
        category = ""

    else:
        raise ValueError(f"Unsupported dataset: {args.dataset}")

    return correct_answer, category

def LLM_mapping_loop_func(main_data, args):
    prompts, target_counts = prepare_llm_mapping_prompts(main_data, args)
    batch_size = args.config.get("batch_size", 64)
    raw_answers = []

    for chunk in tqdm(list(batched(prompts, batch_size)), desc="Batches"):
        raw_texts = query_models_batch(chunk, args.model)
        raw_answers.extend(raw_texts)

    if len(raw_answers) != len(prompts):
        raise ValueError(f"The model returned {len(raw_answers)} answers for {len(prompts)} prompts.")

    y_true = []
    y_pred = []
    category_dict_ref = {"low-near": 294, "low-far": 294, "high-near": 253, "high-far": 254}
    category_dict = {"low-near": 0, "low-far": 0, "high-near": 0, "high-far": 0}
    invalid_answers = 0

    for index in tqdm(range(len(main_data)), desc="LLM mapping process"):
        correct_answer, category = get_correct_answer(main_data, index, args)
        y_true.append(correct_answer)

        predicted_answer = extract_llm_answer(raw_answers[index], target_counts[index])
        y_pred.append(predicted_answer)

        if predicted_answer == INVALID_ANSWER_INDEX:
            invalid_answers += 1

        if args.dataset == "ARN" and y_true[-1] == y_pred[-1]:
            category_dict[category] += 1

    print(f"Invalid LLM answers assigned index {INVALID_ANSWER_INDEX}: {invalid_answers}")

    result = round(metrics.accuracy_score(y_true, y_pred), 2)

    if args.dataset == "ARN":
        for key in category_dict:
            category_dict[key] = round(category_dict[key] / category_dict_ref[key], 2)

        save_llm_mapping_result(args, result, category_dict)
        print("result: ", result, category_dict)
        print("---------------------------------------------------------------")

    elif args.dataset == "MCQ":
        save_llm_mapping_result(args, result, "-")
        print("result: ", result)
        print("---------------------------------------------------------------")


def run_llm_mapping(args):
    data_short = args.dataset.lower()

    if data_short == "arn":
        main_data = pd.read_csv("Data/Datasets/Analogical Reasoning on Narratives (ARN) dataset.xlsx - Sheet1.csv")
    elif data_short == "mcq":
        with open("Data/Datasets/storyanalogy_multiple_choice.json") as f:
            main_data = json.load(f)
    else:
        raise ValueError(f"Unsupported dataset: {args.dataset}")


    LLM_mapping_loop_func(main_data, args)