import openai
import re
from collections import defaultdict
import ollama
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
from transformers import AutoModelForCausalLM, AutoTokenizer
sys.path.append(os.path.abspath('../../../UtilsYF'))
from normal_utils import *
from Data.prompt_string import *

prompt_dict = read_json_file('./Data/prompt_dict.json')

prompt_causal_functional = prompt_dict['prompt_causal_functional']
prompt_temporal = prompt_dict['prompt_temporal']
prompt_structural = prompt_dict['prompt_structural']

prompt_causal_functional2 = prompt_dict['prompt_causal_functional2']
prompt_temporal2 = prompt_dict['prompt_temporal2']

Prompt_causal2_CoT = prompt_dict['Prompt_causal2_CoT']


def build_relation_questions(base_event, target_events, relation_category):
    relations_map = {
        "Causal and Functional": ["CAUSE", "ENABLE", "PREVENT", "MOTIVATE"],
        "Temporal": ["BEFORE", "AFTER", "SYNCHRONOUS"],
        "Structural": ["SUBEVENT", "SAME"]
    }

    if relation_category not in relations_map:
        raise ValueError("Invalid category. Choose from: 'Causal and Functional', 'Temporal', 'Structural'.")

    questions_json = {}
    prev_valid_json = {}
    
    for relation in relations_map[relation_category]:
        questions_json[f"{relation} relations"] = {}

        counter_i = 1
        for i, target_event in enumerate(target_events, start=1):
            if target_event == base_event:
                continue
            
            if relation_category == "Causal and Functional":
                if relation == "CAUSE":
                    question = f"Does the event '{base_event}' directly {relation.lower()} the event '{target_event}'?"
                else:
                    question = f"Does the event '{base_event}' {relation.lower()} the event '{target_event}'?"
                    
            elif relation_category == "Temporal":
                if relation == "SYNCHRONOUS":
                    question = f"Are the events '{base_event}' and '{target_event}' {relation.lower()}?"
                else:
                    question = f"Does the event '{base_event}' happen {relation.lower()} the event '{target_event}'?"
                    
            elif relation_category == "Structural":
                if relation == "SUBEVENT":
                    question = f"Is the event '{base_event}' a {relation.lower()} of the event '{target_event}'?"
                else:
                    question = f"Is the event '{base_event}' the {relation.lower()} as the event '{target_event}'?"
                
                
                
            questions_json[f"{relation} relations"][counter_i] = {
                "base_event": base_event,
                "target_event": target_event,
                "question": question,
                "answer_options": ["Yes", "No", "Unknown"],
                "answer": "YOUR ANSWER GOES HERE"
            }
            
            if len(str(questions_json)) > 2000:
                return prev_valid_json 

            prev_valid_json = dict(questions_json)
            
            counter_i += 1
    return questions_json


def create_prompt(story, base_event, target_events, relation_category):
    question_j = build_relation_questions(base_event, target_events, relation_category)
    prompt = ""
    if relation_category == "Causal and Functional":
        prompt = prompt_causal_functional.format(
            story=story,
            question_json=question_j)
            
    elif relation_category == "Temporal":
        prompt = prompt_temporal.format(
            story=story,
            question_json=question_j)
            
    elif relation_category == "Structural":
        prompt = prompt_structural.format(
            story=story,
            question_json=question_j)
            
    return prompt
    
    
def extract_positive_relations(json_str, existing_dict=None):
    if existing_dict is None:
        existing_dict = {}
        
    # Convert string to dictionary
    data = ast.literal_eval(json_str)
    
    # Iterate over each relation category
    for relation_category in data:
        relation_label = relation_category.split()[0]  # e.g., "SUBEVENT", "SAME"
        for _, item in data[relation_category].items():
            if item["answer"] == "Yes":
                base_e = item['base_event']
                target_e = item['target_event']
                key = f"{base_e}#{target_e}"
                if key in existing_dict:
                    if relation_label not in existing_dict[key]:
                        existing_dict[key].append(relation_label)
                else:
                    existing_dict[key] = [relation_label]
                    
    return existing_dict

def parse_timed_event_string(timed_str):
        lines = timed_str.strip().split("\n")
        event_dict = {}
        current_time = None

        for line in lines:
            line = line.strip()
            time_match = re.match(r"^\d+\.\s*Time\s+(\d+)", line)
            if time_match:
                current_time = int(time_match.group(1))
                event_dict[current_time] = []
            elif line.startswith("-") and current_time is not None:
                event = line[1:].strip()
                event_dict[current_time].append(event)
        return event_dict
        
