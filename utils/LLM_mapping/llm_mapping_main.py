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
import unicodedata
from textwrap import dedent

from utils.helper_utils import *
from Data.Prompts import prompts_llm_event_mapping
from Data.Prompts import prompts_llm_message_mapping

random.seed(309)

RESULTS_DIR = "results/"
os.makedirs(RESULTS_DIR, exist_ok=True)
RESULTS_PATH = RESULTS_DIR + "results_llm_mapping.csv"

RESULTS_PATH_POLLUTION = RESULTS_DIR + "results_data_pollution.csv"


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

        config = args.config if isinstance(args.config, dict) else {}
        base_percentage = int(config.get("base_percentage", 100))

        if base_percentage < 0 or base_percentage > 100:
            raise ValueError("base_percentage must be between 0 and 100.")

        if args.unit.lower() == "story":
            if base_percentage == 0:
                base_story = ""

            elif base_percentage < 100:
                base_words = base_story.split()
                number_of_words = max(1, int(len(base_words) * base_percentage / 100))
                base_story = " ".join(base_words[:number_of_words])

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
    valid_prompts2 = ["prompt_message_mapping_ARN_zs", "prompt_message_mapping_ARN_cot", "prompt_message_mapping_MCQ_zs", "prompt_message_mapping_MCQ_cot"]

    if prompt_name not in valid_prompts and prompt_name not in valid_prompts2:
        raise ValueError(f"Unknown prompt: {prompt_name}")

    if f"_{args.dataset}_" not in prompt_name:
        raise ValueError(f"Prompt {prompt_name} does not match dataset {args.dataset}.")

    if prompt_name in valid_prompts:
        return getattr(prompts_llm_event_mapping, prompt_name)
    elif prompt_name in valid_prompts2:
        return getattr(prompts_llm_message_mapping, prompt_name)


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
    result_config.pop("result_path", None)

    prompt_name = result_config.get("prompt", "")
    prompt_name = prompt_name.replace("_ARN_", "_{dataset}_")
    prompt_name = prompt_name.replace("_MCQ_", "_{dataset}_")
    result_config["prompt"] = prompt_name

    return json.dumps(result_config, sort_keys=True)


def save_llm_mapping_result(args, accuracy, category_dict):
    config = args.config if isinstance(args.config, dict) else {}
    configured_result_path = config.get("result_path", "empty_path")

    if configured_result_path == "empty_path":
        results_path = RESULTS_PATH
    else:
        results_path = os.path.join(RESULTS_DIR, configured_result_path)

    results_directory = os.path.dirname(results_path)

    if results_directory:
        os.makedirs(results_directory, exist_ok=True)

    if os.path.exists(results_path):
        results = pd.read_csv(results_path)

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

    results.to_csv(results_path, index=False)

    print(f"LLM mapping result saved under ID {result_id}")
    print(f"Results path: {results_path}")

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

## data pollution

def normalize_completion_text(text):
    text = unicodedata.normalize("NFKC", str(text))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def get_unique_arn_stories(main_data, args):
    unique_stories = []
    seen_stories = set()

    for index in tqdm(range(len(main_data)), desc="Collecting unique ARN stories"):
        base_story, target_stories = get_llm_mapping_stories(main_data, index, args)
        current_stories = [base_story] + target_stories

        for story in current_stories:
            if story is None:
                continue

            story = normalize_completion_text(story)

            if not story or story.lower() == "nan":
                continue

            if story not in seen_stories:
                seen_stories.add(story)
                unique_stories.append(story)

    return unique_stories


def split_story_by_context(story, context_percentage):
    words = story.split()

    if len(words) < 2:
        return None, None

    split_index = int(len(words) * context_percentage / 100)
    split_index = max(1, min(split_index, len(words) - 1))

    visible_context = " ".join(words[:split_index])
    missing_continuation = " ".join(words[split_index:])

    return visible_context, missing_continuation


