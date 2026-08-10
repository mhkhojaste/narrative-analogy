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


def tp_num(s: str) -> int:
    m = re.search(r'\d+', s)
    return int(m.group()) if m else 10**9

def sort_by_tp(d):
    items = [(text, tp, tp_num(tp)) for text, tp in d.items()]
    return sorted(items, key=lambda x: x[2])

def compose_seq_text(texts):
    return " [SEP] ".join(texts)

def _encode_texts(texts, embedding_model):
    with torch.inference_mode():
        embs = embedding_model.encode(
            texts, batch_size=1024, convert_to_tensor=True, show_progress_bar=False, normalize_embeddings=False
        )
    embs = normalize_embeddings(embs).cpu().numpy().astype(np.float32)
    return embs 

def precompute_similarity_tables(base_dict, target_dict, embedding_model):
    b_sorted = sort_by_tp(base_dict)  # [(b_text, b_tp, tp_num), ...]
    t_sorted = sort_by_tp(target_dict)
    nb, nt = len(b_sorted), len(t_sorted)

    if nb == 0 or nt == 0:
        raise ValueError("base/target is empty.")

    b_texts = [x[0] for x in b_sorted]
    t_texts = [x[0] for x in t_sorted]

    B = _encode_texts(b_texts, embedding_model)  # [nb, d]
    T = _encode_texts(t_texts, embedding_model)  # [nt, d]

    S = (B @ T.T)  # [nb, nt], float32

    b_pairs = [(i, j) for i in range(nb) for j in range(i+1, nb)]
    t_pairs = [(p, q) for p in range(nt) for q in range(p+1, nt)]
    if b_pairs and t_pairs:
        b_pair_texts = [compose_seq_text([b_texts[i], b_texts[j]]) for (i, j) in b_pairs]
        t_pair_texts = [compose_seq_text([t_texts[p], t_texts[q]]) for (p, q) in t_pairs]
        B2 = _encode_texts(b_pair_texts, embedding_model)  
        T2 = _encode_texts(t_pair_texts, embedding_model)  
        P = (B2 @ T2.T)  
    else:
        P = np.zeros((len(b_pairs), len(t_pairs)), dtype=np.float32)

    return b_sorted, t_sorted, S, P, b_pairs, t_pairs


def best_mapping_by_tp_variable_fast(base_dict, target_dict, model, alpha=1.0, beta=1.0):

    b_sorted, t_sorted, S, P, b_pairs, t_pairs = precompute_similarity_tables(base_dict, target_dict, model)
    nb, nt = len(b_sorted), len(t_sorted)
    k = min(nb, nt)

    best_score = -1e9
    best_detail = None
    best_b_sub = None
    best_t_sub = None

    pair_pos = [(r, s) for r in range(k) for s in range(r+1, k)]
    use_s2 = (beta != 0.0) and (len(b_pairs) > 0) and (len(t_pairs) > 0) and (len(pair_pos) > 0)

    bpair_id = {}
    for idx, (i, j) in enumerate(b_pairs):
        bpair_id[(i, j)] = idx
    tpair_id = {}
    for idx, (p, q) in enumerate(t_pairs):
        tpair_id[(p, q)] = idx

    from itertools import combinations
    for b_idx in combinations(range(nb), k):
        for t_idx in combinations(range(nt), k):
            s1_vals = [ S[b_idx[r], t_idx[r]] for r in range(k) ]
            s1 = float(np.mean(s1_vals)) if k > 0 else 0.0

            if use_s2:
                s2_vals = []
                for (r, s) in pair_pos:
                    bi, bj = b_idx[r], b_idx[s]
                    pi, pj = t_idx[r], t_idx[s]
                    bb = (bi, bj) if bi < bj else (bj, bi)
                    tt = (pi, pj) if pi < pj else (pj, pi)
                    s2_vals.append(P[bpair_id[bb], tpair_id[tt]])
                s2 = float(np.mean(s2_vals))
            else:
                s2 = 0.0

            total = alpha * s1 + beta * s2

            if total > best_score:
                best_score = total
                best_b_sub = tuple(b_sorted[i] for i in b_idx)
                best_t_sub = tuple(t_sorted[j] for j in t_idx)
                best_detail = {
                    "k": k,
                    "pairs_itemwise": [
                        (best_b_sub[r][0], best_t_sub[r][0], float(s1_vals[r]), best_b_sub[r][1], best_t_sub[r][1])
                        for r in range(k)
                    ],
                    "s1_mean_itemwise": float(round(s1, 3)),
                    "s2_all_pairs": {
                        "pairs": {f"({r},{s})": float(P[bpair_id[tuple(sorted((b_idx[r], b_idx[s])))],
                                                         tpair_id[tuple(sorted((t_idx[r], t_idx[s])))]])
                                  for (r, s) in pair_pos} if use_s2 else {},
                        "mean": float(round(s2, 3))
                    },
                    "alpha": float(alpha),
                    "beta": float(beta),
                    "total_score": float(round(total, 3))
                }

    return best_b_sub, best_t_sub, best_detail