def generate_questions(event_dict):
    questions = []
    sorted_times = sorted(event_dict.keys())
    counter = 1

    for i, t1 in enumerate(sorted_times):
        for e1 in event_dict[t1]:
            for t2 in sorted_times[i + 1:]:
                for e2 in event_dict[t2]:
                    q = (
                        f"{counter}. What is the causal-functional relation from event "
                        f"[{e1}] to event [{e2}]? "
                        f"Choose one: [NONE, MOTIVATE, CAUSE, ENABLE, PREVENT]"
                    )
                    questions.append(q)
                    counter += 1
    return "\n\n".join(questions)
    
def generate_temporal_relations(time_dict):
    relation_dict = {}
    times = sorted(time_dict.keys())
    for i, t1 in enumerate(times):
        for e1 in time_dict[t1]:
            for e2 in time_dict[t1]:
                if e1 != e2:
                    if f"{e1}#{e2}" not in relation_dict:
                        relation_dict[f"{e1}#{e2}"] = ["SYNCHRONOUS"]
                    else:
                      relation_dict[f"{e1}#{e2}"].append("SYNCHRONOUS")
            for t2 in times[i+1:]:
                for e2 in time_dict[t2]:
                    if f"{e1}#{e2}" not in relation_dict:
                        relation_dict[f"{e1}#{e2}"] = ["BEFORE"]
                    else:
                      relation_dict[f"{e1}#{e2}"].append("BEFORE")
    return relation_dict

def parse_causal_relations(causal_output, existing_relations):
    lines = [line.strip() for line in causal_output.strip().split("\n") if line.strip()]
    temp_key = None

    for line in lines:
        if re.match(r'^\d+\.', line):
            # Step 3: Extract the events and build the key
            match_ = re.search(r'\[([^\]]+)\] to event \[([^\]]+)\]', line)
            if match_:
                e1, e2 = match_.group(1), match_.group(2)
                temp_key = f"{e1}#{e2}"
        else:
            # Step 4: Parse the answer and update dictionary
            match_ = re.search(r'Answer:\s*(\w+)', line)
            if match_ and temp_key:
                relation = match_.group(1)
                if relation != "NONE":
                    if temp_key not in existing_relations:
                        existing_relations[temp_key] = [relation]
                    else:
                      existing_relations[temp_key].append(relation)
                temp_key = None  # Reset for the next pair

    return existing_relations
    
    
def build_combined_relation_dict(story, phrases, model_name):
    events = "\n".join([f"{i+1}. {event}" for i, event in enumerate(phrases)])
    prompt_temporal = prompt_temporal2.format(story=story,  events=events)
    out_temporal = query_models(prompt_temporal, model_name)

    questions = generate_questions(parse_timed_event_string(out_temporal.strip()))

    prompt_causal = prompt_causal_functional2.format(story=story,  questions=questions)
    out_causal = query_models(prompt_causal, model_name)

    relation_dict = generate_temporal_relations(parse_timed_event_string(out_temporal.strip()))
    relation_dict = parse_causal_relations(out_causal.strip(), relation_dict)



    return relation_dict
    
    


def extract_influences(text, phrase_list):
    influence_dict = {}
    
    lines = text.strip().splitlines()
    
    current_target_event = None
    in_classification = False
    
    for line in lines:
        line = line.strip()

        # --- Start of a new question ---
        if "What previous events influenced the occurrence of this event, and what type of influence did they have" in line:
            current_target_event = None
            in_classification = False
            continue

        # --- Target Event ---
        if "Target Event" in line:
            parts = line.split(":", 1)
            if len(parts) > 1:
                current_target_event = parts[1].strip()

            continue

        
        # --- Start of Classification Block ---
        if "Step 2 - Classification" in line:
            in_classification = True
            continue


        # --- Process Classification Lines ---
        if in_classification and ':' in line:
            relation, phrases = line.split(":", 1)
            relation = relation.strip()
            if "-" in relation:
              relation = relation.replace("-", "").strip()
            relation = relation.lower()
            if relation not in {"cause", "motivate", "enable", "prevent"}:
                continue

            for phrase in phrases.split(','):
                clean_phrase = re.sub(r'\s*\(.*?\)', '', phrase).strip()
                if clean_phrase in phrase_list and current_target_event and clean_phrase != current_target_event:
                    key = f"{clean_phrase}#{current_target_event}"
                    if key not in influence_dict:
                        influence_dict[key] = []
                    if relation not in influence_dict[key]:
                        influence_dict[key].append(relation)

    return influence_dict
    
