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
from Data.Prompts.prompts_stage import *
from Data.Prompts.prompt_superunit import *


PATH_UNITS = "Data_new/Units/"
PATH_ABSTRACTION = "Data_new/Abstraction/"
os.makedirs(PATH_ABSTRACTION, exist_ok=True)


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

def convert_events_to_formatted_string2(strings, strings_dict):
    items = [
        f'  {{ "id":"p{i+1}","phrase":"{text}",  "previous_frame": {strings_dict.get(text, "").upper().replace(" ", "_") if strings_dict.get(text, "") else ""}}}'
        for i, text in enumerate(strings)
    ]
    return "[\n" + ",\n".join(items) + "\n]"

def parse_results_by_lines0(s: str) -> dict:
    TARGET_KEYS = {
        "id", "role_code",
        "kernel_name", "rationale"
    }

    # TARGET_KEYS = {
    #     "role_code", "kernel_name",
    #     "rationale"
    # }

    results = []
    in_results = False
    in_object = False
    cur = {}

    lines = s.splitlines()
    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        # enter the results array
        if not in_results:
            if 'results' in line:
                in_results = True
            continue

        # array end?
        if line.startswith(']'):
            break

        # object start?
        if line.startswith('{'):
            in_object = True
            cur = {}
            continue

        # object end?
        if line.startswith('}'):
            # fill missing keys with empty strings
            for k in TARGET_KEYS:
                if k not in cur:
                    cur[k] = ""
            results.append(cur)
            in_object = False
            cur = {}
            continue

        # between objects (commas, etc.)
        if not in_object:
            continue

        # --- key:value line handling (your rules) ---
        # drop trailing comma and all quotes
        work = line
        if work.endswith(','):
            work = work[:-1]
        work = work.replace('"', '').replace("'", "")

        # split by first colon
        if ':' not in work:
            # something is wrong with this line; skip
            continue
        left, right = work.split(':', 1)

        # clean ends
        left = left.strip()
        right = right.strip()

        # match target keys (exact OR containment, per your suggestion)
        for key in TARGET_KEYS:
            if left == key or (key in left):
                cur[key] = right
                break

    return {"results": results}

    
def map_text_to_abstraction(array, json_str):
    start_j = json_str.find("<JSON>")
    end_j = json_str.find("</JSON>")

    if start_j != -1 and end_j != -1:
        end_j += len("</JSON>")      
        json_str2 = json_str[start_j:end_j]
    else:
        json_str2 = ""

    json_str = json_str2
    json_str_clean = json_str.replace("<JSON>", "").replace("</JSON>", "").strip()
    
    try: 
        data = json.loads(json_str_clean)
    except:
        print("json_str_clean: \n")
        print(json_str_clean)
        data = parse_results_by_lines0(json_str_clean)
        print("new data: ")
        print(data)
    
    id_to_text = {item['id'].strip(): item['text'].strip() for item in array}
    
    text_to_abstraction = {}
    for result in data["results"]:
        _id = result["id"].strip()

        if "kernel_name" in result:
            abstraction = result["kernel_name"].strip()
        elif "frame_name" in result:
            try:
                abstraction = result["frame_name"].strip().replace("_", " ").lower()
            except:
                abstraction = ""
        elif "role_name" in result:
            try:
                abstraction = result["role_name"].strip().replace("_", " ").lower()
            except:
                abstraction = ""
        elif "position" in result:
            try:
                abstraction = result["position"].strip()
            except:
                abstraction = ""
        elif "event_type" in result:
            try:
                abstraction = result["event_type"].strip()
            except:
                abstraction = ""

        elif "event_evalaution" in result:
            try:
                abstraction = result["event_evalaution"].strip()
            except:
                abstraction = ""

        elif "role" in result:
            try:
                abstraction = result["role"].strip()
            except:
                abstraction = ""
        
        


        if _id in id_to_text:
            text_to_abstraction[id_to_text[_id]] = abstraction
    
    return text_to_abstraction


def map_text_to_stages(json_str):
    start_j = json_str.find("<JSON>")
    end_j = json_str.find("</JSON>")

    if start_j != -1 and end_j != -1:
        end_j += len("</JSON>")      
        json_str2 = json_str[start_j:end_j]
    else:
        json_str2 = ""

    json_str = json_str2
    json_str_clean = json_str.replace("<JSON>", "").replace("</JSON>", "").strip()
    
    try: 
        data = json.loads(json_str_clean)
    except:
        print("json_str_clean: \n")
        print(json_str_clean)
        data = parse_results_by_lines0(json_str_clean)
        print("new data: ")
        print(data)
    
    text_to_abstraction = {}
    for entry in data.get("results", []):
        if "kernel_name" in entry and "role_code" in entry:
            text_to_abstraction[entry["kernel_name"]] = entry["role_code"]

    return text_to_abstraction