def ensure_results_sheet_exists():
    if not os.path.exists(RESULTS_PATH):
        print("[INFO] Creating new results sheet...")
        columns = [
            "id", "version", "model", "unit", "enrichment", 
            "scoring_unit", "scoring_method", "scoring_constraint", "global_match",
            "MCQ accuracy", "ARN accuracy", 
            "arn low-near", "arn low-far", "arn high-near", "arn high-far"
        ]
        df = pd.DataFrame(columns=columns)
        df.to_csv(RESULTS_PATH, index=False)

def ensure_expriment_sheet_exists(args):
    if "ARN" in args.dataset:
        expriment_name_path = RESULTS_DIR + str(args.version) + "_" + str(args.dataset) + ".csv"
        if not os.path.exists(expriment_name_path):
            print("[INFO] Creating the experiment sheet...")
            columns = ["id", "Base story", "Target 1", "Target 2", "Correct answer", "Mapping base - target1", "Solutions base - target1", "Mapping base - target2", "Solutions base - target2"]
            df = pd.DataFrame(columns=columns)
            df.to_csv(expriment_name_path, index=False)
    else:
        expriment_name_path = RESULTS_DIR + str(args.version) + "_" + str(args.dataset) + ".csv"
        if not os.path.exists(expriment_name_path):
            print("[INFO] Creating the experiment sheet...")
            columns = ["id", "Base story", "Target 1", "Target 2", "Target 3", "Target 4", "Correct answer", "Mapping base - target1", "Solutions base - target1", "Mapping base - target2", "Solutions base - target2", "Mapping base - target3", "Solutions base - target3", "Mapping base - target4", "Solutions base - target4"]
            df = pd.DataFrame(columns=columns)
            df.to_csv(expriment_name_path, index=False)
        
        
def append_results(args, accuracy, arn_array=None):
    ensure_results_sheet_exists()
    df = pd.read_csv(RESULTS_PATH)

    # Check if this version already exists
    existing_row = df[df["version"] == args.version]

    if existing_row.empty:
        # No existing row with this version
        new_id = len(df) + 1
        new_row = {
            "id": new_id,
            "version": args.version,
            "model": args.model,
            "unit": args.unit,
            "enrichment": args.enrichment,
            "scoring_unit": args.scoring_unit,
            "scoring_method": args.scoring_method,
            "scoring_constraint": args.scoring_constraint,
            "global_match": args.global_match,
            "MCQ accuracy": None,
            "ARN accuracy": None,
            "arn low-near": None,
            "arn low-far": None,
            "arn high-near": None,
            "arn high-far": None
        }

        if "MCQ"in args.dataset:
            new_row["MCQ accuracy"] = accuracy
        elif "ARN"in args.dataset:
            new_row["ARN accuracy"] = accuracy
            if arn_array:
                new_row["arn low-near"] = arn_array["low-near"]
                new_row["arn low-far"] = arn_array["low-far"]
                new_row["arn high-near"] = arn_array["high-near"]
                new_row["arn high-far"] = arn_array["high-far"]

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        print(f"[INFO] New version added under ID {new_id}")

    else:
        # Row already exists; update it
        idx = existing_row.index[0]
        if "MCQ"in args.dataset:
            df.at[idx, "MCQ accuracy"] = accuracy
            print(f"[INFO] MCQ accuracy updated for version {args.version}")
        elif "ARN"in args.dataset:
            df.at[idx, "ARN accuracy"] = accuracy
            if arn_array:
                df.at[idx, "arn low-near"] = arn_array["low-near"]
                df.at[idx, "arn low-far"] = arn_array["low-far"]
                df.at[idx, "arn high-near"] = arn_array["high-near"]
                df.at[idx, "arn high-far"] = arn_array["high-far"]
            print(f"[INFO] ARN accuracy and categories updated for version {args.version}")

    df.to_csv(RESULTS_PATH, index=False)

    
