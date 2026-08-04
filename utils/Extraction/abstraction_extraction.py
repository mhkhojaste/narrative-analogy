import openai
import re
from collections import defaultdict
from tqdm import tqdm
from sklearn import metrics
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
import pandas as pd
from typing import Dict, Any, Tuple

from utils.helper_utils import *
from Data.Prompts.prompts_abstraction import *


PATH_UNITS = "Data_new/Units/"
PATH_ABSTRACTION = "Data_new/Abstraction/"
os.makedirs(PATH_ABSTRACTION, exist_ok=True)

### helper functions

def group_phrases_by_role(data):
    grouped = defaultdict(list)
    for text, role in data.items():
        grouped[role].append(text)

    def role_sort_key(role_code):
        m = re.search(r'\d+', role_code)
        return int(m.group()) if m else float('inf')

    sorted_roles = sorted(grouped.keys(), key=role_sort_key)

    result = []
    phrase_id = 1

    for role_code in sorted_roles:
        phrases_list = []
        for text in grouped[role_code]:
            phrases_list.append({
                "id": f"p{phrase_id}",
                "text": text
            })
            phrase_id += 1

        result.append({
            "role_code": role_code,
            "phrases": phrases_list
        })

    lines = []
    lines.append("[")
    for i, block in enumerate(result):
        lines.append("  {")
        lines.append(f'    "role_code": "{block["role_code"]}",')
        lines.append(f'    "phrases": [')

        for j, ph in enumerate(block["phrases"]):
            id_ = ph["id"]
            text = ph["text"].replace('"', '\\"')  # escape quotes
            comma = "," if j < len(block["phrases"]) - 1 else ""
            lines.append(f'      {{ "id":"{id_}","text":"{text}" }}{comma}')

        lines.append("    ]")
        comma = "," if i < len(result) - 1 else ""
        lines.append(f"  }}{comma}")
    lines.append("]")

    return "\n".join(lines)


def convert_events_to_object_array(strings):
    return [{"id": f"p{i+1}", "text": text} for i, text in enumerate(strings)]
    
def convert_events_to_formatted_string(strings):
    items = [
        f'  {{ "id":"p{i+1}","text":"{text}" }}'
        for i, text in enumerate(strings)
    ]
    return "[\n" + ",\n".join(items) + "\n]"

def convert_events_to_formatted_string_with_abstractions(strings, strings_dict):
    items = [
        f'  {{ "id":"p{i+1}","phrase":"{text}",  "previous_frame": {strings_dict.get(text, "").upper().replace(" ", "_") if strings_dict.get(text, "") else ""}}}'
        for i, text in enumerate(strings)
    ]
    return "[\n" + ",\n".join(items) + "\n]"

def parse_results_by_lines(s: str, target_number: int) -> dict:
    target_keys_map = {
        1: {"id", "original_phrase", "position", "rationale"},
        2: {"id", "original_phrase", "frame_name", "rationale"},
        3: {"id", "original_phrase", "frame_name", "previous_frame", "rationale"},
        4: {"id", "original_phrase", "event_evalaution", "rationale"},
        5: {"id", "original_event", "role", "rationale"},
        6: {"role_code", "kernel_name", "rationale"},
    }

    if target_number not in target_keys_map:
        raise ValueError(
            f"Invalid target number: {target_number}. "
            f"Choose one of {list(target_keys_map)}."
        )

    target_keys = target_keys_map[target_number]
    results = []
    in_results = in_object = False
    cur = {}

    for raw in s.splitlines():
        line = raw.strip()

        if not line:
            continue

        if not in_results:
            in_results = "results" in line
            continue

        if line.startswith("]"):
            break

        if line.startswith("{"):
            in_object, cur = True, {}
            continue

        if line.startswith("}"):
            results.append({
                key: cur.get(key, "")
                for key in target_keys
            })
            in_object, cur = False, {}
            continue

        if not in_object:
            continue

        work = line.removesuffix(",").replace('"', "").replace("'", "")

        if ":" not in work:
            continue

        left, right = map(str.strip, work.split(":", 1))

        for key in target_keys:
            if left == key or key in left:
                cur[key] = right
                break

    return {"results": results}