def parse_results_by_lines(s: str) -> dict:
    TARGET_KEYS = {
        "id", "original_phrase",
        "root_l1", "detail_l1", "frame_l1",
        "root_l2", "detail_l2", "frame_l2",
        "root_l3", "frame_l3",
    }

    results = []
    in_results = False
    in_object = False
    cur = {}

    lines = s.splitlines()
    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        # enter the results array
        if not in_results:
            if 'results' in line:
                in_results = True
            continue

        # array end?
        if line.startswith(']'):
            break

        # object start?
        if line.startswith('{'):
            in_object = True
            cur = {}
            continue

        # object end?
        if line.startswith('}'):
            # fill missing keys with empty strings
            for k in TARGET_KEYS:
                if k not in cur:
                    cur[k] = ""
            results.append(cur)
            in_object = False
            cur = {}
            continue

        # between objects (commas, etc.)
        if not in_object:
            continue

        # --- key:value line handling (your rules) ---
        # drop trailing comma and all quotes
        work = line
        if work.endswith(','):
            work = work[:-1]
        work = work.replace('"', '').replace("'", "")

        # split by first colon
        if ':' not in work:
            # something is wrong with this line; skip
            continue
        left, right = work.split(':', 1)

        # clean ends
        left = left.strip()
        right = right.strip()

        # match target keys (exact OR containment, per your suggestion)
        for key in TARGET_KEYS:
            if left == key or (key in left):
                cur[key] = right
                break

    return {"results": results}



def map_text_to_abstraction9(array, json_str):
    json_str_clean = json_str.replace("<JSON>", "").replace("</JSON>", "").strip()

    try: 
        data = json.loads(json_str_clean)
    except:
        print("json_str_clean: \n")
        print(json_str_clean)
        data = parse_results_by_lines(json_str_clean)
        print("new data: ")
        print(data)


    
    id_to_text = {item['id'].strip(): item['text'].strip() for item in array}
    
    text_to_abstraction = {}
    for result in data["results"]:
        _id = result["id"].strip()

        if "kernel_name" in result:
            abstraction = result["kernel_name"].strip()
        elif "frame_l1" in result:
            try:
                abstraction = result["frame_l1"].strip().replace("_", " ").lower()
            except:
                abstraction = ""

        else:
            abstraction = ""
        


        if _id in id_to_text:
            text_to_abstraction[id_to_text[_id]] = abstraction
    
    return text_to_abstraction


def map_text_to_abstraction10(array, json_str):
    json_str_clean = json_str.replace("<JSON>", "").replace("</JSON>", "").strip()
    
    try: 
        data = json.loads(json_str_clean)
    except:
        data = parse_results_by_lines(json_str_clean)
    
    id_to_text = {item['id'].strip(): item['text'].strip() for item in array}
    
    text_to_abstraction = {}
    for result in data["results"]:
        _id = result["id"].strip()

        if "kernel_name" in result:
            abstraction = result["kernel_name"].strip()
        elif "frame_l2" in result:
            try:
                abstraction = result["frame_l2"].strip().replace("_", " ").lower()
            except:
                abstraction = ""

        else:
            abstraction = ""
        


        if _id in id_to_text:
            text_to_abstraction[id_to_text[_id]] = abstraction
    
    return text_to_abstraction

def map_text_to_abstraction11(array, json_str):
    json_str_clean = json_str.replace("<JSON>", "").replace("</JSON>", "").strip()
    
    try: 
        data = json.loads(json_str_clean)
    except:
        data = parse_results_by_lines(json_str_clean)
    
    id_to_text = {item['id'].strip(): item['text'].strip() for item in array}
    
    text_to_abstraction = {}
    for result in data["results"]:
        _id = result["id"].strip()

        if "kernel_name" in result:
            abstraction = result["kernel_name"].strip()
        elif "frame_l3" in result:
            try:
                abstraction = result["frame_l3"].strip().replace("_", " ").lower()
            except:
                abstraction = ""
        else:
            abstraction = ""
        


        if _id in id_to_text:
            text_to_abstraction[id_to_text[_id]] = abstraction
    
    return text_to_abstraction


######### Full datasets and with batching

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