def append_experiment(args, id_s, base_story, targets, correct_ans, mappings, sols):
    ensure_expriment_sheet_exists(args)
    expriment_name_path = RESULTS_DIR + str(args.version) + "_" + str(args.dataset) + ".csv"
    df = pd.read_csv(expriment_name_path)
    
    if "ARN" in args.dataset:
        new_row = {
            "id": str(id_s),
            "Base story": base_story,
            "Target 1": targets[0],
            "Target 2": targets[1],
            "Correct answer": str(correct_ans),
            "Mapping base - target1": str([m for m in mappings[0] if m['best_score'] > 0][:10]),
            "Solutions base - target1": str(sols[0]),
            "Mapping base - target2": str([m for m in mappings[1] if m['best_score'] > 0][:10]),
            "Solutions base - target2": str(sols[1])
        }
    else:
        new_row = {
            "id": str(id_s),
            "Base story": base_story,
            "Target 1": targets[0],
            "Target 2": targets[1],
            "Target 3": targets[2],
            "Target 4": targets[3],
            "Correct answer": str(correct_ans),
            "Mapping base - target1": str([m for m in mappings[0] if m['best_score'] > 0][:10]),
            "Solutions base - target1": str(sols[0]),
            "Mapping base - target2": str([m for m in mappings[1] if m['best_score'] > 0][:10]),
            "Solutions base - target2": str(sols[1]),
            "Mapping base - target3": str([m for m in mappings[2] if m['best_score'] > 0][:10]),
            "Solutions base - target3": str(sols[2]),
            "Mapping base - target4": str([m for m in mappings[3] if m['best_score'] > 0][:10]),
            "Solutions base - target4": str(sols[3])
        }
        
    
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(expriment_name_path, index=False)

def get_minimum_score(solutions):
    new_solutions = []
    
    for sol in solutions:
        if sol['score'] == 0:
            continue
        sol_new = copy.deepcopy(sol)                   
        sol_new['score'] = min(sol['scores'])
        new_solutions.append(sol_new)
        
    return new_solutions

def print_sol(solutions):
    for sol in solutions:
        print(sol)
        break

def compute_max_and_total_scores(solutions):
    max_score = 0
    total_score = 0

    for sol in solutions:
        coverage_sum = sum(sol['coverage'])
        sc = round(sol['score'] / coverage_sum, 3) if coverage_sum > 0 else 0

        if sc > max_score:
            max_score = sc

        if sol['score'] > total_score:
            total_score = sol['score']

    return round(max_score, 3), round(total_score, 3)
    
    
def update_mapping_scores(embedding_model, args, final_solutions, all_enrichment, all_score_unit):
    
    new_solutions = []
    
    for sol in final_solutions:
        
        if sol['score'] == 0:
            continue
        
        sol_new = copy.deepcopy(sol)
        
        
        actual_base = sol['actual_base']
        actual_target = sol['actual_target']
        
        if args.unit == "unit_event_phrases" or args.unit == "unit_event_phrases_2" or args.unit == "unit_event_phrases_3":
            if args.enrichment == "none":
                score, cov = score_event_phrases_no_enrichment(args, actual_base, actual_target, all_score_unit, embedding_model)
            elif args.enrichment == "stage":
                score, cov = score_event_phrases_with_stage_enrichment(args, actual_base, actual_target, all_enrichment, all_score_unit, embedding_model)
            elif "stage_rel" in args.enrichment:
                score, cov = score_event_phrases_with_stage_rel_enrichment(args, actual_base, actual_target, all_enrichment, all_score_unit, embedding_model)
                
                
        sol_new['score'] = round(score, 3)
        
        new_solutions.append(sol_new)
        
    return new_solutions


######### Full datasets and with batching

def extract_all_units(arn_data, arn_event, arn_enrichment, arn_score_unit, args):
    stories_events = {}
    for index, row in tqdm(arn_data.iterrows(), total=len(arn_data)):
        base_story = row["query_narrative"].strip()
        target_story1 = row["first_choice"].strip()
        target_story2 = row["second_choice"].strip()
        
        sample_event = arn_event[index]
        base_event = sample_event["base"]
        target1_event = sample_event["target1"]
        target2_event = sample_event["target2"]

        
        
        
        if len(arn_enrichment)>0 : 
            sample_enrichment = arn_enrichment[index]
            base_enrichment = sample_enrichment["base"]
            target1_enrichment = sample_enrichment["target1"]
            target2_enrichment = sample_enrichment["target2"]
        else:
            base_enrichment = {}
            target1_enrichment = {}
            target2_enrichment = {}

        
        sample_score_unit = arn_score_unit[index]
        base_score_unit = sample_score_unit["base"]
        target1_score_unit = sample_score_unit["target1"]
        target2_score_unit = sample_score_unit["target2"]

        if "superunit" in args.scoring_unit:
            base_event = list(base_event.keys())
            target1_event = list(target1_event.keys())
            target2_event = list(target2_event.keys())

        if "only_abstractions" in args.scoring_constraint: 
            base_event = list(dict.fromkeys(base_score_unit.values()))
            target1_event = list(dict.fromkeys(target1_score_unit.values()))
            target2_event = list(dict.fromkeys(target2_score_unit.values()))

            if "root" in args.scoring_constraint:
                base_event = [v.split()[1] if len(v.split()) > 1 else v for v in base_event]
                target1_event = [v.split()[1] if len(v.split()) > 1 else v for v in target1_event]
                target2_event = [v.split()[1] if len(v.split()) > 1 else v for v in target2_event]

            base_score_unit = {}
            target1_score_unit = {}
            target2_score_unit = {}


        stories_events = get_pairs_update(get_all_possible_pairs_map(base_event, target1_event), args, [base_enrichment, target1_enrichment], [base_score_unit, target1_score_unit], stories_events)
        stories_events = get_pairs_update(get_all_possible_pairs_map(base_event, target2_event), args, [base_enrichment, target2_enrichment], [base_score_unit, target2_score_unit], stories_events)

    return stories_events

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