def get_COT_relations(story, phrases, model_name):
    ph = "\n".join(f"- {ev.strip()}" for ev in phrases)
    prompt = Prompt_causal2_CoT.format(story=story, events=ph)
    out_relations = query_models(prompt, model_name)
    
    relation_dict = extract_influences(out_relations, phrases)
    
    return relation_dict
    
    
def extract_influences_v2(text, phrase_list):
    influence_dict = {}

    lines = text.strip().splitlines()
    
    current_target_event = None
    current_influencing_event = None
    in_question = False
    in_relations_block = False

    for line in lines:
        line = line.strip()

        # --- Detect new question ---
        if "What previous events influenced the occurrence of this event, and what type of influence did they have" in line:
            current_target_event = None
            current_influencing_event = None
            in_question = True
            in_relations_block = False
            continue

        # --- Target Event ---
        if "Target Event" in line:
            parts = line.split(":", 1)
            if len(parts) > 1:
                current_target_event = parts[1].strip()
            continue

        # --- Start of new influencing event ---
        if "Influencing event" in line:
            current_influencing_event = line.split(":")[1].strip()
            in_relations_block = False  # reset
            continue

        # --- Start of relation labels block ---
        if "Relation Labels" in line:
            in_relations_block = True
            continue

        # --- Collect relation labels ---
        if in_relations_block and "relation:" in line:
            label = line.split(":")[1].strip()

            if (
                current_influencing_event 
                and current_target_event 
                and current_influencing_event in phrase_list 
                and current_target_event in phrase_list
                and current_influencing_event != current_target_event
            ):
                key = f"{current_influencing_event}#{current_target_event}"
                if key not in influence_dict:
                    influence_dict[key] = []
                influence_dict[key].append(label)

    return influence_dict
    
    
def get_COT_open_relations(story, phrases, model_name):
    ph = "\n".join(f"- {ev.strip()}" for ev in phrases)
    prompt = Prompt_causal_CoT_open.format(story=story, events=ph)
    out_relations = query_models(prompt, model_name)
    
    relation_dict = extract_influences_v2(out_relations, phrases)
    
    return relation_dict
    


def extract_influences_v3(text, phrase_list):
    influence_dict = {}

    lines = text.strip().splitlines()

    for line in lines:
        line = line.strip()

        if "triple:" not in line:
            continue

        # --- Extract triple content inside brackets ---
        triple_part = line.split("triple:")[1].strip()
        if triple_part.startswith("[") and triple_part.endswith("]"):
            parts = [p.strip() for p in triple_part[1:-1].split(",")]
            if len(parts) == 3:
                first_event, relation, second_event = parts
                relation = relation.lower()

                if (
                    first_event in phrase_list
                    and second_event in phrase_list
                    and first_event != second_event
                    and relation in {"cause", "motivate", "enable", "prevent"}
                ):
                    key = f"{first_event}#{second_event}"
                    if key not in influence_dict:
                        influence_dict[key] = []
                    influence_dict[key].append(relation)

    return influence_dict

def get_triples_relations(story, phrases, model_name):
    ph = "\n".join(f"- {ev.strip()}" for ev in phrases)
    prompt = Prompt_causal_triples.format(story=story, events=ph)
    out_relations = query_models(prompt, model_name)
    
    relation_dict = extract_influences_v3(out_relations, phrases)
    
    return relation_dict


def few_shot_events_block():
    return "\n".join(
        ["Story: "+ ex["story"] + "\nEvents:\n" + json.dumps(ex["events"], ensure_ascii=False, indent=2)
         for ex in FEW_SHOT_EVENTS]
    )

def few_shot_relations_block():
    return "\n".join(
        ["Events:\n"+json.dumps(ex["events"],ensure_ascii=False,indent=2)+
         "\nRelations:\n"+json.dumps(ex["relations"],ensure_ascii=False,indent=2)
         for ex in FEW_SHOT_RELATIONS]
    )
    
    