def build_all_prompts_abstraction(dataset_dict, dataset_event, dataset_name, args):
    if args.task == "abstraction_extraction1":
        fmt = prompt_abstraction_extraction1
    elif args.task == "abstraction_extraction2":
        fmt = prompt_abstraction_extraction2
    elif args.task == "abstraction_extraction3":
        fmt = prompt_abstraction_extraction3
    elif args.task == "abstraction_extraction4":
        fmt = prompt_abstraction_extraction4
    elif args.task == "abstraction_extraction5":
        fmt = prompt_abstraction_extraction5
    elif args.task == "abstraction_extraction6":
        fmt = prompt_abstraction_extraction6

        model_short = model_short_dict.get(args.model)

        if dataset_name == "ARN":
            event_with_abstractions_path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction5_arn.pkl"
        elif dataset_name == "MCQ":
            event_with_abstractions_path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction5_mcq.pkl"

        with open(event_with_abstractions_path, 'rb') as f:
            event_with_abstractions = pickle.load(f) 

    elif args.task == "abstraction_extraction7":
        fmt = prompt_abstraction_extraction7

        model_short = model_short_dict.get(args.model)

        if dataset_name == "ARN":
            event_with_abstractions_path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction6_arn.pkl"
        elif dataset_name == "MCQ":
            event_with_abstractions_path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction6_mcq.pkl"

        with open(event_with_abstractions_path, 'rb') as f:
            event_with_abstractions = pickle.load(f) 

    elif args.task == "abstraction_extraction8":
        fmt = prompt_abstraction_extraction8

        model_short = model_short_dict.get(args.model)

        if dataset_name == "ARN":
            event_with_abstractions_path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction6_arn.pkl"
        elif dataset_name == "MCQ":
            event_with_abstractions_path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction6_mcq.pkl"

        with open(event_with_abstractions_path, 'rb') as f:
            event_with_abstractions = pickle.load(f) 

    elif args.task == "abstraction_extraction9":
        fmt = prompt_abstraction_extraction9

    elif args.task == "abstraction_extraction13":
        fmt = prompt_abstraction_extraction13
    elif args.task == "abstraction_extraction14":
        fmt = prompt_abstraction_extraction14
    elif args.task == "abstraction_extraction20":
        fmt = prompt_abstraction_extraction20
    elif args.task == "abstraction_extraction21":
        fmt = prompt_abstraction_extraction21

        model_short = model_short_dict.get(args.model)

        if dataset_name == "ARN":
            event_with_abstractions_path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction20_arn.pkl"
        elif dataset_name == "MCQ":
            event_with_abstractions_path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction20_mcq.pkl"

        with open(event_with_abstractions_path, 'rb') as f:
            event_with_abstractions = pickle.load(f) 

    elif args.task == "abstraction_extraction22":
        fmt = prompt_abstraction_extraction22
    elif args.task == "abstraction_extraction23":
        fmt = prompt_abstraction_extraction23
    elif args.task == "abstraction_extraction24":
        fmt = prompt_abstraction_extraction24
    elif args.task == "abstraction_extraction25":
        fmt = prompt_abstraction_extraction25

        model_short = model_short_dict.get(args.model)

        if dataset_name == "ARN":
            event_with_abstractions_path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction24_arn.pkl"
        elif dataset_name == "MCQ":
            event_with_abstractions_path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction24_mcq.pkl"

        with open(event_with_abstractions_path, 'rb') as f:
            event_with_abstractions = pickle.load(f)

    elif args.task == "abstraction_extraction26":
        fmt = prompt_abstraction_extraction26

        model_short = model_short_dict.get(args.model)

        if dataset_name == "ARN":
            event_with_abstractions_path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction24_arn.pkl"
        elif dataset_name == "MCQ":
            event_with_abstractions_path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction24_mcq.pkl"

        with open(event_with_abstractions_path, 'rb') as f:
            event_with_abstractions = pickle.load(f)

    elif args.task == "stage_extraction3":
        fmt = prompt_stage_extraction3

        model_short = model_short_dict.get(args.model)

        if dataset_name == "ARN":
            event_with_abstractions_path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction24_arn.pkl"
        elif dataset_name == "MCQ":
            event_with_abstractions_path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction24_mcq.pkl"

        with open(event_with_abstractions_path, 'rb') as f:
            event_with_abstractions = pickle.load(f)

    elif args.task == "stage_extraction1":
        fmt = prompt_stage_extraction

    elif args.task == "superunit2":
        fmt = prompt_group_abstraction2

        model_short = model_short_dict.get(args.model)

        if dataset_name == "ARN":
            event_with_abstractions_path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_stage3_arn.pkl"
        elif dataset_name == "MCQ":
            event_with_abstractions_path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_stage3_mcq.pkl"

        with open(event_with_abstractions_path, 'rb') as f:
            event_with_abstractions = pickle.load(f)

    elif args.task == "superunit1":
        fmt = prompt_group_abstraction

        model_short = model_short_dict.get(args.model)

        if dataset_name == "ARN":
            event_with_abstractions_path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_stage1_arn.pkl"
        elif dataset_name == "MCQ":
            event_with_abstractions_path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_stage1_mcq.pkl"

        with open(event_with_abstractions_path, 'rb') as f:
            event_with_abstractions = pickle.load(f)

    elif args.task == "superunit3":
        fmt = prompt_group_abstraction3

        model_short = model_short_dict.get(args.model)

        if dataset_name == "ARN":
            event_with_abstractions_path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_stage3_arn.pkl"
        elif dataset_name == "MCQ":
            event_with_abstractions_path = f"{PATH_ABSTRACTION}{model_short}{args.unit}_stage3_mcq.pkl"

        with open(event_with_abstractions_path, 'rb') as f:
            event_with_abstractions = pickle.load(f)






    


    prompts, index_map = [], []

    if dataset_name == "ARN":
        print("Creating prompts for ARN dataset")
        for idx, row in tqdm(dataset_dict.iterrows(), total=len(dataset_dict)):
            field_list = []

            if args.task in ["abstraction_extraction1", "abstraction_extraction2", "abstraction_extraction3", "abstraction_extraction4", "abstraction_extraction5", "abstraction_extraction9", "abstraction_extraction13", "abstraction_extraction14", "abstraction_extraction20", "abstraction_extraction22", "abstraction_extraction23", "abstraction_extraction24", "stage_extraction1"]:
                field_list.append(("base", row["query_narrative"].strip(), dataset_event[idx]["base"]))
                field_list.append(("target1", row["first_choice"].strip(), dataset_event[idx]["target1"]))
                field_list.append(("target2", row["second_choice"].strip(), dataset_event[idx]["target2"]))
            elif args.task in ["abstraction_extraction6", "abstraction_extraction7", "abstraction_extraction8", "abstraction_extraction21"]:
                field_list.append(("base", row["query_narrative"].strip(), dataset_event[idx]["base"], event_with_abstractions[idx]["base"]))
                field_list.append(("target1", row["first_choice"].strip(), dataset_event[idx]["target1"], event_with_abstractions[idx]["target1"]))
                field_list.append(("target2", row["second_choice"].strip(), dataset_event[idx]["target2"], event_with_abstractions[idx]["target2"]))
            elif args.task in ["abstraction_extraction25", "abstraction_extraction26", "stage_extraction3"]:
                field_list.append(("base", row["query_narrative"].strip(), sort_list_by_dict(dataset_event[idx]["base"], event_with_abstractions[idx]["base"])))
                field_list.append(("target1", row["first_choice"].strip(), sort_list_by_dict(dataset_event[idx]["target1"], event_with_abstractions[idx]["target1"])))
                field_list.append(("target2", row["second_choice"].strip(), sort_list_by_dict(dataset_event[idx]["target2"], event_with_abstractions[idx]["target2"])))
            elif args.task in ["superunit2", "superunit1", "superunit3"]:
                field_list.append(("base", row["query_narrative"].strip(), event_with_abstractions[idx]["base"]))
                field_list.append(("target1", row["first_choice"].strip(), event_with_abstractions[idx]["target1"]))
                field_list.append(("target2", row["second_choice"].strip(), event_with_abstractions[idx]["target2"]))
                
                


            if args.task in ["abstraction_extraction1", "abstraction_extraction2", "abstraction_extraction3", "abstraction_extraction4", "abstraction_extraction5", "abstraction_extraction9", "abstraction_extraction13", "abstraction_extraction14", "abstraction_extraction20", "abstraction_extraction22", "abstraction_extraction23", "abstraction_extraction24", "abstraction_extraction25", "abstraction_extraction26", "stage_extraction3", "stage_extraction1"]:
                for field_name, text, events in field_list:
                    prompts.append(fmt.format(story=text, phrases=convert_events_to_formatted_string(events)))
                    index_map.append((idx, field_name))
            elif args.task in ["abstraction_extraction6", "abstraction_extraction7", "abstraction_extraction8", "abstraction_extraction21"]:
                for field_name, text, events, events_abstractions in field_list:
                    prompts.append(fmt.format(story=text, phrases=convert_events_to_formatted_string2(events, events_abstractions)))
                    index_map.append((idx, field_name))
            elif args.task in ["superunit2", "superunit1", "superunit3"]:
                for field_name, text, events in field_list:
                    prompts.append(fmt.format(story=text, groups=group_phrases_by_role(events)))
                    index_map.append((idx, field_name))


    elif dataset_name == "MCQ":
        print("Creating prompts for MCQ dataset")
        for idx in tqdm(range(len(dataset_dict))):
            field_list = []

            if args.task in ["abstraction_extraction1", "abstraction_extraction2", "abstraction_extraction3", "abstraction_extraction4", "abstraction_extraction5", "abstraction_extraction9", "abstraction_extraction13", "abstraction_extraction14", "abstraction_extraction20", "abstraction_extraction22", "abstraction_extraction23", "abstraction_extraction24", "stage_extraction1"]:
                field_list.append(("base", dataset_dict[idx]["source"].strip(), dataset_event[idx]["base"]))
                field_list.append(("target1", dataset_dict[idx]["choices"][0].strip(), dataset_event[idx]["target1"]))
                field_list.append(("target2", dataset_dict[idx]["choices"][1].strip(), dataset_event[idx]["target2"]))
                field_list.append(("target3", dataset_dict[idx]["choices"][2].strip(), dataset_event[idx]["target3"]))
                field_list.append(("target4", dataset_dict[idx]["choices"][3].strip(), dataset_event[idx]["target4"]))
            elif args.task in ["abstraction_extraction6", "abstraction_extraction7", "abstraction_extraction8", "abstraction_extraction21"]:
                field_list.append(("base", dataset_dict[idx]["source"].strip(), dataset_event[idx]["base"], event_with_abstractions[idx]["base"]))
                field_list.append(("target1", dataset_dict[idx]["choices"][0].strip(), dataset_event[idx]["target1"], event_with_abstractions[idx]["target1"]))
                field_list.append(("target2", dataset_dict[idx]["choices"][1].strip(), dataset_event[idx]["target2"], event_with_abstractions[idx]["target2"]))
                field_list.append(("target3", dataset_dict[idx]["choices"][2].strip(), dataset_event[idx]["target3"], event_with_abstractions[idx]["target3"]))
                field_list.append(("target4", dataset_dict[idx]["choices"][3].strip(), dataset_event[idx]["target4"], event_with_abstractions[idx]["target4"]))
            elif args.task in ["abstraction_extraction25", "abstraction_extraction26", "stage_extraction3"]:
                field_list.append(("base", dataset_dict[idx]["source"].strip(), sort_list_by_dict(dataset_event[idx]["base"], event_with_abstractions[idx]["base"])))
                field_list.append(("target1", dataset_dict[idx]["choices"][0].strip(), sort_list_by_dict(dataset_event[idx]["target1"], event_with_abstractions[idx]["target1"])))
                field_list.append(("target2", dataset_dict[idx]["choices"][1].strip(), sort_list_by_dict(dataset_event[idx]["target2"], event_with_abstractions[idx]["target2"])))
                field_list.append(("target3", dataset_dict[idx]["choices"][2].strip(), sort_list_by_dict(dataset_event[idx]["target3"], event_with_abstractions[idx]["target3"])))
                field_list.append(("target4", dataset_dict[idx]["choices"][3].strip(), sort_list_by_dict(dataset_event[idx]["target4"], event_with_abstractions[idx]["target4"])))
            elif args.task in ["superunit2", "superunit1", "superunit3"]:
                field_list.append(("base", dataset_dict[idx]["source"].strip(), event_with_abstractions[idx]["base"]))
                field_list.append(("target1", dataset_dict[idx]["choices"][0].strip(), event_with_abstractions[idx]["target1"]))
                field_list.append(("target2", dataset_dict[idx]["choices"][1].strip(), event_with_abstractions[idx]["target2"]))
                field_list.append(("target3", dataset_dict[idx]["choices"][2].strip(), event_with_abstractions[idx]["target3"]))
                field_list.append(("target4", dataset_dict[idx]["choices"][3].strip(), event_with_abstractions[idx]["target4"]))



            
            if args.task in ["abstraction_extraction1", "abstraction_extraction2", "abstraction_extraction3", "abstraction_extraction4", "abstraction_extraction5", "abstraction_extraction9", "abstraction_extraction13", "abstraction_extraction14", "abstraction_extraction20", "abstraction_extraction22", "abstraction_extraction23", "abstraction_extraction24", "abstraction_extraction25", "abstraction_extraction26", "stage_extraction3", "stage_extraction1"]:
                for field_name, text, events in field_list:
                    prompts.append(fmt.format(story=text, phrases=convert_events_to_formatted_string(events)))
                    index_map.append((idx, field_name))
            elif args.task in ["abstraction_extraction6", "abstraction_extraction7", "abstraction_extraction8", "abstraction_extraction21"]:
                for field_name, text, events, events_abstractions in field_list:
                    prompts.append(fmt.format(story=text, phrases=convert_events_to_formatted_string2(events, events_abstractions)))
                    index_map.append((idx, field_name))
            elif args.task in ["superunit2", "superunit1", "superunit3"]:
                for field_name, text, events in field_list:
                    prompts.append(fmt.format(story=text, groups=group_phrases_by_role(events)))
                    index_map.append((idx, field_name))


    return prompts, index_map

