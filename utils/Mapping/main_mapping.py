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


random.seed(309)

from utils.Mapping.helper_function import *
from utils.Mapping.mappings import *
from utils.Mapping.beam_search import *
from utils.helper_utils import *

# from utils.Mapping.helper_function import get_embedding_model
# from utils.Mapping.mappings import get_all_possible_pairs_map
# from utils.Mapping.beam_search import 
# from utils.helper_utils import 


PATH_DATASET = "Data/Datasets/"
PATH_UNITS = "Data_new/Units/"
PATH_ABSTRACTION = "Data_new/Abstraction/"

RESULTS_DIR = "results/"
os.makedirs(RESULTS_DIR, exist_ok=True)
RESULTS_PATH = RESULTS_DIR + "results.csv"

os.makedirs("Graphs_pic", exist_ok=True)
    
def compute_max_and_total_scores(solutions):
    max_score = -np.inf
    total_score = -np.inf

    for sol in solutions:
        coverage_sum = sum(sol['coverage'])
        sc = round(sol['score'] / coverage_sum, 3) if coverage_sum > 0 else 0

        if sc > max_score:
            max_score = sc

        if sol['score'] > total_score:
            total_score = sol['score']

    return round(max_score, 3), round(total_score, 3)

def build_embedding_cache(embedding_model, texts, batch_size=1024, normalize=True, to_numpy=True, show_progress=True):
    with torch.inference_mode():
        embs = embedding_model.encode(
            texts,
            batch_size=batch_size,
            convert_to_tensor=True,
            show_progress_bar=show_progress,
            normalize_embeddings=False,  # we'll handle below for portability
        )

    if normalize:
        embs = normalize_embeddings(embs)  # L2 normalize for cosine=dot

    embs = embs.cpu().numpy() if to_numpy else embs.cpu()

    return dict(zip(texts, embs))

def build_nli_cache(pairs, tok, nli, batch_size=256):
    cache = {}
    device = next(nli.parameters()).device

    expanded_pairs = []

    for a, b in pairs:
        expanded_pairs.append((a, b))
        expanded_pairs.append((b, a))

    expanded_pairs = list(dict.fromkeys(expanded_pairs))

    for start in tqdm(range(0, len(expanded_pairs), batch_size), desc="Building NLI cache"):
        batch = expanded_pairs[start:start + batch_size]

        premises = [a for a, b in batch]
        hypotheses = [b for a, b in batch]

        inputs = tok(
            premises,
            hypotheses,
            return_tensors="pt",
            padding=True,
            truncation=True
        ).to(device)

        with torch.no_grad():
            probs = torch.softmax(
                nli(**inputs).logits,
                dim=-1
            )

        for pair, prob in zip(batch, probs):
            cache[pair] = tuple(prob.tolist())

    return cache

def get_unit_events(unit):
    """Return event texts regardless of whether unit is a list or dict."""
    return list(unit.keys()) if isinstance(unit, dict) else list(unit)

def extract_story_units(main_data, main_units, args):
    all_stories_events = {}
    nli_pairs = []

    for index in tqdm(range(len(main_data)), desc="Extracting unique units"):
        sample_unit = main_units[index]

        base_unit = get_unit_events(sample_unit["base"])
        target_keys = sorted(key for key in sample_unit if key.startswith("target"))

        for target_key in target_keys:
            target_unit = get_unit_events(sample_unit[target_key])
            all_stories_events, nli_pairs = pairs_update(get_all_possible_pairs_map(base_unit, target_unit), [sample_unit["base"], sample_unit[target_key]], all_stories_events, nli_pairs, args)

    return all_stories_events, nli_pairs

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

def fit_mahalanobis_from_dict(embedding_dict):
    X = np.asarray(
        np.stack(list(embedding_dict.values())),
        dtype=np.float64
    )

    estimator = LedoitWolf().fit(X)

    # precision_ = inverse covariance matrix
    return estimator.precision_


def Greedy_mapping(main_data, main_units, embedding_model, nli_model, nli_token, args):

    all_stories_events, nli_pairs = extract_story_units(main_data, main_units, args)
    unique_values = list(dict.fromkeys(chain.from_iterable(all_stories_events.values())))

    if args.scoring_method == "mahalanobis":
        embedding_dicts = build_embedding_cache(embedding_model, unique_values, batch_size=1024, normalize=False, to_numpy=True, show_progress=True)
        VI = fit_mahalanobis_from_dict(embedding_dicts)
        nli_cache = None
    elif args.scoring_method == "nli":
        embedding_dicts = build_embedding_cache(embedding_model, unique_values)
        VI = None
        nli_pairs = list(dict.fromkeys(nli_pairs))
        nli_cache = build_nli_cache(nli_pairs, nli_token, nli_model)

    else:
        embedding_dicts = build_embedding_cache(embedding_model, unique_values)
        VI = None
        nli_cache = None

    


    y_true = []
    y_pred = []
    category_dict_ref = {'low-near': 294, 'low-far': 294, 'high-near': 253, 'high-far': 254}
    category_dict = {'low-near': 0, 'low-far': 0, 'high-near': 0, 'high-far': 0}

    for index in tqdm(range(len(main_data)), desc="Mapping process"):
        sample_unit = main_units[index]
        base_unit = get_unit_events(sample_unit["base"])

        correct_answer, category = get_correct_answer(main_data, index, args)
        y_true.append(correct_answer)

        target_keys = sorted(key for key in sample_unit if key.startswith("target"))

        total_scores = []

        for target_key in target_keys:
            target_unit = get_unit_events(sample_unit[target_key])

            current_maps = generate_local_mappings(get_all_possible_pairs_map(base_unit, target_unit), all_stories_events, embedding_dicts, main_units, VI, nli_cache, args)
            current_final_solutions = beam_search(base_unit, target_unit, current_maps, args.config["top_output"])
            current_max_score, current_total_score = compute_max_and_total_scores(current_final_solutions)

            total_scores.append(current_total_score)
                

        max_index = random.choice([i for i, val in enumerate(total_scores) if val == max(total_scores)])
        y_pred.append(max_index)

        if args.dataset == "ARN" and y_true[-1] == y_pred[-1]:
            category_dict[category] += 1
    

    result = round(metrics.accuracy_score(y_true, y_pred), 2)

    if args.dataset == "ARN":
        for key in category_dict:
            category_dict[key] = round(category_dict[key]/category_dict_ref[key], 2)
        return result, category_dict 
    elif args.dataset == "MCQ":
        return result, "-"

##### Mapping Linear