def manual_parse_event_json(text):
    lines = text.strip().splitlines()
    
    result = []
    current_event = {}
    inside_arguments = False
    current_arguments = {}

    for line in lines:
        line = line.strip().rstrip(',')

        if line.startswith('{'):
            current_event = {}
            current_arguments = {}
            inside_arguments = False
            continue

        elif line.startswith('"id"'):
            try:
                current_event["id"] = line.split(":", 1)[1].strip().strip('"')
            except Exception:
                current_event["id"] = "UNKNOWN_ID"

        elif line.startswith('"trigger"'):
            try:
                current_event["trigger"] = line.split(":", 1)[1].strip().strip('"')
            except Exception:
                current_event["trigger"] = "UNKNOWN_TRIGGER"

        elif line.startswith('"type"'):
            try:
                current_event["type"] = line.split(":", 1)[1].strip().strip('"')
            except Exception:
                pass

        elif line.startswith('"arguments"'):
            inside_arguments = True
            current_arguments = {}
            continue

        elif inside_arguments and line.startswith('}'):
            inside_arguments = False
            current_event["arguments"] = current_arguments
            continue

        elif inside_arguments:
            try:
                key, val = line.split(":", 1)
                key = key.strip().strip('"')
                val = val.strip().strip('"')
                current_arguments[key] = val
            except Exception:
                continue

        elif line.startswith('}'):
            if "id" in current_event and "trigger" in current_event:
                if "arguments" not in current_event:
                    current_event["arguments"] = current_arguments if current_arguments else {}
                result.append(current_event)
            current_event = {}
            current_arguments = {}
            inside_arguments = False

    return result


def extract_event_data(event_json_str):
    # Clean up the string
    clean_str = event_json_str.replace("<JSON>", "").replace("</JSON>", "").strip()
    try: 
        data = json.loads(clean_str)
    except:
        try: 
            data = manual_parse_event_json(clean_str)
        except:
            return [], {}
    
    # Extract event IDs
    try: 
        ids = [event["trigger"].strip() for event in data if "trigger" in event]
    except:
        return [], {}
    
    # Create dictionary with id as key and rest as value
    id_to_event = {}
    for event in data:
        if "id" in event:
            id_to_event[event["id"].strip()] = {}
            if "trigger" in event:
                id_to_event[event["id"].strip()]["trigger"] = event["trigger"].strip()
            if "type" in event:
                id_to_event[event["id"].strip()]["type"] = event["type"].strip()
            if "arguments" in event:
                id_to_event[event["id"].strip()]["arguments"] = event["arguments"]
    
    return ids, id_to_event
    
    
def manual_parse_relation_json(text):
    lines = text.strip().splitlines()
    
    result = []
    current_rel = {}

    for line in lines:
        line = line.strip().rstrip(',')

        if line.startswith('{'):
            current_rel = {}
            continue

        elif line.startswith('"type"'):
            try:
                current_rel["type"] = line.split(":", 1)[1].strip().strip('"')
            except Exception:
                continue

        elif line.startswith('"source"'):
            try:
                current_rel["source"] = line.split(":", 1)[1].strip().strip('"')
            except Exception:
                continue

        elif line.startswith('"target"'):
            try:
                current_rel["target"] = line.split(":", 1)[1].strip().strip('"')
            except Exception:
                continue

        elif line.startswith('}'):
            if all(k in current_rel for k in ("type", "source", "target")):
                result.append(current_rel)
            current_rel = {}

    return result
    
    
def extract_relation_map(relation_json_str, id_to_event):
    # Clean up the string
    clean_str = relation_json_str.replace("<JSON>", "").replace("</JSON>", "").strip()
    try:
        data = json.loads(clean_str)
    except:
        try: 
            data = manual_parse_relation_json(clean_str)
        except:
            return {}

    relation_dict = {}
    
    for relation in data:
        if "source" in relation and relation["source"].strip() in id_to_event and "trigger" in id_to_event[relation["source"].strip()]:
            key_part1 = id_to_event[relation["source"].strip()]["trigger"]
        else:
            key_part1 = None
        if "target" in relation and relation["target"].strip() in id_to_event and "trigger" in id_to_event[relation["target"].strip()]:
            key_part2 = id_to_event[relation["target"].strip()]["trigger"]
        else:
            key_part2 = None
        
        if key_part1 is None or key_part2 is None:
            continue
        if "type" not in relation:
            continue
        
        key = f'{key_part1}#{key_part2}'
        if key not in relation_dict:
            relation_dict[key] = []
        if relation["type"].strip() not in relation_dict[key]:
          relation_dict[key].append(relation["type"].strip())
    
    return relation_dict
    
def extract_events_relations(story, model_name):
    prompt_event = EVENT_PROMPT_TEMPLATE.format(few_shots=few_shot_events_block(), story=story)
    out_event = query_models(prompt_event, model_name)
    
    prompt_rel = REL_PROMPT_TEMPLATE.format(few_shots=few_shot_relations_block(), story=story, events=out_event)
    out_rel = query_models(prompt_rel, model_name)
    
    ids, id_to_event = extract_event_data(out_event)
    relation_dict = extract_relation_map(out_rel, id_to_event)
    
    return ids, relation_dict