def gpu_analysis(prompts):
    prompt_lengths = []
    print("Counting tokens per prompt...")
    for p in tqdm(prompts, desc="Prompts"):
        prompt_lengths.append(tokenise_vllm_batch(p))

    num_prompts = len(prompt_lengths)
    avg_len = sum(prompt_lengths) / num_prompts
    max_len = max(prompt_lengths)
    print(f"\n=== Per-prompt stats ===")
    print(f"Prompts: {num_prompts}")
    print(f"Average length: {avg_len:.1f} tokens")
    print(f"Max length: {max_len} tokens")

    # ---- Per-batch totals ----
    batch_sizes=[8, 16, 32]

    for bs in batch_sizes:
        batch_totals = []
        for i in range(0, num_prompts, bs):
            batch_totals.append(sum(prompt_lengths[i:i+bs]))
        avg_batch = sum(batch_totals) / len(batch_totals)
        max_batch = max(batch_totals)
        print(f"\n=== Batch size {bs} ===")
        print(f"Number of batches: {len(batch_totals)}")
        print(f"Average batch total: {avg_batch:.1f} tokens")
        print(f"Max batch total: {max_batch} tokens")


def abstraction_extraction_pipeline_ARN_all(arn_data, arn_event, args, batch_size=16):
    prompts, index_map = build_all_prompts_abstraction(arn_data, arn_event, "ARN", args)

    if args.task == "abstraction_extraction25" or args.task == "abstraction_extraction26" or args.task == "stage_extraction3":
        model_short = model_short_dict.get(args.model)
        event_with_abstractions_path1 = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction24_arn.pkl"

        with open(event_with_abstractions_path1, 'rb') as f:
            event_with_abstractions1 = pickle.load(f)

    # gpu_analysis(prompts)

    abstraction_dict = {}

    # abstraction_dict9 = {}
    # abstraction_dict10 = {}
    # abstraction_dict11 = {}


    global_offset = 0

    print("Extracting abstractions for ARN dataset")
    for chunk in tqdm(list(batched(prompts, batch_size)), desc="Batches"):

        raw_texts = query_models_batch(chunk, args.model)


        assert len(raw_texts) == len(chunk), f"Model batch output size mismatch for batch {global_offset}!"

        # 2) Map this batch back to its portion of index_map
        slice_map = index_map[global_offset : global_offset + len(chunk)]

        # 3) Parse and assign
        for raw, (row_idx, field_name) in zip(raw_texts, slice_map):

            if args.task == "abstraction_extraction25" or args.task == "abstraction_extraction26" or args.task == "stage_extraction3":
                abstractions_out = map_text_to_abstraction(convert_events_to_object_array(sort_list_by_dict(arn_event[row_idx][field_name], event_with_abstractions1[row_idx][field_name])), raw)
            elif args.task == "superunit2" or args.task == "superunit1" or args.task == "superunit3":
                abstractions_out = map_text_to_stages(raw)
            else:
                abstractions_out = map_text_to_abstraction(convert_events_to_object_array(arn_event[row_idx][field_name]), raw)

            if row_idx not in abstraction_dict:
                abstraction_dict[row_idx] = {}
            abstraction_dict[row_idx][field_name] = abstractions_out



            # abstractions_out9 = map_text_to_abstraction9(convert_events_to_object_array(arn_event[row_idx][field_name]), raw)
            # abstractions_out10 = map_text_to_abstraction10(convert_events_to_object_array(arn_event[row_idx][field_name]), raw)
            # abstractions_out11 = map_text_to_abstraction11(convert_events_to_object_array(arn_event[row_idx][field_name]), raw)

            # if row_idx not in abstraction_dict9:
            #     abstraction_dict9[row_idx] = {}

            # if row_idx not in abstraction_dict10:
            #     abstraction_dict10[row_idx] = {}

            # if row_idx not in abstraction_dict11:
            #     abstraction_dict11[row_idx] = {}

            # abstraction_dict9[row_idx][field_name] = abstractions_out9
            # abstraction_dict10[row_idx][field_name] = abstractions_out10
            # abstraction_dict11[row_idx][field_name] = abstractions_out11



        global_offset += len(chunk)


    model_short = model_short_dict.get(args.model)
    task_short  = task_abstraction_short.get(args.task)

    
    path_save = f"{PATH_ABSTRACTION}{model_short}{args.unit}_{task_short}_arn.pkl"
    with open(path_save, 'wb') as f:
        pickle.dump(abstraction_dict, f)

    print("saved as: ", path_save)

    # path_save9 = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction9_arn.pkl"
    # path_save10 = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction10_arn.pkl"
    # path_save11 = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction11_arn.pkl"



    # with open(path_save9, 'wb') as f:
    #     pickle.dump(abstraction_dict9, f)

    # print("saved as: ", path_save9)

    # with open(path_save10, 'wb') as f:
    #     pickle.dump(abstraction_dict10, f)

    # print("saved as: ", path_save10)

    # with open(path_save11, 'wb') as f:
    #     pickle.dump(abstraction_dict11, f)

    # print("saved as: ", path_save11)


