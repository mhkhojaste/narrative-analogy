import re
from collections import defaultdict
from tqdm import tqdm
import sys
import json
import numpy as np
import os
import time
import ast
import pickle
import pandas as pd
from typing import Dict, Any, Tuple


from utils.helper_utils import *
from Data.Prompts.prompts_unit import *



PATH_UNITS = "Data_new/Units/"
os.makedirs(PATH_UNITS, exist_ok=True)

def extract_event_phrases_from_output(text):
    strings_to_remove = ["<JSON>", "</JSON>", "[", "]"]
    for string in strings_to_remove:
        text = text.replace(string, "")

    final = []

    for item in text.split(','):
        item = item.strip().replace("'", "").replace('"', "").strip()

        if item:
            item = item if item[0].isupper() else item[0].upper() + item[1:]

            if item not in final:
                final.append(item)
    return final

def batched(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i+n]

def build_all_prompts_for_dataset(dataset_dict, dataset_name, args):
    fmt = prompt_event_phrase_extraction
    prompts, index_map = [], []

    print(f"Creating prompts for {dataset_name} dataset")
    if dataset_name == "ARN":
        for idx, row in tqdm(dataset_dict.iterrows(), total=len(dataset_dict)):
            field_list = []
            field_list.append(("base", row["query_narrative"].strip()))
            field_list.append(("target1", row["first_choice"].strip()))
            field_list.append(("target2", row["second_choice"].strip()))
            
            for field_name, text in field_list:
                prompts.append(fmt.format(story=text))
                index_map.append((idx, field_name))

    elif dataset_name == "MCQ":
        print("Creating prompts for MCQ dataset")
        for idx in tqdm(range(len(dataset_dict))):
            field_list = []
            field_list.append(("base", dataset_dict[idx]["source"].strip()))
            field_list.append(("target1", dataset_dict[idx]["choices"][0].strip()))
            field_list.append(("target2", dataset_dict[idx]["choices"][1].strip()))
            field_list.append(("target3", dataset_dict[idx]["choices"][2].strip()))
            field_list.append(("target4", dataset_dict[idx]["choices"][3].strip()))

            for field_name, text in field_list:
                prompts.append(fmt.format(story=text))
                index_map.append((idx, field_name))

    return prompts, index_map


def unit_extraction_pipeline_all(data, dataset_name, args, batch_size=16):
    prompts, index_map = build_all_prompts_for_dataset(data, dataset_name, args)

    unit_dict = {}
    global_offset = 0

    print(f"Extracting units for {dataset_name} dataset")

    for chunk in tqdm(list(batched(prompts, batch_size)), desc="Batches"):
        raw_texts = query_models_batch(chunk, args.model)

        assert len(raw_texts) == len(chunk), f"Model batch output size mismatch for batch {global_offset}!"

        slice_map = index_map[global_offset : global_offset + len(chunk)]

        for raw, (row_idx, field_name) in zip(raw_texts, slice_map):
            events_arr = extract_event_phrases_from_output(raw)

            if row_idx not in unit_dict:
                unit_dict[row_idx] = {}

            unit_dict[row_idx][field_name] = events_arr

        global_offset += len(chunk)

    model_short = model_short_dict.get(args.model)
    dataset_suffix = dataset_name.lower()
    path_save = f"{PATH_UNITS}{model_short}{args.unit}_{dataset_suffix}.pkl"

    with open(path_save, "wb") as f:
        pickle.dump(unit_dict, f)

    print("saved as:", path_save)
    
        
########### main function     

def run_unit_extraction(args):
    if args.dataset == "ARN":
        data = pd.read_csv('Data/Datasets/Analogical Reasoning on Narratives (ARN) dataset.xlsx - Sheet1.csv')
    elif args.dataset == "MCQ":
        with open('Data/Datasets/storyanalogy_multiple_choice.json') as f:
            data = json.load(f)
    else:
        raise ValueError(f"Unsupported dataset: {args.dataset}")

    unit_extraction_pipeline_all(data, args.dataset, args)
    
        
        
        
    