def create_story_completion_prompt(visible_context, prompt_name):
    if prompt_name == "guided":
        return dedent(f"""\
        You are provided with the FIRST PIECE of an instance from the ARN (Analogical Reasoning on Narratives) dataset.

        Finish the SECOND PIECE of the instance as it EXACTLY appeared in the dataset. ONLY rely on the original form of the instance in the dataset to finish the SECOND PIECE.

        Output ONLY the missing SECOND PIECE. Do not repeat the FIRST PIECE. Do not provide any explanation, label, quotation marks, Markdown formatting, or additional text.

        FIRST PIECE:
        {visible_context}

        SECOND PIECE:""").strip()

    if prompt_name == "general":
        return dedent(f"""\
        You are provided with the FIRST PIECE of a story.

        Finish the SECOND PIECE based on the FIRST PIECE so that they form one complete story.

        Output ONLY the missing SECOND PIECE. Do not repeat the FIRST PIECE. Do not provide any explanation, label, quotation marks, Markdown formatting, or additional text.

        FIRST PIECE:
        {visible_context}

        SECOND PIECE:""").strip()

    raise ValueError(f"Unknown data-pollution prompt: {prompt_name}")


def clean_generated_completion(raw_answer, visible_context):
    if raw_answer is None:
        return ""

    answer = str(raw_answer).strip()

    if "</think>" in answer:
        answer = answer.rsplit("</think>", 1)[-1].strip()

    code_block = re.fullmatch(r"```(?:text)?\s*(.*?)\s*```", answer, re.IGNORECASE | re.DOTALL)

    if code_block:
        answer = code_block.group(1).strip()

    second_piece_parts = re.split(r"\bSECOND\s+PIECE\s*:\s*", answer, flags=re.IGNORECASE)

    if len(second_piece_parts) > 1:
        answer = second_piece_parts[-1].strip()

    answer = re.sub(r"^(?:missing\s+continuation|story\s+continuation|continuation|completion|answer|second\s+piece)\s*:\s*", "", answer, flags=re.IGNORECASE)
    normalized_answer = normalize_completion_text(answer)
    normalized_context = normalize_completion_text(visible_context)

    if normalized_answer.startswith(normalized_context):
        normalized_answer = normalized_answer[len(normalized_context):].strip()

    return normalized_answer


def levenshtein_distance(reference, prediction):
    if len(reference) < len(prediction):
        reference, prediction = prediction, reference

    previous_row = list(range(len(prediction) + 1))

    for reference_index, reference_item in enumerate(reference, start=1):
        current_row = [reference_index]

        for prediction_index, prediction_item in enumerate(prediction, start=1):
            insertion_cost = current_row[prediction_index - 1] + 1
            deletion_cost = previous_row[prediction_index] + 1
            substitution_cost = previous_row[prediction_index - 1] + (reference_item != prediction_item)
            current_row.append(min(insertion_cost, deletion_cost, substitution_cost))

        previous_row = current_row

    return previous_row[-1]


def sequence_accuracy(reference, prediction):
    if not reference and not prediction:
        return 1.0

    if not reference or not prediction:
        return 0.0

    distance = levenshtein_distance(reference, prediction)
    return max(0.0, 1.0 - distance / max(len(reference), len(prediction)))


def tokenize_completion(text):
    return re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)


def calculate_completion_metrics(references, predictions):
    if len(references) != len(predictions):
        raise ValueError(f"Found {len(references)} references but {len(predictions)} predictions.")

    if not references:
        raise ValueError("No references were available for metric calculation.")

    exact_match_scores = []
    token_accuracy_scores = []
    character_accuracy_scores = []

    for reference, prediction in zip(references, predictions):
        reference = normalize_completion_text(reference)
        prediction = normalize_completion_text(prediction)

        exact_match_scores.append(int(reference == prediction))
        token_accuracy_scores.append(sequence_accuracy(tokenize_completion(reference), tokenize_completion(prediction)))
        character_accuracy_scores.append(sequence_accuracy(list(reference), list(prediction)))

    exact_match = sum(exact_match_scores) / len(exact_match_scores)
    token_accuracy = sum(token_accuracy_scores) / len(token_accuracy_scores)
    character_accuracy = sum(character_accuracy_scores) / len(character_accuracy_scores)

    return round(exact_match, 4), round(token_accuracy, 4), round(character_accuracy, 4)