def abstraction_extraction_pipeline_MCQ_all(mcq_data, mcq_event, args, batch_size=16):
    prompts, index_map = build_all_prompts_abstraction(mcq_data, mcq_event, "MCQ", args)

    if args.task == "abstraction_extraction25" or args.task == "abstraction_extraction26" or args.task == "stage_extraction3":
        model_short = model_short_dict.get(args.model)
        event_with_abstractions_path1 = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction24_mcq.pkl"

        with open(event_with_abstractions_path1, 'rb') as f:
            event_with_abstractions1 = pickle.load(f)

    abstraction_dict = {}

    # abstraction_dict9 = {}
    # abstraction_dict10 = {}
    # abstraction_dict11 = {}


    global_offset = 0

    print("Extracting abstractions for MCQ dataset")
    for chunk in tqdm(list(batched(prompts, batch_size)), desc="Batches"):
        raw_texts = query_models_batch(chunk, args.model)

        assert len(raw_texts) == len(chunk), f"Model batch output size mismatch for batch {global_offset}!"

        # 2) Map this batch back to its portion of index_map
        slice_map = index_map[global_offset : global_offset + len(chunk)]

        # 3) Parse and assign
        for raw, (row_idx, field_name) in zip(raw_texts, slice_map):
            if args.task == "abstraction_extraction25" or args.task == "abstraction_extraction26" or args.task == "stage_extraction3":
                abstractions_out = map_text_to_abstraction(convert_events_to_object_array(sort_list_by_dict(mcq_event[row_idx][field_name], event_with_abstractions1[row_idx][field_name])), raw)
            elif args.task == "superunit2" or args.task == "superunit1" or args.task == "superunit3":
                abstractions_out = map_text_to_stages(raw)
            else:
                abstractions_out = map_text_to_abstraction(convert_events_to_object_array(mcq_event[row_idx][field_name]), raw)

            if row_idx not in abstraction_dict:
                abstraction_dict[row_idx] = {}
            abstraction_dict[row_idx][field_name] = abstractions_out


            # abstractions_out9 = map_text_to_abstraction9(convert_events_to_object_array(mcq_event[row_idx][field_name]), raw)
            # abstractions_out10 = map_text_to_abstraction10(convert_events_to_object_array(mcq_event[row_idx][field_name]), raw)
            # abstractions_out11 = map_text_to_abstraction11(convert_events_to_object_array(mcq_event[row_idx][field_name]), raw)

            # if row_idx not in abstraction_dict:
            #     abstraction_dict[row_idx] = {}
            # abstraction_dict[row_idx][field_name] = abstractions_out

            # if row_idx not in abstraction_dict9:
            #     abstraction_dict9[row_idx] = {}

            # if row_idx not in abstraction_dict10:
            #     abstraction_dict10[row_idx] = {}

            # if row_idx not in abstraction_dict11:
            #     abstraction_dict11[row_idx] = {}

            # abstraction_dict9[row_idx][field_name] = abstractions_out9
            # abstraction_dict10[row_idx][field_name] = abstractions_out10
            # abstraction_dict11[row_idx][field_name] = abstractions_out11


        global_offset += len(chunk)


    model_short = model_short_dict.get(args.model)
    task_short  = task_abstraction_short.get(args.task)
    
    path_save = f"{PATH_ABSTRACTION}{model_short}{args.unit}_{task_short}_mcq.pkl"

    with open(path_save, 'wb') as f:
        pickle.dump(abstraction_dict, f)

    print("saved as: ", path_save)


    # path_save9 = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction9_mcq.pkl"
    # path_save10 = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction10_mcq.pkl"
    # path_save11 = f"{PATH_ABSTRACTION}{model_short}{args.unit}_abstraction11_mcq.pkl"



    # with open(path_save9, 'wb') as f:
    #     pickle.dump(abstraction_dict9, f)

    # print("saved as: ", path_save9)

    # with open(path_save10, 'wb') as f:
    #     pickle.dump(abstraction_dict10, f)

    # print("saved as: ", path_save10)

    # with open(path_save11, 'wb') as f:
    #     pickle.dump(abstraction_dict11, f)

    # print("saved as: ", path_save11)