def fit_mahalanobis_from_dict(embedding_dict, reg=1e-4, use_shrinkage=True):
    # Stack to (n, d) float64 for stable linear algebra
    X = np.asarray(np.stack(list(embedding_dict.values()), axis=0), dtype=np.float64)
    mu = X.mean(axis=0)
    Xc = X - mu

    if use_shrinkage:
        try:
            from sklearn.covariance import LedoitWolf
            Sigma = LedoitWolf().fit(Xc).covariance_
            # LW is well-conditioned → inverse (not pinv) is appropriate
            VI = np.linalg.inv(Sigma)
        except Exception:
            # Fallback to sample covariance + ridge + pinv
            Sigma = np.cov(Xc, rowvar=False, ddof=1)
            Sigma = Sigma + reg * np.eye(Sigma.shape[0], dtype=Sigma.dtype)
            VI = np.linalg.pinv(Sigma)
    else:
        Sigma = np.cov(Xc, rowvar=False, ddof=1)
        Sigma = Sigma + reg * np.eye(Sigma.shape[0], dtype=Sigma.dtype)
        VI = np.linalg.pinv(Sigma)

    # Symmetrize to remove numerical drift
    VI = 0.5 * (VI + VI.T)
    return mu, VI



def mapping_pipeline_ARN(embedding_model, arn_data, arn_event, arn_enrichment, arn_score_unit, args):

    ## generates sentenses
    stories_events = extract_all_units(arn_data, arn_event, arn_enrichment, arn_score_unit, args)

    unique_values = list(dict.fromkeys(chain.from_iterable(stories_events.values())))


    if args.scoring_constraint == "mahalanobis":
        embedding_dicts = build_embedding_cache(embedding_model, unique_values, batch_size=1024, normalize=False, to_numpy=True, show_progress=True)
        mu, VI = fit_mahalanobis_from_dict(embedding_dicts, reg=1e-4, use_shrinkage=True)

    else:
        embedding_dicts = build_embedding_cache(embedding_model, unique_values)
        mu = 0
        VI = 0

    

    y_true = []
    y_pred = []
    category_dict_ref = {'low-near': 294, 'low-far': 294, 'high-near': 253, 'high-far': 254}
    category_dict = {'low-near': 0, 'low-far': 0, 'high-near': 0, 'high-far': 0}

    for index, row in tqdm(arn_data.iterrows(), total=len(arn_data)):
        base_story = row["query_narrative"].strip()
        target_story1 = row["first_choice"].strip()
        target_story2 = row["second_choice"].strip()
        
        correct_answer = int(row["correct_answer"]) - 1
        y_true.append(correct_answer)
        category = row["distractor_similarity"] + "-" + row["analogy_level"]
        
        sample_event = arn_event[index]
        base_event = sample_event["base"]
        target1_event = sample_event["target1"]
        target2_event = sample_event["target2"]
        
        
        if len(arn_enrichment)>0 : 
            sample_enrichment = arn_enrichment[index]
            base_enrichment = sample_enrichment["base"]
            target1_enrichment = sample_enrichment["target1"]
            target2_enrichment = sample_enrichment["target2"]
        else:
            base_enrichment = {}
            target1_enrichment = {}
            target2_enrichment = {}

        sample_score_unit = arn_score_unit[index]
        base_score_unit = sample_score_unit["base"]
        target1_score_unit = sample_score_unit["target1"]
        target2_score_unit = sample_score_unit["target2"]

        if "superunit" in args.scoring_unit:
            base_event = list(base_event.keys())
            target1_event = list(target1_event.keys())
            target2_event = list(target2_event.keys())


        if "only_abstractions" in args.scoring_constraint: 
            base_event = list(dict.fromkeys(base_score_unit.values()))
            target1_event = list(dict.fromkeys(target1_score_unit.values()))
            target2_event = list(dict.fromkeys(target2_score_unit.values()))

            if "root" in args.scoring_constraint:
                base_event = [v.split()[1] if len(v.split()) > 1 else v for v in base_event]
                target1_event = [v.split()[1] if len(v.split()) > 1 else v for v in target1_event]
                target2_event = [v.split()[1] if len(v.split()) > 1 else v for v in target2_event]

            base_score_unit = {}
            target1_score_unit = {}
            target2_score_unit = {}

        if args.global_match == "order-search":
            _, _, best_detail1 = best_mapping_by_tp_variable_fast(base_score_unit, target1_score_unit, embedding_model, alpha=0, beta=1)
            _, _, best_detail2 = best_mapping_by_tp_variable_fast(base_score_unit, target2_score_unit, embedding_model, alpha=0, beta=1)
            total_scores = [best_detail1['total_score'], best_detail2['total_score']]
        else:
            ## Best mapping base-target1
            maps1 = generate_local_mappings(get_all_possible_pairs_map(base_event, target1_event), stories_events, embedding_dicts, mu, VI, args, [base_enrichment, target1_enrichment])
            final_solutions1 = beam_search(base_event, target1_event, maps1, args.top_output)
            max_score1, total_score1 = compute_max_and_total_scores(final_solutions1)
    
            
            if args.global_match == "Beam-search2":
                final_solutions1 = update_mapping_scores(embedding_model, args, final_solutions1, [base_enrichment, target1_enrichment], [base_score_unit, target1_score_unit])
                max_score1, total_score1 = compute_max_and_total_scores(final_solutions1)

            if args.global_match == "Beam-search-min":
                final_solutions1 = get_minimum_score(final_solutions1)
                max_score1, total_score1 = compute_max_and_total_scores(final_solutions1)

            ## Best mapping base-target2
            maps2 = generate_local_mappings(get_all_possible_pairs_map(base_event, target2_event), stories_events, embedding_dicts, mu, VI, args, [base_enrichment, target2_enrichment])
            final_solutions2 = beam_search(base_event, target2_event, maps2, args.top_output)
            max_score2, total_score2 = compute_max_and_total_scores(final_solutions2)

            
            if args.global_match == "Beam-search2":
                final_solutions2 = update_mapping_scores(embedding_model, args, final_solutions2, [base_enrichment, target2_enrichment], [base_score_unit, target2_score_unit])
                max_score2, total_score2 = compute_max_and_total_scores(final_solutions2)

            if args.global_match == "Beam-search-min":
                final_solutions2 = get_minimum_score(final_solutions2)
                max_score2, total_score2 = compute_max_and_total_scores(final_solutions2)

            total_scores = [total_score1, total_score2]
                
        max_value = max(total_scores)
        max_indices = [i for i, val in enumerate(total_scores) if val == max_value]
        max_index = random.choice(max_indices)
        
        y_pred.append(max_index)
        if y_true[-1] == y_pred[-1]:
            category_dict[category] += 1
        
        if args.global_match != "order-search":
            append_experiment(args, index, base_story, [target_story1, target_story2], correct_answer, [maps1, maps2], [final_solutions1, final_solutions2])
    
    
    result = round(metrics.accuracy_score(y_true, y_pred), 3)
    for key in category_dict:
        category_dict[key] = round(category_dict[key]/category_dict_ref[key], 3)
        
    return result, category_dict