def Linear_mapping(main_data, main_units, embedding_model, nli_model, nli_token, args):

    all_stories_events, nli_pairs = extract_story_units(main_data, main_units, args)
    unique_values = list(dict.fromkeys(chain.from_iterable(all_stories_events.values())))

    if args.scoring_method == "mahalanobis":
        embedding_dicts = build_embedding_cache(embedding_model, unique_values, batch_size=1024, normalize=False, to_numpy=True, show_progress=True)
        VI = fit_mahalanobis_from_dict(embedding_dicts)
        nli_cache = None

    elif args.scoring_method == "nli":
        embedding_dicts = build_embedding_cache(embedding_model, unique_values)
        VI = None
        nli_pairs = list(dict.fromkeys(nli_pairs))
        nli_cache = build_nli_cache(nli_pairs, nli_token, nli_model)

    else:
        embedding_dicts = build_embedding_cache(embedding_model, unique_values)
        VI = None
        nli_cache = None

    y_true = []
    y_pred = []

    category_dict_ref = {"low-near": 294, "low-far": 294, "high-near": 253, "high-far": 254}
    category_dict = {"low-near": 0, "low-far": 0, "high-near": 0, "high-far": 0}

    for index in tqdm(range(len(main_data)), desc="Linear positional mapping"):

        sample_unit = main_units[index]
        base_unit = list(get_unit_events(sample_unit["base"]))

        assert len(base_unit) > 0, f"Empty base story at sample {index}"

        correct_answer, category = get_correct_answer(main_data, index, args)
        y_true.append(correct_answer)

        target_keys = sorted((key for key in sample_unit if key.startswith("target")), key=lambda key: int(key.replace("target", "")))

        assert len(target_keys) > 0, f"No target stories at sample {index}"
        assert 0 <= correct_answer < len(target_keys), f"Invalid answer {correct_answer} at sample {index}"

        total_scores = []

        for target_key in target_keys:

            target_unit = list(get_unit_events(sample_unit[target_key]))

            assert len(target_unit) > 0, f"Empty {target_key} at sample {index}"

            number_of_mappings = min(len(base_unit), len(target_unit))

            assert number_of_mappings > 0, f"No mapping at sample {index}, target {target_key}"

            if number_of_mappings == 0:
                total_scores.append(-10.0)
                continue

            mapping_scores = []

            for position in range(number_of_mappings):

                base_event = base_unit[position]
                target_event = target_unit[position]

                base_values = score_pair([base_event], sample_unit["base"], args)
                target_values = score_pair([target_event], sample_unit[target_key], args)

                assert base_values is not None, f"score_pair returned None for base event '{base_event}' at sample {index}"
                assert target_values is not None, f"score_pair returned None for target event '{target_event}' at sample {index}"
                assert len(base_values) > 0, f"No scoring units for base event '{base_event}' at sample {index}"
                assert len(target_values) > 0, f"No scoring units for target event '{target_event}' at sample {index}"

                if len(base_values) != len(target_values):
                    print(f"Warning: representation-length mismatch at sample {index}, target {target_key}, position {position}: {len(base_values)} vs {len(target_values)}")

                number_of_values = min(len(base_values), len(target_values))

                if number_of_values == 0:
                    mapping_scores.append(-10.0)
                    continue

                base_values = base_values[:number_of_values]
                target_values = target_values[:number_of_values]

                missing_values = list(dict.fromkeys([value for value in base_values + target_values if value not in embedding_dicts]))

                if missing_values:
                    normalize_missing = args.scoring_method != "mahalanobis"
                    missing_embeddings = embedding_model.encode(missing_values, normalize_embeddings=normalize_missing, convert_to_numpy=True, show_progress_bar=False)
                    embedding_dicts.update(dict(zip(missing_values, missing_embeddings)))

                B_local = np.stack([embedding_dicts[value] for value in base_values])
                T_local = np.stack([embedding_dicts[value] for value in target_values])

                assert np.all(np.isfinite(B_local)), f"Invalid base embedding at sample {index}, target {target_key}, position {position}"
                assert np.all(np.isfinite(T_local)), f"Invalid target embedding at sample {index}, target {target_key}, position {position}"

                if args.scoring_method == "mahalanobis":
                    local_score = final_mahalanobis_similarity(B_local, T_local, VI)

                elif args.scoring_method == "nli":
                    nli_scores = []

                    for value_index in range(number_of_values):

                        base_value = base_values[value_index]
                        target_value = target_values[value_index]
                        pair = (base_value, target_value)

                        if pair not in nli_cache:
                            new_nli_cache = build_nli_cache([pair], nli_token, nli_model, batch_size=1)
                            nli_cache.update(new_nli_cache)

                        p_contra, p_neutral, p_ent = nli_cache[pair]

                        assert np.all(np.isfinite([p_contra, p_neutral, p_ent])), f"Invalid NLI probabilities for pair {pair} at sample {index}"
                        assert np.isclose(p_contra + p_neutral + p_ent, 1.0, atol=1e-4), f"NLI probabilities do not sum to one for pair {pair}"

                        raw_cosine = float(np.dot(B_local[value_index], T_local[value_index]))
                        soft_sign = p_ent + p_neutral - p_contra
                        nli_score = raw_cosine * soft_sign

                        assert np.isfinite(nli_score), f"Invalid NLI score for pair {pair} at sample {index}"

                        nli_scores.append(nli_score)

                    local_score = float(np.min(nli_scores)) if nli_scores else -10.0

                else:
                    local_score = float(np.mean(np.sum(B_local * T_local, axis=1)))

                assert np.isfinite(local_score), f"Invalid local score at sample {index}, target {target_key}, position {position}"

                mapping_scores.append(local_score)

            current_total_score = float(np.mean(mapping_scores)) if mapping_scores else -10.0


            assert np.isfinite(current_total_score), f"Invalid total score at sample {index}, target {target_key}"

            total_scores.append(current_total_score)

        assert len(total_scores) == len(target_keys), f"Missing target scores at sample {index}"
        assert np.all(np.isfinite(total_scores)), f"Invalid candidate scores at sample {index}"

        max_score = max(total_scores)
        max_indices = [i for i, value in enumerate(total_scores) if np.isclose(value, max_score)]

        assert len(max_indices) > 0, f"No valid prediction at sample {index}"

        max_index = random.choice(max_indices)
        y_pred.append(max_index)
    
        if args.dataset == "ARN" and y_true[-1] == y_pred[-1]:
            assert category in category_dict, f"Unknown category '{category}' at sample {index}"
            category_dict[category] += 1

    result = round(metrics.accuracy_score(y_true, y_pred), 2)

    if args.dataset == "ARN":
        for key in category_dict:
            category_dict[key] = round(category_dict[key] / category_dict_ref[key], 2)

        return result, category_dict

    elif args.dataset == "MCQ":
        return result, "-"

######## Mapping Role_constrained

def align_units_with_roles(units, arc_story):
    valid_roles = {"TP1", "TP2", "TP3", "TP4", "TP5"}
    return [(unit, arc_story[unit]) for unit in units if unit in arc_story and arc_story[unit] in valid_roles]


def get_role_position_mappings(base_units, target_units, base_arc, target_arc, target_key):
    role_order = ["TP1", "TP2", "TP3", "TP4", "TP5"]

    base_with_roles = align_units_with_roles(base_units, base_arc)
    target_with_roles = align_units_with_roles(target_units, target_arc)

    base_by_role = {role: [] for role in role_order}
    target_by_role = {role: [] for role in role_order}

    for unit, role in base_with_roles:
        base_by_role[role].append(unit)

    for unit, role in target_with_roles:
        target_by_role[role].append(unit)

    mappings = []

    for role in role_order:
        number_of_mappings = min(len(base_by_role[role]), len(target_by_role[role]))

        for position in range(number_of_mappings):
            mappings.append((base_by_role[role][position], target_by_role[role][position], role))

    return mappings