def map_text_to_abstraction(array, json_str, target_number):
    abstraction_map = {
        1: ("position", lambda value: value.strip()),
        2: ("frame_name", lambda value: value.strip().replace("_", " ").lower()),
        3: ("frame_name", lambda value: value.strip().replace("_", " ").lower()),
        4: ("event_evalaution", lambda value: value.strip()),
        5: ("role", lambda value: value.strip()),
    }

    if target_number not in abstraction_map:
        raise ValueError(
            f"Unsupported target number: {target_number}. "
            f"Expected one of {list(abstraction_map)}."
        )

    start = json_str.find("<JSON>")
    end = json_str.find("</JSON>", start)

    json_str_clean = (
        json_str[start + len("<JSON>") : end].strip()
        if start != -1 and end != -1
        else ""
    )

    try:
        data = json.loads(json_str_clean)
    except json.JSONDecodeError:
        print("Invalid JSON; using line parser:\n", json_str_clean)
        data = parse_results_by_lines(json_str_clean, target_number)

    id_to_text = {
        item["id"].strip(): item["text"].strip()
        for item in array
    }

    abstraction_key, transform = abstraction_map[target_number]
    text_to_abstraction = {}

    for result in data.get("results", []):
        result_id = str(result.get("id", "")).strip()
        value = result.get(abstraction_key, "")

        if result_id in id_to_text:
            text_to_abstraction[id_to_text[result_id]] = (
                transform(value) if isinstance(value, str) else ""
            )

    return text_to_abstraction


def map_text_to_stages(json_str):
    start = json_str.find("<JSON>")
    end = json_str.find("</JSON>", start)

    json_str_clean = (
        json_str[start + len("<JSON>"):end].strip()
        if start != -1 and end != -1
        else ""
    )

    try:
        data = json.loads(json_str_clean)
    except json.JSONDecodeError:
        print("Invalid JSON; using line parser:\n", json_str_clean)
        data = parse_results_by_lines(json_str_clean, 6)

    return {
        entry["kernel_name"]: entry["role_code"]
        for entry in data.get("results", [])
        if "kernel_name" in entry and "role_code" in entry
    }


def batched(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i+n]


def sort_list_by_dict(lst, dct):
    def sort_key(x):
        val = dct.get(x)
        try:
            return int(val)
        except (TypeError, ValueError):
            return float('inf')  # Put invalid or missing values at the end
    return sorted(lst, key=sort_key)




############# Prompts

def load_previous_abstractions(dataset_name, args):
    abstraction_type_map = {"conceptual_abstraction_level1": "conceptual0", "evaluative_abstraction": "timeline", "arc_abstraction": "timeline", "stage_abstraction": "arc"}
    abstraction_type = abstraction_type_map.get(args.task)

    if abstraction_type is None:
        return None

    model_short = model_short_dict.get(args.model)
    path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_{abstraction_type}_{dataset_name.lower()}.pkl"
    with open(path, "rb") as f:
        return pickle.load(f)

def get_dataset_fields(dataset_dict, dataset_name):
    if dataset_name == "ARN":
        iterator = tqdm(dataset_dict.iterrows(), total=len(dataset_dict))
        for idx, row in iterator:
            yield idx, {"base": row["query_narrative"].strip(), "target1": row["first_choice"].strip(), "target2": row["second_choice"].strip()}

    elif dataset_name == "MCQ":
        for idx in tqdm(range(len(dataset_dict))):
            row = dataset_dict[idx]

            yield idx, {
                "base": row["source"].strip(),
                **{
                    f"target{i + 1}": choice.strip()
                    for i, choice in enumerate(row["choices"][:4])
                },
            }

    else:
        raise ValueError(f"Unsupported dataset: {dataset_name}")


def build_prompt(fmt, task, story, events, previous_abstractions=None,):
    if task == "conceptual_abstraction_level1":
        phrases = convert_events_to_formatted_string_with_abstractions(events, previous_abstractions)
        return fmt.format(story=story, phrases=phrases)

    if task == "stage_abstraction":
        return fmt.format(story=story, groups=group_phrases_by_role(previous_abstractions))

    if task in {"evaluative_abstraction", "arc_abstraction"}:
        events = sort_list_by_dict(events, previous_abstractions)

    return fmt.format(story=story, phrases=convert_events_to_formatted_string(events))


