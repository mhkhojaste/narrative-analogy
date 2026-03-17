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
from Data.Prompts.prompts_stage import *

PATH_UNITS = "Data_YF/Units/"
PATH_STAGE = "Data_YF/Stage/"
os.makedirs(PATH_STAGE, exist_ok=True)
# 顶部
import json, re
from json.decoder import JSONDecodeError
try:
    import json5
except Exception:
    json5 = None
try:
    from json_repair import repair_json
except Exception:
    repair_json = None

def robust_json_loads(s: str):
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s.strip(), flags=re.IGNORECASE)

    try:
        return json.loads(s)
    except JSONDecodeError:
        pass


    if "{" in s and "}" in s:
        chunk = s[s.find("{"): s.rfind("}") + 1]
        try:
            return json.loads(chunk)
        except JSONDecodeError:
            s2 = chunk
    else:
        s2 = s

    if json5 is not None:
        try:
            return json5.loads(s2)
        except Exception:
            pass

    if repair_json is not None:
        try:
            fixed = repair_json(s2)
            return json.loads(fixed)
        except Exception:
            pass

    s3 = re.sub(r'(?<!\\)"?"?([A-Za-z_]\w*)"?\s*:', r'"\1":', s2)  
    s3 = re.sub(r",\s*([}\]])", r"\1", s3)                         
    s3 = re.sub(r"(?<!\\)'", '"', s3)                              
    return json.loads(s3)



def convert_events_to_object_array(strings):
    return [{"id": f"p{i+1}", "text": text} for i, text in enumerate(strings)]
    
def convert_events_to_formatted_string(strings):
    items = [
        f'  {{ "id":"p{i+1}","text":"{text}" }}'
        for i, text in enumerate(strings)
    ]
    return "[\n" + ",\n".join(items) + "\n]"
    
    
def map_text_to_role(array, json_str):
    json_str_clean = json_str.replace("<JSON>", "").replace("</JSON>", "").strip()
    
    data = robust_json_loads(json_str_clean)
    
    id_to_text = {item['id']: item['text'] for item in array}
    
    text_to_role = {}
    for result in data["results"]:
        _id = result["id"]
        role = result["role"]
        if _id in id_to_text:
            text_to_role[id_to_text[_id]] = role
    
    return text_to_role
    
    
def stage_extraction_model(story, events, model_name, args):
    if args.task == "stage_extraction":
        prompt = prompt_stage_extraction.format(story=story, events=convert_events_to_formatted_string(events))
    elif args.task == "stage_extraction2":
        prompt = prompt_stage_extraction2.format(story=story, events=convert_events_to_formatted_string(events))
    elif args.task == "stage_extraction3":
        prompt = prompt_stage_extraction3.format(story=story, events=convert_events_to_formatted_string(events))
        
    model_stages = query_models(prompt, model_name)
    
    stages_dict = map_text_to_role(convert_events_to_object_array(events), model_stages)
    
    return stages_dict
    

def stage_extraction_pipeline_ARN_random(arn_data, arn_event, args):
    
    stage_dict = {}
    
    for index in tqdm(arn_data):
        sample = arn_data[index]
        base_story = sample['base_story'].strip()
        target_story1 = sample['target0'].strip()
        target_story2 = sample['target1'].strip()
        
        dict_events_index = arn_event[index]
        base_story_events = dict_events_index['base']
        target_story1_events = dict_events_index['target1']
        target_story2_events = dict_events_index['target2']
        
        stage_dict[index] = {}
        
        stage_dict[index]['base'] = stage_extraction_model(base_story, base_story_events, args.model, args)
        stage_dict[index]['target1'] = stage_extraction_model(target_story1, target_story1_events, args.model, args)
        stage_dict[index]['target2'] = stage_extraction_model(target_story2, target_story2_events, args.model, args)
        
        
        
    model_short = model_short_dict.get(args.model)
    task_short  = task_stage_short.get(args.task)
    path_save = f"{PATH_STAGE}{model_short}{args.unit}_{task_short}_arn_random.pkl"
    with open(path_save, 'wb') as f:
        pickle.dump(stage_dict, f)
        
        
def stage_extraction_pipeline_MCQ_random(mcq_data, mcq_event, args):
    
    stage_dict = {}

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
        
        stage_dict[index] = {}
        
        stage_dict[index]['base'] = stage_extraction_model(base_story, base_story_events, args.model, args)
        stage_dict[index]['target1'] = stage_extraction_model(target_story1, target_story1_events, args.model, args)
        stage_dict[index]['target2'] = stage_extraction_model(target_story2, target_story2_events, args.model, args)
        stage_dict[index]['target3'] = stage_extraction_model(target_story3, target_story3_events, args.model, args)
        stage_dict[index]['target4'] = stage_extraction_model(target_story4, target_story4_events, args.model, args)
        
            
            
            
    model_short = model_short_dict.get(args.model)
    task_short  = task_stage_short.get(args.task)
    path_save = f"{PATH_STAGE}{model_short}{args.unit}_{task_short}_mcq_random.pkl"
    with open(path_save, 'wb') as f:
        pickle.dump(stage_dict, f)


def run_stage_extraction(args):
    
    if args.dataset == "ARN_random":
        with open('Data/Datasets/arn_random_subset.pkl', 'rb') as f:
            arn_data = pickle.load(f)
            
        model_short = model_short_dict.get(args.model)
        path_save = f"{PATH_UNITS}{model_short}{args.unit}_arn_random.pkl"
        with open(path_save, 'rb') as f:
            arn_event = pickle.load(f)
        
        stage_extraction_pipeline_ARN_random(arn_data, arn_event, args)
        
    elif args.dataset == "MCQ_random":
        with open('Data/Datasets/mcq_random_subset.pkl', 'rb') as f:
            mcq_data = pickle.load(f)
            
        model_short = model_short_dict.get(args.model)
        path_save = f"{PATH_UNITS}{model_short}{args.unit}_mcq_random.pkl"
        with open(path_save, 'rb') as f:
            mcq_event = pickle.load(f)
            
        stage_extraction_pipeline_MCQ_random(mcq_data, mcq_event, args)