def Role_constrained_mapping(main_data, main_units, main_arc_units, embedding_model, nli_model, nli_token, args):
    all_stories_events, nli_pairs = extract_story_units(main_data, main_units, args)
    unique_values = list(dict.fromkeys(chain.from_iterable(all_stories_events.values())))

    if args.scoring_method == "mahalanobis":
        embedding_dicts = build_embedding_cache(embedding_model, unique_values, batch_size=1024, normalize=False, to_numpy=True, show_progress=True)
        VI = fit_mahalanobis_from_dict(embedding_dicts)
        nli_cache = None

    elif args.scoring_method == "nli":
        embedding_dicts = build_embedding_cache(embedding_model, unique_values)
        VI = None
        nli_pairs = list(dict.fromkeys(nli_pairs))
        nli_cache = build_nli_cache(nli_pairs, nli_token, nli_model)

    else:
        embedding_dicts = build_embedding_cache(embedding_model, unique_values)
        VI = None
        nli_cache = None

    y_true = []
    y_pred = []

    category_dict_ref = {"low-near": 294, "low-far": 294, "high-near": 253, "high-far": 254}
    category_dict = {"low-near": 0, "low-far": 0, "high-near": 0, "high-far": 0}

    empty_target_mappings = 0
    empty_sample_mappings = 0

    for index in tqdm(range(len(main_data)), desc="Role-constrained positional mapping"):
        sample_unit = main_units[index]
        sample_arc = main_arc_units[index]

        base_unit = list(get_unit_events(sample_unit["base"]))

        correct_answer, category = get_correct_answer(main_data, index, args)
        y_true.append(correct_answer)

        target_keys = sorted(key for key in sample_unit if key.startswith("target"))
        total_scores = []

        for target_key in target_keys:
            target_unit = list(get_unit_events(sample_unit[target_key]))

            role_mappings = get_role_position_mappings(base_unit, target_unit, sample_arc["base"], sample_arc[target_key], target_key)

            if not role_mappings:
                empty_target_mappings += 1
                total_scores.append(-np.inf)
                continue

            mapping_scores = []

            for base_event, target_event, role in role_mappings:
                base_values = score_pair([base_event], sample_unit["base"], args)
                target_values = score_pair([target_event], sample_unit[target_key], args)

                if base_values is None or target_values is None:
                    raise ValueError(f"score_pair returned None at sample {index}, target {target_key}, role {role}.")

                number_of_values = min(len(base_values), len(target_values))

                if number_of_values == 0:
                    raise ValueError(f"No scoring values at sample {index}, target {target_key}, role {role}.")

                base_values = base_values[:number_of_values]
                target_values = target_values[:number_of_values]

                missing_values = list(dict.fromkeys([value for value in base_values + target_values if value not in embedding_dicts]))

                if missing_values:
                    normalize_missing = args.scoring_method != "mahalanobis"
                    missing_embeddings = embedding_model.encode(missing_values, normalize_embeddings=normalize_missing, convert_to_numpy=True, show_progress_bar=False)
                    embedding_dicts.update(dict(zip(missing_values, missing_embeddings)))

                B_local = np.stack([embedding_dicts[value] for value in base_values])
                T_local = np.stack([embedding_dicts[value] for value in target_values])

                if args.scoring_method == "mahalanobis":
                    local_score = final_mahalanobis_similarity(B_local, T_local, VI)

                elif args.scoring_method == "nli":
                    nli_scores = []

                    for value_index in range(number_of_values):
                        base_value = base_values[value_index]
                        target_value = target_values[value_index]
                        pair = (base_value, target_value)

                        if pair not in nli_cache:
                            new_nli_cache = build_nli_cache([pair], nli_token, nli_model, batch_size=1)
                            nli_cache.update(new_nli_cache)

                        p_contra, p_neutral, p_ent = nli_cache[pair]
                        raw_cosine = float(np.dot(B_local[value_index], T_local[value_index]))
                        soft_sign = p_ent + p_neutral - p_contra
                        nli_score = raw_cosine * soft_sign
                        nli_scores.append(nli_score)

                    local_score = float(np.min(nli_scores))

                else:
                    local_score = float(np.mean(np.sum(B_local * T_local, axis=1)))

                if not np.isfinite(local_score):
                    raise ValueError(f"Invalid local score at sample {index}, target {target_key}, role {role}: {local_score}")

                mapping_scores.append(local_score)

            current_total_score = float(np.mean(mapping_scores))
            total_scores.append(current_total_score)

        if not total_scores:
            raise ValueError(f"No target stories at sample {index}.")

        valid_scores = [score for score in total_scores if np.isfinite(score)]

        if not valid_scores:
            empty_sample_mappings += 1
            max_index = random.randrange(len(target_keys))
        else:
            max_score = max(total_scores)
            max_indices = [i for i, score in enumerate(total_scores) if score == max_score]
            max_index = random.choice(max_indices)

        y_pred.append(max_index)

        if args.dataset == "ARN" and y_true[-1] == y_pred[-1]:
            category_dict[category] += 1

    print("Targets without shared TP roles:", empty_target_mappings)
    print("Samples without any valid TP mapping:", empty_sample_mappings)

    result = round(metrics.accuracy_score(y_true, y_pred), 2)

    if args.dataset == "ARN":
        for key in category_dict:
            category_dict[key] = round(category_dict[key] / category_dict_ref[key], 2)

        return result, category_dict

    elif args.dataset == "MCQ":
        return result, "-"