### full data mcq

def extract_all_units_mcq(mcq_data, mcq_event, mcq_enrichment, mcq_score_unit, args):
    stories_events = {}
    for index in tqdm(range(len(mcq_data))):
        base_story = mcq_data[index]["source"].strip()
        target_story1 = mcq_data[index]["choices"][0].strip()
        target_story2 = mcq_data[index]["choices"][1].strip()
        target_story3 = mcq_data[index]["choices"][2].strip()
        target_story4 = mcq_data[index]["choices"][3].strip()
        
        sample_event = mcq_event[index]
        base_event = sample_event["base"]
        target1_event = sample_event["target1"]
        target2_event = sample_event["target2"]
        target3_event = sample_event["target3"]
        target4_event = sample_event["target4"]
        
        
        if len(mcq_enrichment)>0 : 
            sample_enrichment = mcq_enrichment[index]
            base_enrichment = sample_enrichment["base"]
            target1_enrichment = sample_enrichment["target1"]
            target2_enrichment = sample_enrichment["target2"]
            target3_enrichment = sample_enrichment["target3"]
            target4_enrichment = sample_enrichment["target4"]
        else:
            base_enrichment = {}
            target1_enrichment = {}
            target2_enrichment = {}
            target3_enrichment = {}
            target4_enrichment = {}

        
        sample_score_unit = mcq_score_unit[index]
        base_score_unit = sample_score_unit["base"]
        target1_score_unit = sample_score_unit["target1"]
        target2_score_unit = sample_score_unit["target2"]
        target3_score_unit = sample_score_unit["target3"]
        target4_score_unit = sample_score_unit["target4"]

        if "superunit" in args.scoring_unit:
            base_event = list(base_event.keys())
            target1_event = list(target1_event.keys())
            target2_event = list(target2_event.keys())
            target3_event = list(target3_event.keys())
            target4_event = list(target4_event.keys())

        if "only_abstractions" in args.scoring_constraint: 
            base_event = list(dict.fromkeys(base_score_unit.values()))
            target1_event = list(dict.fromkeys(target1_score_unit.values()))
            target2_event = list(dict.fromkeys(target2_score_unit.values()))
            target3_event = list(dict.fromkeys(target3_score_unit.values()))
            target4_event = list(dict.fromkeys(target4_score_unit.values()))

            if "root" in args.scoring_constraint:
                base_event = [v.split()[1] if len(v.split()) > 1 else v for v in base_event]
                target1_event = [v.split()[1] if len(v.split()) > 1 else v for v in target1_event]
                target2_event = [v.split()[1] if len(v.split()) > 1 else v for v in target2_event]
                target3_event = [v.split()[1] if len(v.split()) > 1 else v for v in target3_event]
                target4_event = [v.split()[1] if len(v.split()) > 1 else v for v in target4_event]

            base_score_unit = {}
            target1_score_unit = {}
            target2_score_unit = {}
            target3_score_unit = {}
            target4_score_unit = {}

        
        
        stories_events = get_pairs_update(get_all_possible_pairs_map(base_event, target1_event), args, [base_enrichment, target1_enrichment], [base_score_unit, target1_score_unit], stories_events)
        stories_events = get_pairs_update(get_all_possible_pairs_map(base_event, target2_event), args, [base_enrichment, target2_enrichment], [base_score_unit, target2_score_unit], stories_events)
        stories_events = get_pairs_update(get_all_possible_pairs_map(base_event, target3_event), args, [base_enrichment, target3_enrichment], [base_score_unit, target3_score_unit], stories_events)
        stories_events = get_pairs_update(get_all_possible_pairs_map(base_event, target4_event), args, [base_enrichment, target4_enrichment], [base_score_unit, target4_score_unit], stories_events)

    return stories_events