######### Random datasets and without batching

def abstraction_extraction_model(story, phrases, model_name, args):
    if args.task == "abstraction_extraction1":
        prompt = prompt_abstraction_extraction1.format(story=story, phrases=convert_events_to_formatted_string(phrases))
    elif args.task == "abstraction_extraction2":
        prompt = prompt_abstraction_extraction2.format(story=story, phrases=convert_events_to_formatted_string(phrases))
    elif args.task == "abstraction_extraction3":
        prompt = prompt_abstraction_extraction3.format(story=story, phrases=convert_events_to_formatted_string(phrases))
    elif args.task == "abstraction_extraction4":
        prompt = prompt_abstraction_extraction4.format(story=story, phrases=convert_events_to_formatted_string(phrases))
    elif args.task == "abstraction_extraction5":
        prompt = prompt_abstraction_extraction5.format(story=story, phrases=convert_events_to_formatted_string(phrases))
    
    model_abstraction = query_models(prompt, model_name)
    
    abstractions_dict = map_text_to_abstraction(convert_events_to_object_array(phrases), model_abstraction)
    
    return abstractions_dict
    
def abstraction_extraction_pipeline_ARN_random(arn_data, arn_event, args):
    
    abstraction_dict = {}
    
    for index in tqdm(arn_data):
        sample = arn_data[index]
        base_story = sample['base_story'].strip()
        target_story1 = sample['target0'].strip()
        target_story2 = sample['target1'].strip()
        
        dict_events_index = arn_event[index]
        base_story_events = dict_events_index['base']
        target_story1_events = dict_events_index['target1']
        target_story2_events = dict_events_index['target2']
        
        abstraction_dict[index] = {}
        
        abstraction_dict[index]['base'] = abstraction_extraction_model(base_story, base_story_events, args.model, args)
        abstraction_dict[index]['target1'] = abstraction_extraction_model(target_story1, target_story1_events, args.model, args)
        abstraction_dict[index]['target2'] = abstraction_extraction_model(target_story2, target_story2_events, args.model, args)
        
        
    model_short = model_short_dict.get(args.model)
    task_short  = task_abstraction_short.get(args.task)
    
    path_save = f"{PATH_ABSTRACTION}{model_short}{args.unit}_{task_short}_dict_arn_random.pkl"

    with open(path_save, 'wb') as f:
        pickle.dump(abstraction_dict, f)
        
        
