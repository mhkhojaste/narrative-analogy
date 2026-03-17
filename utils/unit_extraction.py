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
from Data.Prompts.prompts_unit import *



PATH_UNITS = "Data_new/Units/"
os.makedirs(PATH_UNITS, exist_ok=True)

def extract_event_phrases_from_output(text):
    # print("Raw model output:")
    # print("################################")
    # print(text)
    # Step 1: Remove <JSON> tags and square brackets
    if '<JSON>' in text:
        text = text.replace('<JSON>', '')
    if '</JSON>' in text:
        text = text.replace('</JSON>', '')
    if '[' in text:
        text = text.replace('[', '')
    if ']' in text:
        text = text.replace(']', '')

    # Step 2
    raw_parts = text.split(',')

    final = []

    for item in raw_parts:
        item = item.strip()
        # Remove quotes
        item = item.replace("'", "").replace('"', "")  

        item = item.strip()

        # Step 3.1: Skip empty strings
        if item == '':
            continue

        # Step 3.2: Capitalize first letter if needed
        if not item[0].isupper():
            item = item[0].upper() + item[1:]

        # Step 3.3: Add to final list if not already there
        if item not in final:
            final.append(item)


    return final



######### Full datasets and with batching

def batched(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i+n]

def split_story_to_list_string(story: str) -> str:
    sentences = [s.strip() for s in story.split('.') if s.strip()]
    result = "\n".join(f"{i+1}. {sentence}" for i, sentence in enumerate(sentences))
    return result

def build_all_prompts_for_dataset(dataset_dict, dataset_name, args):
    """
    Returns:
      prompts: flat list of prompts
      index_map: list of (row_index, field_name) aligned with prompts
    """
    # choose template once
    if args.unit == "unit_event_phrases":
        fmt = prompt_event_phrase_extraction
    elif args.unit == "unit_event_phrases_2":
        fmt = prompt_event_phrase_extraction_2
    elif args.unit == "unit_event_phrases_3":
        fmt = prompt_event_phrase_extraction_3
    elif args.unit == "unit_event_phrases_4":
        fmt = prompt_event_phrase_extraction_4
    else:
        raise ValueError(f"Unknown unit: {args.unit}")

    prompts, index_map = [], []

    if dataset_name == "ARN":
        print("Creating prompts for ARN dataset")
        for idx, row in tqdm(dataset_dict.iterrows(), total=len(dataset_dict)):
            field_list = []
            field_list.append(("base", row["query_narrative"].strip()))
            field_list.append(("target1", row["first_choice"].strip()))
            field_list.append(("target2", row["second_choice"].strip()))

            if args.unit != "unit_event_phrases_4":
                for field_name, text in field_list:
                    prompts.append(fmt.format(story=text))
                    index_map.append((idx, field_name))
            else:
                for field_name, text in field_list:
                    prompts.append(fmt.format(story=split_story_to_list_string(text)))
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

            if args.unit != "unit_event_phrases_4":
                for field_name, text in field_list:
                    prompts.append(fmt.format(story=text))
                    index_map.append((idx, field_name))
            else:
                for field_name, text in field_list:
                    prompts.append(fmt.format(story=split_story_to_list_string(text)))
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

    print("prompt_lengths: ", prompt_lengths)


def unit_extraction_pipeline_ARN_all(arn_data, args, batch_size=16):

    prompts, index_map = build_all_prompts_for_dataset(arn_data, "ARN", args)


    unit_dict = {}
    global_offset = 0

    print("Extracting units for ARN dataset")
    for chunk in tqdm(list(batched(prompts, batch_size)), desc="Batches"):
        raw_texts = query_models_batch(chunk, args.model)

        assert len(raw_texts) == len(chunk), f"Model batch output size mismatch for batch {global_offset}!"

        # 2) Map this batch back to its portion of index_map
        slice_map = index_map[global_offset : global_offset + len(chunk)]

        # 3) Parse and assign
        for raw, (row_idx, field_name) in zip(raw_texts, slice_map):
            events_arr = extract_event_phrases_from_output(raw)
            if row_idx not in unit_dict:
                unit_dict[row_idx] = {}
            unit_dict[row_idx][field_name] = events_arr
        
        global_offset += len(chunk)


    model_short = model_short_dict.get(args.model)
    path_save = f"{PATH_UNITS}{model_short}{args.unit}_arn.pkl"
    with open(path_save, 'wb') as f:
        pickle.dump(unit_dict, f)

    print("saved as: ", path_save)