######## Mapping Global
def Global_assignment_mapping(main_data, main_units, embedding_model, nli_model, nli_token, args):
    all_stories_events, nli_pairs = extract_story_units(main_data, main_units, args)
    unique_values = list(dict.fromkeys(chain.from_iterable(all_stories_events.values())))

    if args.scoring_method == "mahalanobis":
        embedding_dicts = build_embedding_cache(embedding_model, unique_values, batch_size=1024, normalize=False, to_numpy=True, show_progress=True)
        VI = fit_mahalanobis_from_dict(embedding_dicts)
        nli_cache = None

    elif args.scoring_method == "nli":
        embedding_dicts = build_embedding_cache(embedding_model, unique_values)
        VI = None
        nli_pairs = list(dict.fromkeys(nli_pairs))
        nli_cache = build_nli_cache(nli_pairs, nli_token, nli_model)

    else:
        embedding_dicts = build_embedding_cache(embedding_model, unique_values)
        VI = None
        nli_cache = None

    y_true = []
    y_pred = []

    category_dict_ref = {"low-near": 294, "low-far": 294, "high-near": 253, "high-far": 254}
    category_dict = {"low-near": 0, "low-far": 0, "high-near": 0, "high-far": 0}

    tie_count = 0

    for index in tqdm(range(len(main_data)), desc="Global assignment mapping"):
        sample_unit = main_units[index]
        base_unit = list(get_unit_events(sample_unit["base"]))

        if not base_unit:
            raise ValueError(f"Base story has no units at sample {index}.")

        correct_answer, category = get_correct_answer(main_data, index, args)
        y_true.append(correct_answer)

        target_keys = sorted(key for key in sample_unit if key.startswith("target"))

        if not target_keys:
            raise ValueError(f"No target stories at sample {index}.")

        total_scores = []

        for target_key in target_keys:
            target_unit = list(get_unit_events(sample_unit[target_key]))

            if not target_unit:
                total_scores.append(-np.inf)
                continue

            score_matrix = np.empty((len(base_unit), len(target_unit)), dtype=np.float64)

            for base_index, base_event in enumerate(base_unit):
                for target_index, target_event in enumerate(target_unit):
                    base_values = score_pair([base_event], sample_unit["base"], args)
                    target_values = score_pair([target_event], sample_unit[target_key], args)

                    if base_values is None or target_values is None:
                        raise ValueError(f"score_pair returned None at sample {index}, target {target_key}, edge ({base_index}, {target_index}).")

                    number_of_values = min(len(base_values), len(target_values))

                    if number_of_values == 0:
                        raise ValueError(f"No scoring values at sample {index}, target {target_key}, edge ({base_index}, {target_index}).")

                    base_values = base_values[:number_of_values]
                    target_values = target_values[:number_of_values]

                    missing_values = list(dict.fromkeys([value for value in base_values + target_values if value not in embedding_dicts]))

                    if missing_values:
                        normalize_missing = args.scoring_method != "mahalanobis"
                        missing_embeddings = embedding_model.encode(missing_values, normalize_embeddings=normalize_missing, convert_to_numpy=True, show_progress_bar=False)
                        embedding_dicts.update(dict(zip(missing_values, missing_embeddings)))

                    B_local = np.stack([embedding_dicts[value] for value in base_values])
                    T_local = np.stack([embedding_dicts[value] for value in target_values])

                    if args.scoring_method == "mahalanobis":
                        local_score = final_mahalanobis_similarity(B_local, T_local, VI)

                    elif args.scoring_method == "nli":
                        component_scores = []

                        for value_index in range(number_of_values):
                            base_value = base_values[value_index]
                            target_value = target_values[value_index]
                            pair = (base_value, target_value)

                            if pair not in nli_cache:
                                new_nli_cache = build_nli_cache([pair], nli_token, nli_model, batch_size=1)
                                nli_cache.update(new_nli_cache)

                            p_contra, p_neutral, p_ent = nli_cache[pair]
                            raw_cosine = float(np.dot(B_local[value_index], T_local[value_index]))
                            soft_sign = p_ent + p_neutral - p_contra
                            component_scores.append(raw_cosine * soft_sign)

                        local_score = float(np.mean(component_scores))

                    else:
                        local_score = float(np.mean(np.sum(B_local * T_local, axis=1)))

                    if not np.isfinite(local_score):
                        raise ValueError(f"Invalid local score at sample {index}, target {target_key}, edge ({base_index}, {target_index}): {local_score}")

                    score_matrix[base_index, target_index] = local_score

            if not np.all(np.isfinite(score_matrix)):
                raise ValueError(f"Score matrix contains non-finite values at sample {index}, target {target_key}.")

            row_indices, column_indices = linear_sum_assignment(score_matrix, maximize=True)
            selected_scores = score_matrix[row_indices, column_indices]
            expected_mappings = min(len(base_unit), len(target_unit))

            if len(selected_scores) != expected_mappings:
                raise ValueError(f"Incorrect assignment size at sample {index}, target {target_key}: expected {expected_mappings}, received {len(selected_scores)}.")

            current_total_score = float(np.mean(selected_scores))
            total_scores.append(current_total_score)

        valid_scores = [score for score in total_scores if np.isfinite(score)]

        if not valid_scores:
            raise ValueError(f"No valid target scores at sample {index}.")

        max_score = max(total_scores)
        max_indices = [i for i, score in enumerate(total_scores) if score == max_score]

        if len(max_indices) > 1:
            tie_count += 1

        y_pred.append(random.choice(max_indices))

        if args.dataset == "ARN" and y_true[-1] == y_pred[-1]:
            category_dict[category] += 1

    print("Global assignment ties:", tie_count)

    result = round(metrics.accuracy_score(y_true, y_pred), 2)

    print("y_pred: ", y_pred)
    dssddsdsdsds

    if args.dataset == "ARN":
        for key in category_dict:
            category_dict[key] = round(category_dict[key] / category_dict_ref[key], 2)

        return result, category_dict

    elif args.dataset == "MCQ":
        return result, "-"


###### GED

VALID_GED_VARIANTS = {"GED_events", "GED_conceptual", "GED_stage", "GED_events_full", "GED_conceptual_evaluative", "GED_conceptual_full", "GED_stage_arc"}
VALID_ARC_ROLES = {"TP1", "TP2", "TP3", "TP4", "TP5"}

def print_ged_graph(graph):
    print("\nNODES")

    for node_id, data in graph.nodes(data=True):
        print(f"{node_id}: type={data.get('type')}, text={data.get('text')}, position={data.get('position')}, role={data.get('role')}, values={data.get('values')}")

    print("\nEDGES")

    for source, target, data in graph.edges(data=True):
        print(f"{source} -> {target}: type={data.get('type')}")


def plot_ged_graph(graph, output_path, title="GED graph"):
    node_colors = {"event": "#4C78A8", "conceptual": "#72B7B2", "evaluative": "#F58518", "stage": "#54A24B", "arc": "#E45756"}
    colors = [node_colors.get(data.get("type"), "#B0B0B0") for _, data in graph.nodes(data=True)]
    labels = {node_id: f"{data.get('type')}\n{data.get('text', '')[:25]}" for node_id, data in graph.nodes(data=True)}
    edge_labels = {(source, target): data.get("type", "") for source, target, data in graph.edges(data=True)}
    attachment_targets = {target for source, target, data in graph.edges(data=True) if data.get("type") != "next"}
    layer_positions = {"conceptual": 1.5, "evaluative": -1.5, "stage": 3.0, "arc": -3.0}
    positions = {}

    for index, (node_id, data) in enumerate(graph.nodes(data=True)):
        node_position = data.get("position")

        if node_position is None:
            parent_positions = [graph.nodes[parent].get("position") for parent in graph.predecessors(node_id)]
            parent_positions = [position for position in parent_positions if position is not None]
            node_position = sum(parent_positions) / len(parent_positions) if parent_positions else index

        vertical_position = layer_positions.get(data.get("type"), 1.5) if node_id in attachment_targets else 0
        positions[node_id] = (node_position, vertical_position)

    plt.figure(figsize=(max(14, len(graph.nodes) * 2.5), 6))
    nx.draw_networkx_nodes(graph, positions, node_color=colors, node_size=2200, edgecolors="black")
    nx.draw_networkx_labels(graph, positions, labels=labels, font_size=7)
    nx.draw_networkx_edges(graph, positions, arrows=True, arrowstyle="-|>", arrowsize=25, min_source_margin=25, min_target_margin=25)
    nx.draw_networkx_edge_labels(graph, positions, edge_labels=edge_labels, font_size=7)
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print("saved as: ", output_path)