def abstraction_extraction_pipeline_MCQ_random(mcq_data, mcq_event, args):
    
    abstraction_dict = {}

    for index in tqdm(mcq_data):
        sample = mcq_data[index]
        base_story = sample['base_story'].strip()
        target_story1 = sample['target0'].strip()
        target_story2 = sample['target1'].strip()
        target_story3 = sample['target2'].strip()
        target_story4 = sample['target3'].strip()
        
        dict_events_index = mcq_event[index]
        base_story_events = dict_events_index['base']
        target_story1_events = dict_events_index['target1']
        target_story2_events = dict_events_index['target2']
        target_story3_events = dict_events_index['target3']
        target_story4_events = dict_events_index['target4']
        
        abstraction_dict[index] = {}
        
        abstraction_dict[index]['base'] = abstraction_extraction_model(base_story, base_story_events, args.model, args)
        abstraction_dict[index]['target1'] = abstraction_extraction_model(target_story1, target_story1_events, args.model, args)
        abstraction_dict[index]['target2'] = abstraction_extraction_model(target_story2, target_story2_events, args.model, args)
        abstraction_dict[index]['target3'] = abstraction_extraction_model(target_story3, target_story3_events, args.model, args)
        abstraction_dict[index]['target4'] = abstraction_extraction_model(target_story4, target_story4_events, args.model, args)
        
            
            
    model_short = model_short_dict.get(args.model)
    task_short  = task_abstraction_short.get(args.task)
    
    path_save = f"{PATH_ABSTRACTION}{model_short}{args.unit}_{task_short}_dict_mcq_random.pkl"
        
    with open(path_save, 'wb') as f:
        pickle.dump(abstraction_dict, f)
        
        