def build_all_prompts_abstraction(dataset_dict, dataset_event, dataset_name, args):
    prompt_map = {
        "timeline_extraction": prompt_timeline_extraction,
        "conceptual_abstraction_level0": prompt_conceptual_abstraction_level0,
        "conceptual_abstraction_level1": prompt_conceptual_abstraction_level1,
        "evaluative_abstraction": prompt_evaluative_abstraction,
        "arc_abstraction": prompt_arc_abstraction,
        "stage_abstraction": prompt_stage_abstraction
    }

    try:
        fmt = prompt_map[args.task]
    except KeyError:
        raise ValueError(f"Unsupported task: {args.task}")

    event_with_abstractions = load_previous_abstractions(dataset_name, args)

    prompts, index_map = [], []

    print(f"Creating prompts for {dataset_name} dataset")

    for idx, fields in get_dataset_fields(dataset_dict, dataset_name):
        for field_name, story in fields.items():
            events = dataset_event[idx][field_name]
            previous = (event_with_abstractions[idx][field_name] if event_with_abstractions is not None else None)

            prompts.append(
                build_prompt(
                    fmt=fmt,
                    task=args.task,
                    story=story,
                    events=events,
                    previous_abstractions=previous,
                )
            )
            index_map.append((idx, field_name))

    return prompts, index_map


############# Run the dataset

def abstraction_extraction_pipeline_all(dataset_data, dataset_event, dataset_name, args, batch_size=16):
    target_numbers = {"timeline_extraction": 1, "conceptual_abstraction_level0": 2, "conceptual_abstraction_level1": 3, "evaluative_abstraction": 4,
        "arc_abstraction": 5, "stage_abstraction": 6}

    if args.task not in target_numbers:
        raise ValueError(f"Unsupported task: {args.task}")

    prompts, index_map = build_all_prompts_abstraction(dataset_data, dataset_event, dataset_name, args)

    model_short = model_short_dict.get(args.model)
    dataset_suffix = dataset_name.lower()
    target_number = target_numbers[args.task]

    event_with_abstractions = None

    if args.task in {"evaluative_abstraction", "arc_abstraction"}:
        timeline_path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_timeline_{dataset_suffix}.pkl"
        with open(timeline_path, "rb") as f:
            event_with_abstractions = pickle.load(f)

    abstraction_dict = {}
    global_offset = 0

    print(f"Extracting abstractions for {dataset_name} dataset")

    for chunk in tqdm(list(batched(prompts, batch_size)), desc="Batches"):
        raw_texts = query_models_batch(chunk, args.model)

        assert len(raw_texts) == len(chunk), f"Model batch output size mismatch for batch {global_offset}!"

        slice_map = index_map[global_offset : global_offset + len(chunk)]

        for raw, (row_idx, field_name) in zip(raw_texts, slice_map):
            if args.task == "stage_abstraction":
                abstractions_out = map_text_to_stages(raw)
            else:
                events = dataset_event[row_idx][field_name]

                if args.task in {"evaluative_abstraction", "arc_abstraction"}:
                    events = sort_list_by_dict(events, event_with_abstractions[row_idx][field_name])

                abstractions_out = map_text_to_abstraction(convert_events_to_object_array(events), raw, target_number)

            abstraction_dict.setdefault(row_idx, {})[field_name] = abstractions_out
            

        global_offset += len(chunk)

    task_short = task_abstraction_short.get(args.task)

    if task_short is None:
        raise ValueError(
            f"No short name configured for task: {args.task}"
        )

    path_save = f"{PATH_ABSTRACTION}{model_short}{args.unit}_{task_short}_{dataset_suffix}.pkl"

    with open(path_save, "wb") as f:
        pickle.dump(abstraction_dict, f)

    print("saved as:", path_save)

        
def run_abstraction_extraction(args):
    print(f"Model: {args.model}, Task: {args.task}, Unit: {args.unit}, Dataset: {args.dataset}")

    if args.dataset == "ARN":
        dataset_data = pd.read_csv('Data/Datasets/Analogical Reasoning on Narratives (ARN) dataset.xlsx - Sheet1.csv')
    elif args.dataset == "MCQ":
        with open('Data/Datasets/storyanalogy_multiple_choice.json') as f:
            dataset_data = json.load(f)

    model_short = model_short_dict.get(args.model)
    dataset_suffix = args.dataset.lower()
    event_path = f"{PATH_UNITS}{model_short}{args.unit}_{dataset_suffix}.pkl"
    with open(event_path, "rb") as f:
        dataset_event = pickle.load(f)


    abstraction_extraction_pipeline_all(dataset_data, dataset_event, args.dataset, args)