def mapping_pipeline_MCQ(embedding_model, mcq_data, mcq_event, mcq_enrichment, mcq_score_unit, args):
    ## generates sentenses
    stories_events = extract_all_units_mcq(mcq_data, mcq_event, mcq_enrichment, mcq_score_unit, args)

    unique_values = list(dict.fromkeys(chain.from_iterable(stories_events.values())))


    if args.scoring_constraint == "mahalanobis":
        embedding_dicts = build_embedding_cache(embedding_model, unique_values, batch_size=1024, normalize=False, to_numpy=True, show_progress=True)
        mu, VI = fit_mahalanobis_from_dict(embedding_dicts, reg=1e-4, use_shrinkage=True)

    else:
        embedding_dicts = build_embedding_cache(embedding_model, unique_values)
        mu = 0
        VI = 0

    y_true = []
    y_pred = []
    for index in tqdm(range(len(mcq_data))):
        base_story = mcq_data[index]["source"].strip()
        target_story1 = mcq_data[index]["choices"][0].strip()
        target_story2 = mcq_data[index]["choices"][1].strip()
        target_story3 = mcq_data[index]["choices"][2].strip()
        target_story4 = mcq_data[index]["choices"][3].strip()

        correct_answer = int(mcq_data[index]['answer'])
        y_true.append(correct_answer)
        
        sample_event = mcq_event[index]
        base_event = sample_event["base"]
        target1_event = sample_event["target1"]
        target2_event = sample_event["target2"]
        target3_event = sample_event["target3"]
        target4_event = sample_event["target4"]
        
        
        if len(mcq_enrichment)>0 : 
            sample_enrichment = mcq_enrichment[index]
            base_enrichment = sample_enrichment["base"]
            target1_enrichment = sample_enrichment["target1"]
            target2_enrichment = sample_enrichment["target2"]
            target3_enrichment = sample_enrichment["target3"]
            target4_enrichment = sample_enrichment["target4"]
        else:
            base_enrichment = {}
            target1_enrichment = {}
            target2_enrichment = {}
            target3_enrichment = {}
            target4_enrichment = {}

        
        sample_score_unit = mcq_score_unit[index]
        base_score_unit = sample_score_unit["base"]
        target1_score_unit = sample_score_unit["target1"]
        target2_score_unit = sample_score_unit["target2"]
        target3_score_unit = sample_score_unit["target3"]
        target4_score_unit = sample_score_unit["target4"]

        if "superunit" in args.scoring_unit:
            base_event = list(base_event.keys())
            target1_event = list(target1_event.keys())
            target2_event = list(target2_event.keys())
            target3_event = list(target3_event.keys())
            target4_event = list(target4_event.keys())

        if "only_abstractions" in args.scoring_constraint: 
            base_event = list(dict.fromkeys(base_score_unit.values()))
            target1_event = list(dict.fromkeys(target1_score_unit.values()))
            target2_event = list(dict.fromkeys(target2_score_unit.values()))
            target3_event = list(dict.fromkeys(target3_score_unit.values()))
            target4_event = list(dict.fromkeys(target4_score_unit.values()))

            if "root" in args.scoring_constraint:
                base_event = [v.split()[1] if len(v.split()) > 1 else v for v in base_event]
                target1_event = [v.split()[1] if len(v.split()) > 1 else v for v in target1_event]
                target2_event = [v.split()[1] if len(v.split()) > 1 else v for v in target2_event]
                target3_event = [v.split()[1] if len(v.split()) > 1 else v for v in target3_event]
                target4_event = [v.split()[1] if len(v.split()) > 1 else v for v in target4_event]

            base_score_unit = {}
            target1_score_unit = {}
            target2_score_unit = {}
            target3_score_unit = {}
            target4_score_unit = {}

        if args.global_match == "order-search":
            _, _, best_detail1 = best_mapping_by_tp_variable_fast(base_score_unit, target1_score_unit, embedding_model, alpha=0, beta=1)
            _, _, best_detail2 = best_mapping_by_tp_variable_fast(base_score_unit, target2_score_unit, embedding_model, alpha=0, beta=1)
            _, _, best_detail3 = best_mapping_by_tp_variable_fast(base_score_unit, target3_score_unit, embedding_model, alpha=0, beta=1)
            _, _, best_detail4 = best_mapping_by_tp_variable_fast(base_score_unit, target4_score_unit, embedding_model, alpha=0, beta=1)
            total_scores = [best_detail1['total_score'], best_detail2['total_score'], best_detail3['total_score'], best_detail4['total_score']]
        else:
        ## Best mapping base-target1
            maps1 = generate_local_mappings(get_all_possible_pairs_map(base_event, target1_event), stories_events, embedding_dicts, mu, VI, args, [base_enrichment, target1_enrichment])
            final_solutions1 = beam_search(base_event, target1_event, maps1, args.top_output)
            max_score1, total_score1 = compute_max_and_total_scores(final_solutions1)
            
            if args.global_match == "Beam-search2":
                final_solutions1 = update_mapping_scores(embedding_model, args, final_solutions1, [base_enrichment, target1_enrichment], [base_score_unit, target1_score_unit])
                max_score1, total_score1 = compute_max_and_total_scores(final_solutions1)

            if args.global_match == "Beam-search-min":
                final_solutions1 = get_minimum_score(final_solutions1)
                max_score1, total_score1 = compute_max_and_total_scores(final_solutions1)

        ## Best mapping base-target2
            maps2 = generate_local_mappings(get_all_possible_pairs_map(base_event, target2_event), stories_events, embedding_dicts, mu, VI, args, [base_enrichment, target2_enrichment])
            final_solutions2 = beam_search(base_event, target2_event, maps2, args.top_output)
            max_score2, total_score2 = compute_max_and_total_scores(final_solutions2)

            
            if args.global_match == "Beam-search2":
                final_solutions2 = update_mapping_scores(embedding_model, args, final_solutions2, [base_enrichment, target2_enrichment], [base_score_unit, target2_score_unit])
                max_score2, total_score2 = compute_max_and_total_scores(final_solutions2)
    
            if args.global_match == "Beam-search-min":
                final_solutions2 = get_minimum_score(final_solutions2)
                max_score2, total_score2 = compute_max_and_total_scores(final_solutions2)
        
            
            maps3 = generate_local_mappings(get_all_possible_pairs_map(base_event, target3_event), stories_events, embedding_dicts, mu, VI, args, [base_enrichment, target3_enrichment])
            final_solutions3 = beam_search(base_event, target3_event, maps3, args.top_output)
            max_score3, total_score3 = compute_max_and_total_scores(final_solutions3)
            
            
            if args.global_match == "Beam-search2":
                final_solutions3 = update_mapping_scores(embedding_model, args, final_solutions3, [base_enrichment, target3_enrichment], [base_score_unit, target3_score_unit])
                max_score3, total_score3 = compute_max_and_total_scores(final_solutions3)
    
            if args.global_match == "Beam-search-min":
                final_solutions3 = get_minimum_score(final_solutions3)
                max_score3, total_score3 = compute_max_and_total_scores(final_solutions3)
        
            
            
            maps4 = generate_local_mappings(get_all_possible_pairs_map(base_event, target4_event), stories_events, embedding_dicts, mu, VI, args, [base_enrichment, target4_enrichment])
            final_solutions4 = beam_search(base_event, target4_event, maps4, args.top_output)
            max_score4, total_score4 = compute_max_and_total_scores(final_solutions4)
            
            
            if args.global_match == "Beam-search2":
                final_solutions4 = update_mapping_scores(embedding_model, args, final_solutions4, [base_enrichment, target4_enrichment], [base_score_unit, target4_score_unit])
                max_score4, total_score4 = compute_max_and_total_scores(final_solutions4)
    
            if args.global_match == "Beam-search-min":
                final_solutions4 = get_minimum_score(final_solutions4)
                max_score4, total_score4 = compute_max_and_total_scores(final_solutions4)
        
            
            
            
            total_scores = [total_score1, total_score2, total_score3, total_score4]
                

        max_value = max(total_scores)
        max_indices = [i for i, val in enumerate(total_scores) if val == max_value]
        max_index = random.choice(max_indices)

        y_pred.append(max_index)
        
        if args.global_match != "order-search":
            append_experiment(args, index, base_story, [target_story1, target_story2, target_story3, target_story4], correct_answer, [maps1, maps2, maps3, maps4], [final_solutions1, final_solutions2, final_solutions3, final_solutions4])
        
    result = round(metrics.accuracy_score(y_true, y_pred), 3)
    return result, "-"   