def run_abstraction_extraction(args):
    print(f"Model: {args.model}, Task: {args.task}, Unit: {args.unit}, Dataset: {args.dataset}")
    if args.dataset == "ARN_random":
        with open('Data/Datasets/arn_random_subset.pkl', 'rb') as f:
            arn_data = pickle.load(f)
            
        model_short = model_short_dict.get(args.model)
        path_save = f"{PATH_UNITS}{model_short}{args.unit}_arn_random.pkl"
        with open(path_save, 'rb') as f:
            arn_event = pickle.load(f)
        
        abstraction_extraction_pipeline_ARN_random(arn_data, arn_event, args)

    elif args.dataset == "ARN":
        arn_data = pd.read_csv('Data/Datasets/Analogical Reasoning on Narratives (ARN) dataset.xlsx - Sheet1.csv')

        model_short = model_short_dict.get(args.model)
        path_save = f"{PATH_UNITS}{model_short}{args.unit}_arn.pkl"

        with open(path_save, 'rb') as f:
            arn_event = pickle.load(f)


        abstraction_extraction_pipeline_ARN_all(arn_data, arn_event, args)
        
    elif args.dataset == "MCQ_random":
        with open('Data/Datasets/mcq_random_subset.pkl', 'rb') as f:
            mcq_data = pickle.load(f)
            
        model_short = model_short_dict.get(args.model)
        path_save = f"{PATH_UNITS}{model_short}{args.unit}_mcq_random.pkl"
        print("PATH TO LOAD EVENTS:")
        print(path_save)
        with open(path_save, 'rb') as f:
            mcq_event = pickle.load(f)
            
        abstraction_extraction_pipeline_MCQ_random(mcq_data, mcq_event, args)

    elif args.dataset == "MCQ":
        with open('Data/Datasets/storyanalogy_multiple_choice.json') as f:
            mcq_data = json.load(f)

        model_short = model_short_dict.get(args.model)
        path_save = f"{PATH_UNITS}{model_short}{args.unit}_mcq.pkl"
        print("PATH TO LOAD EVENTS:")
        print(path_save)
        with open(path_save, 'rb') as f:
            mcq_event = pickle.load(f)


        abstraction_extraction_pipeline_MCQ_all(mcq_data, mcq_event, args)