def save_data_pollution_result(model_name, prompt_name, experiment, exact_match, token_accuracy, character_accuracy, args):
    columns = ["model_name", "prompt", "experiment", "exact_match", "token_accuracy", "character_accuracy"]
    new_row = {"model_name": model_name, "prompt": prompt_name, "experiment": experiment, "exact_match": exact_match, "token_accuracy": token_accuracy, "character_accuracy": character_accuracy}

    config = args.config if isinstance(args.config, dict) else {}
    configured_result_path = config.get("result_path", "empty_path")

    if configured_result_path == "empty_path":
        results_path = RESULTS_PATH_POLLUTION
    else:
        results_path = os.path.join(RESULTS_DIR, configured_result_path)

    results_directory = os.path.dirname(results_path)

    if results_directory:
        os.makedirs(results_directory, exist_ok=True)

    if os.path.exists(results_path):
        results = pd.read_csv(results_path)
    else:
        results = pd.DataFrame(columns=columns)

    if "prompt" not in results.columns:
        results["prompt"] = "legacy"

    for column in columns:
        if column not in results.columns:
            results[column] = None

    results["experiment"] = pd.to_numeric(results["experiment"], errors="coerce")
    existing_row = (results["model_name"] == model_name) & (results["prompt"] == prompt_name) & (results["experiment"] == experiment)

    if existing_row.any():
        for column, value in new_row.items():
            results.loc[existing_row, column] = value
    else:
        results = pd.concat([results, pd.DataFrame([new_row])], ignore_index=True)

    results = results[columns]
    results = results.sort_values(["model_name", "prompt", "experiment"], kind="stable")
    results.to_csv(results_path, index=False)


def data_pollution_task(main_data, args):
    if args.dataset.upper() != "ARN":
        raise ValueError("The context-completion data-pollution experiment only supports ARN.")

    if args.unit.lower() != "context":
        raise ValueError(f"Unsupported data-pollution unit: {args.unit}")

    config = args.config if isinstance(args.config, dict) else {}
    prompt_name = str(config.get("prompt", "guided")).strip().lower()
    valid_prompts = ["guided", "general"]
    batch_size = int(config.get("batch_size", 16))

    if prompt_name not in valid_prompts:
        raise ValueError(f"Unknown prompt: {prompt_name}. Valid prompts are: {valid_prompts}")

    if batch_size < 1:
        raise ValueError("batch_size must be greater than zero.")

    context_percentages = [10, 20, 40, 80]
    unique_stories = get_unique_arn_stories(main_data, args)

    if not unique_stories:
        raise ValueError("No ARN stories were found.")

    print(f"Model: {args.model}")
    print(f"Prompt: {prompt_name}")
    print(f"Number of unique ARN stories: {len(unique_stories)}")
    print("----------------------")

    for context_percentage in context_percentages:
        prompts = []
        references = []
        visible_contexts = []

        for story in unique_stories:
            visible_context, missing_continuation = split_story_by_context(story, context_percentage)

            if visible_context is None:
                continue

            prompts.append(create_story_completion_prompt(visible_context, prompt_name))
            references.append(missing_continuation)
            visible_contexts.append(visible_context)

        raw_answers = []

        for start_index in tqdm(range(0, len(prompts), batch_size), desc=f"{prompt_name} E@{context_percentage}"):
            prompt_batch = prompts[start_index:start_index + batch_size]
            batch_answers = query_models_batch(prompt_batch, args.model)
            raw_answers.extend(batch_answers)

        if len(raw_answers) != len(prompts):
            raise ValueError(f"The model returned {len(raw_answers)} answers for {len(prompts)} prompts at E@{context_percentage}.")

        predictions = [clean_generated_completion(answer, context) for answer, context in zip(raw_answers, visible_contexts)]
        empty_predictions = sum(not prediction for prediction in predictions)
        exact_match, token_accuracy, character_accuracy = calculate_completion_metrics(references, predictions)

        save_data_pollution_result(args.model, prompt_name, context_percentage, exact_match, token_accuracy, character_accuracy, args)

        print(f"Prompt: {prompt_name}")
        print(f"E@{context_percentage}")
        print(f"Exact match: {exact_match}")
        print(f"Token accuracy: {token_accuracy}")
        print(f"Character accuracy: {character_accuracy}")
        print(f"Empty predictions: {empty_predictions}")
        print("----------------------")

def run_llm_mapping(args):
    data_short = args.dataset.lower()

    if data_short == "arn":
        main_data = pd.read_csv("Data/Datasets/Analogical Reasoning on Narratives (ARN) dataset.xlsx - Sheet1.csv")
    elif data_short == "mcq":
        with open("Data/Datasets/storyanalogy_multiple_choice.json") as f:
            main_data = json.load(f)
    else:
        raise ValueError(f"Unsupported dataset: {args.dataset}")

    if args.task == "llm_mapping":
        LLM_mapping_loop_func(main_data, args)
    elif args.task == "data_pollution":
        data_pollution_task(main_data, args)