def get_ged_scoring_values(text, node_type, args):
    if text is None:
        return []

    text = str(text).strip()

    if not text:
        return []

    if node_type == "conceptual":
        text = text.replace("_", " ").lower()
        words = text.split()
        return [words[1] if len(words) > 1 else text]

    return [text]


def add_ged_node(graph, node_id, node_type, text, args, position=None, role=None):
    scoring_values = get_ged_scoring_values(text, node_type, args)

    if not scoring_values:
        return False

    graph.add_node(node_id, type=node_type, text=str(text), values=scoring_values, position=position, role=role)
    return True


def add_temporal_edges(graph, backbone_nodes):
    for position in range(len(backbone_nodes) - 1):
        graph.add_edge(backbone_nodes[position], backbone_nodes[position + 1], type="next")


def get_stage_items(stage_story):
    if not isinstance(stage_story, dict):
        return []

    stage_items = [(stage_text, role) for stage_text, role in stage_story.items() if role in VALID_ARC_ROLES]
    stage_items.sort(key=lambda item: int(item[1].replace("TP", "")))

    return stage_items


def add_shared_arc_and_stage_nodes(graph, backbone_event_nodes, arc_story, stage_story, args):
    arc_labels = {"TP1": "Introduction", "TP2": "Event", "TP3": "Challenge", "TP4": "Action", "TP5": "Conclusion"}
    stage_items = get_stage_items(stage_story)
    stage_values_by_role = {}
    arc_nodes_by_role = {}
    stage_nodes_by_role = {}

    for stage_index, (stage_text, role) in enumerate(stage_items):
        if role in VALID_ARC_ROLES:
            stage_values_by_role.setdefault(role, []).append((f"shared_stage_{stage_index}", stage_text))

    for backbone_node, event in backbone_event_nodes:
        role = arc_story.get(event)

        if role not in VALID_ARC_ROLES:
            continue

        if role not in arc_nodes_by_role:
            arc_node_id = f"shared_arc_{role}"
            arc_text = arc_labels[role]

            if add_ged_node(graph, arc_node_id, "arc", arc_text, args):
                arc_nodes_by_role[role] = arc_node_id

        if role in arc_nodes_by_role:
            graph.add_edge(backbone_node, arc_nodes_by_role[role], type="has_arc")

        for stage_node_id, stage_text in stage_values_by_role.get(role, []):
            if stage_node_id not in graph:
                if add_ged_node(graph, stage_node_id, "stage", stage_text, args):
                    stage_nodes_by_role.setdefault(role, []).append(stage_node_id)

            if stage_node_id in graph:
                graph.add_edge(backbone_node, stage_node_id, type="has_stage")

def timeline_sort_key(event, timeline_story):
    try:
        return int(str(timeline_story.get(event, "")).strip())
    except (TypeError, ValueError):
        return float("inf")

def build_ged_graph(events_story, conceptual_story, evaluative_story, arc_story, stage_story, timeline_story, graph_variant, args):
    if graph_variant not in VALID_GED_VARIANTS:
        raise ValueError(f"Unknown GED graph variant: {graph_variant}")

    events_story = list(events_story) if events_story is not None else []
    conceptual_story = conceptual_story if isinstance(conceptual_story, dict) else {}
    evaluative_story = evaluative_story if isinstance(evaluative_story, dict) else {}
    arc_story = arc_story if isinstance(arc_story, dict) else {}
    stage_story = stage_story if isinstance(stage_story, dict) else {}
    timeline_story = timeline_story if isinstance(timeline_story, dict) else {}

    if args.config.get("timeline", False) in (True, "true"):
        events_story.sort(key=lambda event: timeline_sort_key(event, timeline_story))

    graph = nx.DiGraph()

    if graph_variant == "GED_events":
        backbone_nodes = []

        for event_index, event in enumerate(events_story):
            event_node_id = f"event_{event_index}"

            if add_ged_node(graph, event_node_id, "event", event, args, position=event_index):
                backbone_nodes.append(event_node_id)

        add_temporal_edges(graph, backbone_nodes)

    elif graph_variant == "GED_conceptual":
        backbone_nodes = []

        for event_index, event in enumerate(events_story):
            conceptual_text = conceptual_story.get(event)

            if conceptual_text is None:
                continue

            conceptual_node_id = f"conceptual_{event_index}"

            if add_ged_node(graph, conceptual_node_id, "conceptual", conceptual_text, args, position=event_index):
                backbone_nodes.append(conceptual_node_id)

        add_temporal_edges(graph, backbone_nodes)

    elif graph_variant == "GED_stage":
        backbone_nodes = []

        for stage_index, (stage_text, role) in enumerate(get_stage_items(stage_story)):
            stage_node_id = f"stage_{stage_index}"

            if add_ged_node(graph, stage_node_id, "stage", stage_text, args, position=stage_index):
                backbone_nodes.append(stage_node_id)

        add_temporal_edges(graph, backbone_nodes)

    elif graph_variant == "GED_events_full":
        backbone_nodes = []
        backbone_event_nodes = []

        for event_index, event in enumerate(events_story):
            event_node_id = f"event_{event_index}"

            if not add_ged_node(graph, event_node_id, "event", event, args, position=event_index):
                continue

            backbone_nodes.append(event_node_id)
            backbone_event_nodes.append((event_node_id, event))

            conceptual_text = conceptual_story.get(event)

            if conceptual_text is not None:
                conceptual_node_id = f"conceptual_{event_index}"

                if add_ged_node(graph, conceptual_node_id, "conceptual", conceptual_text, args, position=event_index):
                    graph.add_edge(event_node_id, conceptual_node_id, type="has_conceptual")

            evaluative_text = evaluative_story.get(event)

            if evaluative_text is not None:
                evaluative_node_id = f"evaluative_{event_index}"

                if add_ged_node(graph, evaluative_node_id, "evaluative", evaluative_text, args, position=event_index):
                    graph.add_edge(event_node_id, evaluative_node_id, type="has_evaluative")

        add_temporal_edges(graph, backbone_nodes)
        add_shared_arc_and_stage_nodes(graph, backbone_event_nodes, arc_story, stage_story, args)

    elif graph_variant == "GED_conceptual_evaluative":
        backbone_nodes = []

        for event_index, event in enumerate(events_story):
            conceptual_text = conceptual_story.get(event)

            if conceptual_text is None:
                continue

            conceptual_node_id = f"conceptual_{event_index}"

            if not add_ged_node(graph, conceptual_node_id, "conceptual", conceptual_text, args, position=event_index):
                continue

            backbone_nodes.append(conceptual_node_id)
            evaluative_text = evaluative_story.get(event)

            if evaluative_text is not None:
                evaluative_node_id = f"evaluative_{event_index}"

                if add_ged_node(graph, evaluative_node_id, "evaluative", evaluative_text, args, position=event_index):
                    graph.add_edge(conceptual_node_id, evaluative_node_id, type="has_evaluative")

        add_temporal_edges(graph, backbone_nodes)

    elif graph_variant == "GED_conceptual_full":
        backbone_nodes = []
        backbone_event_nodes = []

        for event_index, event in enumerate(events_story):
            conceptual_text = conceptual_story.get(event)

            if conceptual_text is None:
                continue

            conceptual_node_id = f"conceptual_{event_index}"

            if not add_ged_node(graph, conceptual_node_id, "conceptual", conceptual_text, args, position=event_index):
                continue

            backbone_nodes.append(conceptual_node_id)
            backbone_event_nodes.append((conceptual_node_id, event))

            evaluative_text = evaluative_story.get(event)

            if evaluative_text is not None:
                evaluative_node_id = f"evaluative_{event_index}"

                if add_ged_node(graph, evaluative_node_id, "evaluative", evaluative_text, args, position=event_index):
                    graph.add_edge(conceptual_node_id, evaluative_node_id, type="has_evaluative")

        add_temporal_edges(graph, backbone_nodes)
        add_shared_arc_and_stage_nodes(graph, backbone_event_nodes, arc_story, stage_story, args)

    elif graph_variant == "GED_stage_arc":
        arc_labels = {"TP1": "Introduction", "TP2": "Event", "TP3": "Challenge", "TP4": "Action", "TP5": "Conclusion"}
        backbone_nodes = []
        stage_role_pairs = []
        arc_nodes_by_role = {}

        for stage_index, (stage_text, role) in enumerate(get_stage_items(stage_story)):
            stage_node_id = f"stage_{stage_index}"

            if add_ged_node(graph, stage_node_id, "stage", stage_text, args, position=stage_index):
                backbone_nodes.append(stage_node_id)
                stage_role_pairs.append((stage_node_id, role))

        add_temporal_edges(graph, backbone_nodes)

        for stage_node_id, role in stage_role_pairs:
            if role not in arc_nodes_by_role:
                arc_node_id = f"arc_{role}"
                arc_text = arc_labels[role]

                if add_ged_node(graph, arc_node_id, "arc", arc_text, args):
                    arc_nodes_by_role[role] = arc_node_id

            if role in arc_nodes_by_role:
                graph.add_edge(stage_node_id, arc_nodes_by_role[role], type="has_arc")

    return graph