########## New clean method (TODO: I should remove this comment at the end)
def extract_story_units(main_data, main_units, args):
    all_stories_events = {}

    for index in tqdm(range(len(main_data))):
        sample_unit = main_units[index]
        base_unit = sample_unit["base"]

        target_keys = sorted(key for key in sample_unit if key.startswith("target"))

        for target_key in target_keys:
            target_unit = sample_unit[target_key]
            all_stories_events = pairs_update(get_all_possible_pairs_map(base_unit, target_unit), sample_unit, all_stories_events, args)

    return all_stories_events

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


def Greedy_mapping(main_data, main_units, embedding_model, args):

    all_stories_events = extract_story_units(main_data, main_units, args)
    unique_values = list(dict.fromkeys(chain.from_iterable(all_stories_events.values())))
    embedding_dicts = build_embedding_cache(embedding_model, unique_values)


    y_true = []
    y_pred = []
    category_dict_ref = {'low-near': 294, 'low-far': 294, 'high-near': 253, 'high-far': 254}
    category_dict = {'low-near': 0, 'low-far': 0, 'high-near': 0, 'high-far': 0}

    for index in tqdm(range(len(main_data))):
        sample_unit = main_units[index]
        base_unit = sample_unit["base"]

        correct_answer, category = get_correct_answer(main_data, index, args)
        y_true.append(correct_answer)

        target_keys = sorted(key for key in sample_unit if key.startswith("target"))

        total_scores = []

        for target_key in target_keys:
            target_unit = sample_unit[target_key]

            current_maps = generate_local_mappings(get_all_possible_pairs_map(base_unit, target_unit), all_stories_events, embedding_dicts, main_unitsو args)
            current_final_solutions = beam_search(base_unit, target_unit, current_maps, args.config["top_output"])
            current_max_score, current_total_score = compute_max_and_total_scores(current_final_solutions)

            total_scores.append(current_total_score)
                

        max_index = random.choice([i for i, val in enumerate(total_scores) if val == max(total_scores)])
        y_pred.append(max_index)

        if args.dataset == "ARN" and y_true[-1] == y_pred[-1]:
            category_dict[category] += 1
        
    result = round(metrics.accuracy_score(y_true, y_pred), 3)

    if args.dataset == "ARN":
        for key in category_dict:
            category_dict[key] = round(category_dict[key]/category_dict_ref[key], 3)
        return result, category_dict 
    elif args.dataset == "MCQ":
        return result, "-"
            