def unit_extraction_pipeline_MCQ_all(mcq_data, args, batch_size=16):

    prompts, index_map = build_all_prompts_for_dataset(mcq_data, "MCQ", args)
    unit_dict = {}
    global_offset = 0
    
    print("Extracting units for MCQ dataset")
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
    path_save = f"{PATH_UNITS}{model_short}{args.unit}_mcq.pkl"
    with open(path_save, 'wb') as f:
        pickle.dump(unit_dict, f)

    print("saved as: ", path_save)

######### Random datasets and without batching


def event_phrase_extraction_model(story, model_name, args):
    if args.unit == "unit_event_phrases":
        prompt = prompt_event_phrase_extraction.format(story=story)
    elif args.unit == "unit_event_phrases_2":
        prompt = prompt_event_phrase_extraction_2.format(story=story)
    elif args.unit == "unit_event_phrases_3":
        prompt = prompt_event_phrase_extraction_3.format(story=story)
        
    model_events = query_models(prompt, model_name)
    events_arr = extract_event_phrases_from_output(model_events)
    return events_arr
    
    
    
def unit_extraction_pipeline_ARN_random(arn_data, args):
    
    unit_dict = {}
    
    for index in tqdm(arn_data):
        sample = arn_data[index]
        base_story = sample['base_story'].strip()
        target_story1 = sample['target0'].strip()
        target_story2 = sample['target1'].strip()
        
        unit_dict[index] = {}
        
        unit_dict[index]['base'] = event_phrase_extraction_model(base_story, args.model, args)
        unit_dict[index]['target1'] = event_phrase_extraction_model(target_story1, args.model, args)
        unit_dict[index]['target2'] = event_phrase_extraction_model(target_story2, args.model, args)
        
            
        
    model_short = model_short_dict.get(args.model)
    path_save = f"{PATH_UNITS}{model_short}{args.unit}_arn_random.pkl"
    with open(path_save, 'wb') as f:
        pickle.dump(unit_dict, f)
        
        
def unit_extraction_pipeline_MCQ_random(mcq_data, args):
    
    unit_dict = {}

    for index in tqdm(mcq_data):
        sample = mcq_data[index]
        base_story = sample['base_story'].strip()
        target_story1 = sample['target0'].strip()
        target_story2 = sample['target1'].strip()
        target_story3 = sample['target2'].strip()
        target_story4 = sample['target3'].strip()
        
        unit_dict[index] = {}
        
        unit_dict[index]['base'] = event_phrase_extraction_model(base_story, args.model, args)
        unit_dict[index]['target1'] = event_phrase_extraction_model(target_story1, args.model, args)
        unit_dict[index]['target2'] = event_phrase_extraction_model(target_story2, args.model, args)
        unit_dict[index]['target3'] = event_phrase_extraction_model(target_story3, args.model, args)
        unit_dict[index]['target4'] = event_phrase_extraction_model(target_story4, args.model, args)
        
            
            
    model_short = model_short_dict.get(args.model)
    path_save = f"{PATH_UNITS}{model_short}{args.unit}_mcq_random.pkl"
    with open(path_save, 'wb') as f:
        pickle.dump(unit_dict, f)
    
        
########### main function     

def run_unit_extraction(args):
    
    if args.dataset == "ARN_random":
        with open('Data/Datasets/arn_random_subset.pkl', 'rb') as f:
            arn_data = pickle.load(f)
        unit_extraction_pipeline_ARN_random(arn_data, args)

    elif args.dataset == "ARN":
        arn_data = pd.read_csv('Data/Datasets/Analogical Reasoning on Narratives (ARN) dataset.xlsx - Sheet1.csv')
        unit_extraction_pipeline_ARN_all(arn_data, args)


    elif args.dataset == "MCQ_random":
        with open('Data/Datasets/mcq_random_subset.pkl', 'rb') as f:
            mcq_data = pickle.load(f)
            
        unit_extraction_pipeline_MCQ_random(mcq_data, args)

    elif args.dataset == "MCQ":
        with open('Data/Datasets/storyanalogy_multiple_choice.json') as f:
            mcq_data = json.load(f)

        unit_extraction_pipeline_MCQ_all(mcq_data, args)
    
        
        
        
    