def build_ged_graph_cache(main_data, main_events, main_conceptual, main_evaluative, main_arc, main_stage, main_timeline, args):
    graph_cache = {}
    unique_graph_cache = {}
    all_scoring_values = []
    reused_graphs = 0

    input_lengths = [len(main_events), len(main_conceptual), len(main_evaluative), len(main_arc), len(main_stage), len(main_timeline)]

    if any(length != len(main_data) for length in input_lengths):
        raise ValueError(f"GED input lengths do not match main_data: main_data={len(main_data)}, inputs={input_lengths}")

    for index in tqdm(range(len(main_data)), desc="Building GED graphs"):
        sample_events = main_events[index]
        sample_conceptual = main_conceptual[index]
        sample_evaluative = main_evaluative[index]
        sample_arc = main_arc[index]
        sample_stage = main_stage[index]
        sample_timeline = main_timeline[index]

        if args.dataset == "ARN":
            row = main_data.iloc[index]
            story_texts = {"base": row["query_narrative"].strip(), "target1": row["first_choice"].strip(), "target2": row["second_choice"].strip()}

        elif args.dataset == "MCQ":
            sample_data = main_data[index]
            story_texts = {"base": sample_data["source"].strip()}
            story_texts.update({f"target{choice_index + 1}": choice.strip() for choice_index, choice in enumerate(sample_data["choices"])})

        else:
            raise ValueError(f"Unsupported dataset for GED graph caching: {args.dataset}")

        story_keys = ["base"] + sorted(key for key in sample_events if key.startswith("target"))

        for story_key in story_keys:
            if story_key not in story_texts:
                raise KeyError(f"Story text is missing at sample {index}, key {story_key}.")

            events_story = sample_events.get(story_key, [])
            conceptual_story = sample_conceptual.get(story_key, {})
            evaluative_story = sample_evaluative.get(story_key, {})
            arc_story = sample_arc.get(story_key, {})
            stage_story = sample_stage.get(story_key, {})
            timeline_story = sample_timeline.get(story_key, {})

            story_signature = story_texts[story_key]

            if story_signature not in unique_graph_cache:
                graph = build_ged_graph(events_story, conceptual_story, evaluative_story, arc_story, stage_story, timeline_story, args.global_map, args)
                unique_graph_cache[story_signature] = graph

                for _, node_data in graph.nodes(data=True):
                    all_scoring_values.extend(node_data["values"])
            else:
                graph = unique_graph_cache[story_signature]
                reused_graphs += 1

            graph_cache[(index, story_key)] = graph


    unique_scoring_values = list(dict.fromkeys(all_scoring_values))

    print("Total story occurrences:", len(graph_cache))
    print("Unique GED graphs:", len(unique_graph_cache))
    print("Reused GED graphs:", reused_graphs)

    return graph_cache, unique_scoring_values


def collect_missing_ged_nli_pairs(base_graph, target_graph, nli_cache):
    missing_pairs = []

    for _, base_data in base_graph.nodes(data=True):
        for _, target_data in target_graph.nodes(data=True):
            if base_data["type"] != target_data["type"]:
                continue

            base_values = base_data["values"]
            target_values = target_data["values"]
            number_of_values = min(len(base_values), len(target_values))

            for value_index in range(number_of_values):
                pair = (base_values[value_index], target_values[value_index])

                if pair not in nli_cache:
                    missing_pairs.append(pair)

    return list(dict.fromkeys(missing_pairs))


def ged_node_substitution_cost(base_data, target_data, embedding_dicts, VI, nli_cache, args):
    if base_data["type"] != target_data["type"]:
        return 1.0

    base_values = base_data["values"]
    target_values = target_data["values"]
    number_of_values = min(len(base_values), len(target_values))

    if number_of_values == 0:
        return 1.0

    base_values = base_values[:number_of_values]
    target_values = target_values[:number_of_values]

    B_local = np.stack([embedding_dicts[value] for value in base_values])
    T_local = np.stack([embedding_dicts[value] for value in target_values])

    if args.scoring_method == "mahalanobis":
        normalized_similarity = float(np.clip(final_mahalanobis_similarity(B_local, T_local, VI), 0.0, 1.0))

    elif args.scoring_method == "nli":
        component_scores = []

        for value_index in range(number_of_values):
            base_value = base_values[value_index]
            target_value = target_values[value_index]
            pair = (base_value, target_value)

            if pair not in nli_cache:
                raise KeyError(f"Missing NLI pair in GED cache: {pair}")

            p_contra, p_neutral, p_ent = nli_cache[pair]
            raw_cosine = float(np.dot(B_local[value_index], T_local[value_index]))
            soft_sign = p_ent + p_neutral - p_contra
            component_scores.append(raw_cosine * soft_sign)

        raw_similarity = float(np.mean(component_scores))
        normalized_similarity = float(np.clip((raw_similarity + 1.0) / 2.0, 0.0, 1.0))

    else:
        raw_similarity = float(np.mean(np.sum(B_local * T_local, axis=1)))
        normalized_similarity = float(np.clip((raw_similarity + 1.0) / 2.0, 0.0, 1.0))

    return float(1.0 - normalized_similarity)