def extract_kernel_names_stages(data):
    result = {}
    for idx, sections in data.items():
        result[idx] = {}
        for section, tps in sections.items():
            kernel_list = [info['kernel_name'] for info in tps.values()]
            result[idx][section] = kernel_list
    return result

def map_kernel_to_tp(data):
    result = {}
    for idx, sections in data.items():
        result[idx] = {}
        for section, tps in sections.items():
            kernel_map = {info['kernel_name']: tp for tp, info in tps.items()}
            result[idx][section] = kernel_map
    return result
    

        
    
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

    path_units = (
        f"{PATH_UNITS}{model_short}{args.unit}_{data_short}.pkl"
        if args.unit == "events"
        else f"{PATH_ABSTRACTION}{model_short}events_{args.unit}_{data_short}.pkl"
    )

    with open(path_units, "rb") as f:
        main_units = pickle.load(f)

    return main_data, main_units


def run_main_mapping(args):
    print("\n=== Step 1: Loading embedding model ===")
    embedding_model = get_embedding_model()
    
    print("\n=== Step 2: Loading the Dataset and the Units ===")
    if args.dataset == "ARN":
         main_data, main_units = load_data(args)
    elif args.dataset == "MCQ":
        main_data, main_units = load_data(args)

    
    print(f"\n=== Step 3: Run the mapping with {arg.global_map} mapping and {args.scoring_method} scoring and {arg.config} config")
    if arg.global_map == "Greedy":
        accuracy, arn_category_accuracy = Greedy_mapping(main_data, main_units, embedding_model, args)

    elif arg.global_map == "Order":
        accuracy, arn_category_accuracy = 0, 0

    elif arg.global_map == "max_flow":
        accuracy, arn_category_accuracy = 0, 0
    
    print("accuracy: ", accuracy)
    print("arn_category: ", arn_category)
    
    append_results(args, accuracy, arn_category)