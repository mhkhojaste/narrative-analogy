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

from utils.helper_utils import *
from Data.Prompts.prompt_superunit import *


PATH_UNITS = "Data_YF/Units/"
PATH_STAGE = "Data_YF/Stage/"
PATH_SUPERUNIT = "Data_YF/Super_units/"

os.makedirs(PATH_SUPERUNIT, exist_ok=True)

def stage_dict_to_custom_string(data):

    # Group phrases by TP code
    grouped = defaultdict(list)
    for phrase, tp in data.items():
        grouped[tp].append(phrase)

    # Ensure groups are ordered TP1 -> TP5
    ordered_groups = sorted(grouped.items(), key=lambda x: int(x[0][2:]))

    # Build the structured list
    result = []
    phrase_id = 1
    for tp, phrases in ordered_groups:
        phrase_list = []
        for phrase in phrases:
            phrase_list.append({
                "id": f"p{phrase_id}",
                "text": phrase
            })
            phrase_id += 1
        result.append({
            "role_code": tp,
            "phrases": phrase_list
        })

    # Now format the string exactly like required
    lines = ["["]
    for group in result:
        lines.append("  {")
        lines.append(f"    \"role_code\": \"{group['role_code']}\",")
        lines.append("    \"phrases\": [")
        for i, phrase in enumerate(group["phrases"]):
            comma = "," if i < len(group["phrases"]) - 1 else ""
            lines.append(f"      {{ \"id\":\"{phrase['id']}\",\"text\":\"{phrase['text']}\" }}{comma}")
        lines.append("    ]")
        lines.append("  },")
    if lines[-1].endswith(","):
        lines[-1] = lines[-1][:-1]  # remove last comma
    lines.append("]")

    return "\n".join(lines)



def parse_json_stage_string(text: str):
    cleaned = text.replace("<JSON>", "").replace("</JSON>", "").strip()
    

    data = json.loads(cleaned)

    result = {
        item["role_code"]: {
            "kernel_name": item["kernel_name"],
            "rationale": item["rationale"]
        }
        for item in data["results"]
    }

    return result
    
def superunit_extraction_model(story, stages, model_name, args):
    if "super1" in args.task:
        prompt = prompt_group_abstraction.format(story=story, groups=stage_dict_to_custom_string(stages))
        
    model_superunits = query_models(prompt, model_name)
    superunits_answer = parse_json_stage_string(model_superunits)
    
    return superunits_answer
    
    
def superunit_extraction_pipeline_ARN_random(arn_data, arn_stages, args):
    
    superunits_dict = {}
    
    for index in tqdm(arn_data):
        sample = arn_data[index]
        base_story = sample['base_story'].strip()
        target_story1 = sample['target0'].strip()
        target_story2 = sample['target1'].strip()
        
        dict_stages_index = arn_stages[index]
        base_stage_dict = dict_stages_index["base"]
        target1_stage_dict = dict_stages_index["target1"]
        target2_stage_dict = dict_stages_index["target2"]
        
        superunits_dict[index] = {}
        
        superunits_dict[index]['base'] = superunit_extraction_model(base_story, base_stage_dict, args.model, args)
        superunits_dict[index]['target1'] = superunit_extraction_model(target_story1, target1_stage_dict, args.model, args)
        superunits_dict[index]['target2'] = superunit_extraction_model(target_story2, target2_stage_dict, args.model, args)

        
        
    model_short = model_short_dict.get(args.model)
    path_save = f"{PATH_SUPERUNIT}{model_short}{args.unit}_{args.task}_arn_random.pkl"
    with open(path_save, 'wb') as f:
        pickle.dump(superunits_dict, f)
        

def superunit_extraction_pipeline_MCQ_random(mcq_data, mcq_stages, args):
    
    superunits_dict = {}

    for index in tqdm(mcq_data):
        sample = mcq_data[index]
        base_story = sample['base_story'].strip()
        target_story1 = sample['target0'].strip()
        target_story2 = sample['target1'].strip()
        target_story3 = sample['target2'].strip()
        target_story4 = sample['target3'].strip()
        
        dict_stages_index = mcq_stages[index]
        base_stage_dict = dict_stages_index["base"]
        target1_stage_dict = dict_stages_index["target1"]
        target2_stage_dict = dict_stages_index["target2"]
        target3_stage_dict = dict_stages_index["target3"]
        target4_stage_dict = dict_stages_index["target4"]
        
        superunits_dict[index] = {}
        
        superunits_dict[index]['base'] = superunit_extraction_model(base_story, base_stage_dict, args.model, args)
        superunits_dict[index]['target1'] = superunit_extraction_model(target_story1, target1_stage_dict, args.model, args)
        superunits_dict[index]['target2'] = superunit_extraction_model(target_story2, target2_stage_dict, args.model, args)
        superunits_dict[index]['target3'] = superunit_extraction_model(target_story3, target3_stage_dict, args.model, args)
        superunits_dict[index]['target4'] = superunit_extraction_model(target_story4, target4_stage_dict, args.model, args)
            
            
            
    model_short = model_short_dict.get(args.model)
    path_save = f"{PATH_SUPERUNIT}{model_short}{args.unit}_{args.task}_mcq_random.pkl"
    with open(path_save, 'wb') as f:
        pickle.dump(superunits_dict, f)
        
def run_superunit_extraction(args):
    
    if args.dataset == "ARN_random":
        with open('Data/Datasets/arn_random_subset.pkl', 'rb') as f:
            arn_data = pickle.load(f)
            
        model_short = model_short_dict.get(args.model)
        task_short  = args.task.split("_")[0]
        path_save = f"{PATH_STAGE}{model_short}{args.unit}_{task_short}_arn_random.pkl"
        with open(path_save, 'rb') as f:
            arn_stages = pickle.load(f)
        
        superunit_extraction_pipeline_ARN_random(arn_data, arn_stages, args)
        
    elif args.dataset == "MCQ_random":
        with open('Data/Datasets/mcq_random_subset.pkl', 'rb') as f:
            mcq_data = pickle.load(f)
            
        model_short = model_short_dict.get(args.model)
        task_short  = args.task.split("_")[0]
        path_save = f"{PATH_STAGE}{model_short}{args.unit}_{task_short}_mcq_random.pkl"
        with open(path_save, 'rb') as f:
            mcq_stages = pickle.load(f)
            
        superunit_extraction_pipeline_MCQ_random(mcq_data, mcq_stages, args)