def ged_node_deletion_cost(node_data):
    return 0.5


def ged_node_insertion_cost(node_data):
    return 0.5


def ged_edge_substitution_cost(base_edge_data, target_edge_data):
    return 0.0 if base_edge_data.get("type") == target_edge_data.get("type") else 1.0


def ged_edge_deletion_cost(edge_data):
    return 0.5


def ged_edge_insertion_cost(edge_data):
    return 0.5


def get_normalized_ged_similarity(base_graph, target_graph, embedding_dicts, VI, nli_cache, args):
    deletion_insertion_cost = 0.5 * (base_graph.number_of_nodes() + target_graph.number_of_nodes() + base_graph.number_of_edges() + target_graph.number_of_edges())

    if deletion_insertion_cost == 0:
        return None, None, 0.0

    node_substitution_function = lambda base_data, target_data: ged_node_substitution_cost(base_data, target_data, embedding_dicts, VI, nli_cache, args)
    timeout = float(args.config.get("ged_timeout", 5.0))

    if timeout <= 0:
        raise ValueError(f"ged_timeout must be positive, received: {timeout}")

    start_time = time.perf_counter()
    ged = nx.graph_edit_distance(base_graph, target_graph, node_subst_cost=node_substitution_function, node_del_cost=ged_node_deletion_cost, node_ins_cost=ged_node_insertion_cost, edge_subst_cost=ged_edge_substitution_cost, edge_del_cost=ged_edge_deletion_cost, edge_ins_cost=ged_edge_insertion_cost, timeout=timeout)
    elapsed_time = time.perf_counter() - start_time

    if ged is None:
        return None, None, elapsed_time

    ged = float(ged)

    if not np.isfinite(ged) or ged < 0:
        raise ValueError(f"Invalid GED value: {ged}")

    effective_ged = min(ged, deletion_insertion_cost)
    normalized_ged = effective_ged / deletion_insertion_cost
    graph_similarity = float(np.clip(1.0 - normalized_ged, 0.0, 1.0))

    return graph_similarity, ged, elapsed_time


def build_ged_nli_cache(graph_cache, main_events, nli_token, nli_model, batch_size=256):
    all_nli_pairs = []
    seen_pairs = set()

    for index in tqdm(range(len(main_events)), desc="Collecting GED NLI pairs"):
        base_graph = graph_cache[(index, "base")]
        target_keys = sorted(key for key in main_events[index] if key.startswith("target"))

        for target_key in target_keys:
            target_graph = graph_cache[(index, target_key)]
            graph_pairs = collect_missing_ged_nli_pairs(base_graph, target_graph, {})

            for pair in graph_pairs:
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    all_nli_pairs.append(pair)

    print("Unique GED NLI pairs:", len(all_nli_pairs))

    if not all_nli_pairs:
        return {}

    return build_nli_cache(all_nli_pairs, nli_token, nli_model, batch_size=batch_size)


def GED_mapping(main_data, main_events, main_conceptual, main_evaluative, main_arc, main_stage, main_timeline, embedding_model, nli_model, nli_token, args):
    graph_cache, unique_scoring_values = build_ged_graph_cache(main_data, main_events, main_conceptual, main_evaluative, main_arc, main_stage, main_timeline, args)
    nli_batch_size = int(args.config.get("nli_batch_size", 256))

    if args.scoring_method == "mahalanobis":
        embedding_dicts = build_embedding_cache(embedding_model, unique_scoring_values, batch_size=1024, normalize=False, to_numpy=True, show_progress=True)
        VI = fit_mahalanobis_from_dict(embedding_dicts)
        nli_cache = None

    elif args.scoring_method == "nli":
        embedding_dicts = build_embedding_cache(embedding_model, unique_scoring_values)
        VI = None
        nli_cache = build_ged_nli_cache(graph_cache, main_events, nli_token, nli_model, batch_size=nli_batch_size)

    else:
        embedding_dicts = build_embedding_cache(embedding_model, unique_scoring_values)
        VI = None
        nli_cache = None

    y_true = []
    y_pred = []

    category_dict_ref = {"low-near": 294, "low-far": 294, "high-near": 253, "high-far": 254}
    category_dict = {"low-near": 0, "low-far": 0, "high-near": 0, "high-far": 0}

    tie_count = 0
    empty_graph_comparisons = 0
    failed_ged_comparisons = 0
    near_timeout_comparisons = 0
    ged_timeout = float(args.config.get("ged_timeout", 5.0))

    for index in tqdm(range(len(main_data)), desc=f"GED mapping ({args.global_map})"):
        sample_events = main_events[index]
        base_graph = graph_cache[(index, "base")]

        correct_answer, category = get_correct_answer(main_data, index, args)
        y_true.append(correct_answer)

        target_keys = sorted(key for key in sample_events if key.startswith("target"))
        total_scores = []

        if not target_keys:
            raise ValueError(f"No target stories at sample {index}.")

        for target_key in target_keys:
            target_graph = graph_cache[(index, target_key)]

            if base_graph.number_of_nodes() == 0 or target_graph.number_of_nodes() == 0:
                empty_graph_comparisons += 1
                total_scores.append(-np.inf)
                continue

            graph_similarity, ged, elapsed_time = get_normalized_ged_similarity(base_graph, target_graph, embedding_dicts, VI, nli_cache, args)

            if elapsed_time >= 0.95 * ged_timeout:
                near_timeout_comparisons += 1

            if graph_similarity is None:
                failed_ged_comparisons += 1
                total_scores.append(-np.inf)
                continue

            total_scores.append(graph_similarity)

        valid_scores = [score for score in total_scores if np.isfinite(score)]

        if not valid_scores:
            raise ValueError(f"No valid GED target scores at sample {index}.")

        max_score = max(total_scores)
        max_indices = [target_index for target_index, score in enumerate(total_scores) if score == max_score]

        if len(max_indices) > 1:
            tie_count += 1

        y_pred.append(random.choice(max_indices))

        if args.dataset == "ARN" and y_true[-1] == y_pred[-1]:
            category_dict[category] += 1

    print("GED graph variant:", args.global_map)
    print("GED timeout:", ged_timeout)
    print("GED ties:", tie_count)
    print("Empty graph comparisons:", empty_graph_comparisons)
    print("Failed GED comparisons:", failed_ged_comparisons)
    print("Comparisons near timeout:", near_timeout_comparisons)

    result = round(metrics.accuracy_score(y_true, y_pred), 2)

    if args.dataset == "ARN":
        for key in category_dict:
            category_dict[key] = round(category_dict[key] / category_dict_ref[key], 2)

        return result, category_dict

    elif args.dataset == "MCQ":
        return result, "-"

####### Load data   

def merge_abstraction_units(conceptual_units, evaluative_units):
    merged_units = {}

    for idx, sample in conceptual_units.items():
        merged_units[idx] = {}

        for field_name, events in sample.items():
            evaluative_events = evaluative_units.get(idx, {}).get(field_name, {})

            merged_units[idx][field_name] = {
                event: [
                    conceptual_value,
                    evaluative_events.get(event, "")
                ]
                for event, conceptual_value in events.items()
            }

    return merged_units
        
    
def load_data(args):
    data_short = args.dataset.lower()
    model_short = model_short_dict.get(args.model)

    if data_short == "arn":
        main_data = pd.read_csv(
            "Data/Datasets/Analogical Reasoning on Narratives (ARN) dataset.xlsx - Sheet1.csv"
        )
    elif data_short == "mcq":
        with open("Data/Datasets/storyanalogy_multiple_choice.json") as f:
            main_data = json.load(f)
    else:
        raise ValueError(f"Unsupported dataset: {args.dataset}")

    if args.unit == "events":
        path_units = f"{PATH_UNITS}{model_short}events_{data_short}.pkl"
        with open(path_units, "rb") as f:
            main_units = pickle.load(f)

    elif args.unit == "conceptual0_evaluative":
        conceptual_path = (f"{PATH_ABSTRACTION}{model_short}events_conceptual0_{data_short}.pkl")
        evaluative_path = (f"{PATH_ABSTRACTION}{model_short}events_evaluative_{data_short}.pkl")

        with open(conceptual_path, "rb") as f:
            conceptual_units = pickle.load(f)
        with open(evaluative_path, "rb") as f:
            evaluative_units = pickle.load(f)

        main_units = merge_abstraction_units(conceptual_units, evaluative_units)

    elif args.unit == "stage_arc":
        path_units = (f"{PATH_ABSTRACTION}{model_short}events_stage_{data_short}.pkl")
        with open(path_units, "rb") as f:
            main_units = pickle.load(f)

    else:
        path_units = (f"{PATH_ABSTRACTION}{model_short}events_{args.unit}_{data_short}.pkl")
        with open(path_units, "rb") as f:
            main_units = pickle.load(f)
    
    path_arc_abstraction = (f"{PATH_ABSTRACTION}{model_short}events_arc_{data_short}.pkl")
    with open(path_arc_abstraction, "rb") as f:
        arc_abstraction = pickle.load(f)

    path_timeline = (f"{PATH_ABSTRACTION}{model_short}events_timeline_{data_short}.pkl")
    with open(path_timeline, "rb") as f:
        timeline_abstraction = pickle.load(f)

    return main_data, main_units, arc_abstraction, timeline_abstraction


def load_ged_data(args):
    data_short = args.dataset.lower()
    model_short = model_short_dict.get(args.model)

    if data_short == "arn":
        main_data = pd.read_csv("Data/Datasets/Analogical Reasoning on Narratives (ARN) dataset.xlsx - Sheet1.csv")
    elif data_short == "mcq":
        with open("Data/Datasets/storyanalogy_multiple_choice.json") as f:
            main_data = json.load(f)
    else:
        raise ValueError(f"Unsupported dataset: {args.dataset}")

    events_path = f"{PATH_UNITS}{model_short}events_{data_short}.pkl"
    conceptual_path = f"{PATH_ABSTRACTION}{model_short}events_conceptual0_{data_short}.pkl"
    evaluative_path = f"{PATH_ABSTRACTION}{model_short}events_evaluative_{data_short}.pkl"
    arc_path = f"{PATH_ABSTRACTION}{model_short}events_arc_{data_short}.pkl"
    stage_path = f"{PATH_ABSTRACTION}{model_short}events_stage_{data_short}.pkl"
    timeline_path = f"{PATH_ABSTRACTION}{model_short}events_timeline_{data_short}.pkl"

    with open(events_path, "rb") as f:
        main_events = pickle.load(f)

    with open(conceptual_path, "rb") as f:
        main_conceptual = pickle.load(f)

    with open(evaluative_path, "rb") as f:
        main_evaluative = pickle.load(f)

    with open(arc_path, "rb") as f:
        main_arc = pickle.load(f)

    with open(stage_path, "rb") as f:
        main_stage = pickle.load(f)

    with open(timeline_path, "rb") as f:
        main_timeline = pickle.load(f)

    return main_data, main_events, main_conceptual, main_evaluative, main_arc, main_stage, main_timeline

def run_main_mapping(args):
    start_time_overall = time.perf_counter()

    print("\n=== Step 1: Loading embedding model ===")
    embedding_model = get_embedding_model(args)
    nli_model, nli_token = get_nli_model()
    
    print("\n=== Step 2: Loading the Dataset and the Units ===")
    if args.dataset == "ARN":
        main_data, main_units, arc_abstraction, timeline_abstraction = load_data(args)
    elif args.dataset == "MCQ":
        main_data, main_units, arc_abstraction, timeline_abstraction = load_data(args)

    
    print(f"\n=== Step 3: Run the mapping with {args.global_map} mapping and {args.scoring_method} scoring and {args.config} config")
    if args.global_map == "Greedy":
        accuracy, arn_category_accuracy = Greedy_mapping(main_data, main_units, embedding_model, nli_model, nli_token, args)

    elif args.global_map == "Linear":
        accuracy, arn_category_accuracy = Linear_mapping(main_data, main_units, embedding_model, nli_model, nli_token, args)

    elif args.global_map == "Role_mapping":
        if args.unit == "stage":
            accuracy, arn_category_accuracy = Role_constrained_mapping(main_data, main_units, main_units, embedding_model, nli_model, nli_token, args)
        else:
            accuracy, arn_category_accuracy = Role_constrained_mapping(main_data, main_units, arc_abstraction, embedding_model, nli_model, nli_token, args)
        
    elif args.global_map == "Global_mapping":
        accuracy, arn_category_accuracy = Global_assignment_mapping(main_data, main_units, embedding_model, nli_model, nli_token, args)

    elif args.global_map.startswith("GED_"):
        main_data, main_events, main_conceptual, main_evaluative, main_arc, main_stage, main_timeline = load_ged_data(args)
        accuracy, arn_category_accuracy = GED_mapping(main_data, main_events, main_conceptual, main_evaluative, main_arc, main_stage, main_timeline, embedding_model, nli_model, nli_token, args)

        
    
    print("accuracy: ", accuracy)
    print("arn_category: ", arn_category_accuracy)
    
    append_results(args, accuracy, arn_category_accuracy)
    
    elapsed_time_overall = time.perf_counter() - start_time_overall
    print("time overall for : ", float(args.config.get("ged_timeout", 5.0)), " is: ", elapsed_time_overall)