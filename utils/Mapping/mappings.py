from itertools import combinations
from typing import List, Tuple, Dict, Set
from tqdm import tqdm

from utils.Mapping.helper_function import *


def get_all_possible_pairs_map(base, target):
    base_comb = list(combinations(base, 2))
    target_comb = list(combinations(target, 2))
    target_comb += [(b, a) for a, b in target_comb]  # flipped versions

    all_mapping = []
    for base_pair in base_comb:
        for target_pair in target_comb:
            all_mapping.append([
                [(base_pair[0], base_pair[1]), (target_pair[0], target_pair[1])],
                [(base_pair[1], base_pair[0]), (target_pair[1], target_pair[0])]
            ])
    return all_mapping
    
    
def extract_base_target_relation(story1, ph1, q_model):
    all_relations = {}
    
    for ph in ph1:
        prompt = create_prompt(story1, ph, ph1, "Causal and Functional")
        ans = query_models(prompt, q_model)
        all_relations = extract_positive_relations(ans.strip(), all_relations)
        prompt = create_prompt(story1, ph, ph1, "Temporal")
        ans = query_models(prompt, q_model)
        all_relations = extract_positive_relations(ans.strip(), all_relations)
        
        
    return all_relations


def compute_score_different_method(units1, units2, s_method, embedding_model):
    
    if s_method == "verbalized":
        sentence1 = " ".join(units1)
        sentence2 = " ".join(units2)
        
        score = similarity(sentence1, sentence2, embedding_model)

    elif s_method == "triple":
        score_sum = 0
        for index_u in range(len(units1)):
            score_sum += similarity(units1[index_u], units2[index_u], embedding_model)
            
        score = round(score_sum / len(units1), 3)
        
    return score
    
    
def score_event_phrases_no_enrichment(args, base_units, target_units, all_score_unit, embedding_model):
    if len(base_units) != len(target_units):
        raise ValueError("base_units and target_units must have the same length.")

    if args.scoring_unit == "stage_abstraction":
        stages_dict = {"TP1" : "Introduction", "TP2" : "Event", "TP3" : "Action", "TP4" : "Challenge", "TP5" : "Conclusion"}
    elif args.scoring_unit == "stage_abstraction2" or args.scoring_unit == "stage_abstraction3":
        stages_dict = {"TP1" : "Introduction", "TP2" : "Event", "TP3" : "Challenge", "TP4" : "Action", "TP5" : "Conclusion"}
        
    if args.scoring_unit == "unit":
        units1 = list(base_units)
        units2 = list(target_units)
        score = compute_score_different_method(units1, units2, args.scoring_method, embedding_model)
        return score, 1
    elif "abstraction" in args.scoring_unit:
        units1 = [all_score_unit[0].get(u, u) for u in base_units]
        units2 = [all_score_unit[1].get(v, v) for v in target_units]
        score = compute_score_different_method(units1, units2, args.scoring_method, embedding_model)
        return score, 1
    elif args.scoring_unit == "stage_abstraction" or args.scoring_unit == "stage_abstraction2" or args.scoring_unit == "stage_abstraction3":
        units1 = list(base_units)
        units2 = list(target_units)
        
        if args.scoring_constraint == "none":
            score = compute_score_different_method(units1, units2, args.scoring_method, embedding_model)
            return score, 1
        else:
            stage1 = [stages_dict.get(all_score_unit[0][u]) for u in base_units] 
            stage2 = [stages_dict.get(all_score_unit[1][v]) for v in target_units]
            
            if args.scoring_constraint == "hard":
                if stage1 != stage2:
                    return 0, 0
                else:
                    score = compute_score_different_method(units1, units2, args.scoring_method, embedding_model)
                    return score, 1
                    
            elif args.scoring_constraint == "soft_simple":
                units1_new = []
                units2_new = []
                for u, s in zip(units1, stage1):
                    units1_new.extend([u, s])
                for u, s in zip(units2, stage2):
                    units2_new.extend([u, s])
                    
                score = compute_score_different_method(units1_new, units2_new, args.scoring_method, embedding_model)
                return score, 1
                
            elif args.scoring_constraint == "soft_parentheses":
                units1_new = []
                units2_new = []
                for u, s in zip(units1, stage1):
                    units1_new.extend([u, f"({s})"])
                for u, s in zip(units2, stage2):
                    units2_new.extend([u, f"({s})"])
                
                score = compute_score_different_method(units1_new, units2_new, args.scoring_method, embedding_model)
                return score, 1
            elif args.scoring_constraint == "soft_sentence":
                units1_new = []
                units2_new = []
                for u, s in zip(units1, stage1):
                    units1_new.extend([u, f"is a {s} and"])
                for u, s in zip(units2, stage2):
                    units2_new.extend([u, f"is a {s} and"])
                    
                if units1_new:
                    units1_new[-1] = units1_new[-1][:-3] + "."
                if units2_new:
                    units2_new[-1] = units2_new[-1][:-3] + "."
                
                score = compute_score_different_method(units1_new, units2_new, args.scoring_method, embedding_model)
                return score, 1
    
        
def score_event_phrases_with_stage_enrichment(args, base_units, target_units, all_enrichment, all_score_unit, embedding_model):
    
    if len(base_units) != len(target_units):
        raise ValueError("base_units and target_units must have the same length.")

    
    if args.scoring_unit == "stage_abstraction":
        stages_dict = {"TP1" : "Introduction", "TP2" : "Event", "TP3" : "Action", "TP4" : "Challenge", "TP5" : "Conclusion"}
    elif args.scoring_unit == "stage_abstraction2" or args.scoring_unit == "stage_abstraction3":
        stages_dict = {"TP1" : "Introduction", "TP2" : "Event", "TP3" : "Challenge", "TP4" : "Action", "TP5" : "Conclusion"}
        
    stage1 = [stages_dict.get(all_enrichment[0][u]) for u in base_units]
    stage2 = [stages_dict.get(all_enrichment[1][v]) for v in target_units]
    
    if args.scoring_unit == "unit":
        units1 = list(base_units)
        units2 = list(target_units)
    elif args.scoring_unit == "abstraction1" or args.scoring_unit == "abstraction2":
        units1 = [all_score_unit[0][u] for u in base_units]
        units2 = [all_score_unit[1][v] for v in target_units]
    
    if args.scoring_constraint == "hard":
        if stage1 != stage2:
            return 0, 0
        else:
            score = compute_score_different_method(units1, units2, args.scoring_method, embedding_model)
            return score, 1
    elif args.scoring_constraint == "soft_simple":
        units1_new = []
        units2_new = []
        for u, s in zip(units1, stage1):
            units1_new.extend([u, s])
        for u, s in zip(units2, stage2):
            units2_new.extend([u, s])
        
        score = compute_score_different_method(units1_new, units2_new, args.scoring_method, embedding_model)
        return score, 1
        
    elif args.scoring_constraint == "soft_parentheses":
        units1_new = []
        units2_new = []
        for u, s in zip(units1, stage1):
            units1_new.extend([u, f"({s})"])
        for u, s in zip(units2, stage2):
            units2_new.extend([u, f"({s})"])
        
        score = compute_score_different_method(units1_new, units2_new, args.scoring_method, embedding_model)
        return score, 1
    elif args.scoring_constraint == "soft_sentence":
        units1_new = []
        units2_new = []
        for u, s in zip(units1, stage1):
            units1_new.extend([u, f"is a {s} and"])
        for u, s in zip(units2, stage2):
            units2_new.extend([u, f"is a {s} and"])

        if units1_new:
            units1_new[-1] = units1_new[-1][:-3] + "."
        if units2_new:
            units2_new[-1] = units2_new[-1][:-3] + "."
        
        score = compute_score_different_method(units1_new, units2_new, args.scoring_method, embedding_model)
        return score, 1
        
def score_event_phrases_with_stage_rel_enrichment(args, base_units, target_units, all_enrichment, all_score_unit, embedding_model):
    if len(base_units) != len(target_units):
        raise ValueError("base_units and target_units must have the same length.")
        
    if args.scoring_unit == "unit":
        units1 = list(base_units)
        units2 = list(target_units)
    elif args.scoring_unit == "abstraction1" or args.scoring_unit == "abstraction2" or args.scoring_unit == "abstraction3" or args.scoring_unit == "abstraction4":
        units1 = [all_score_unit[0][u] for u in base_units]
        units2 = [all_score_unit[1][v] for v in target_units]
        
    if args.enrichment == "stage_rel_0":
        stage1_new = {event: details['label'] for details in all_enrichment[0]['stages'].values() for event in details['events']}
        stage2_new = {event: details['label'] for details in all_enrichment[1]['stages'].values() for event in details['events']}
        
        stage1 = [stage1_new.get(u, "MISSING UNIT") for u in base_units]
        stage2 = [stage2_new.get(v, "MISSING UNIT") for v in target_units]
        
        
        if args.scoring_constraint == "soft_parentheses":
            units1_new = []
            units2_new = []
            for u, s in zip(units1, stage1):
                units1_new.extend([u, f"({s})"])
            for u, s in zip(units2, stage2):
                units2_new.extend([u, f"({s})"])
            
            score = compute_score_different_method(units1_new, units2_new, args.scoring_method, embedding_model)
            return score, 1
        
    elif args.enrichment == "stage_rel_1":
        rels1 = all_enrichment[0]['relations']
        rels2 = all_enrichment[1]['relations']
        
        
        if base_units[0] + "#" + base_units[1] in rels1:
            rel1 = rels1[base_units[0] + "#" + base_units[1]]
        else:
            return 0, 0
            
        if target_units[0] + "#" + target_units[1] in rels2:
            rel2 = rels2[target_units[0] + "#" + target_units[1]]
        else:
            return 0, 0
        
        
        if args.scoring_constraint == "hard":
            if rel1 != rel2:
                return 0, 0
                
            score = compute_score_different_method(units1, units2, args.scoring_method, embedding_model)
            return score, 1
            
        elif args.scoring_constraint == "soft_parentheses":
            units1_new = [units1[0], f"({rel1})", units1[1]]
            units2_new = [units2[0], f"({rel2})", units2[1]]
            
            score = compute_score_different_method(units1_new, units2_new, args.scoring_method, embedding_model)
            return score, 1
        
        
    
    
def get_best_pair_mapping(embedding_model, available_maps, args, all_enrichment, all_score_unit):
    results = []
    for mapping in available_maps:
        total_score = 0
        coverage = 0
        for direction in mapping:
            b1, b2 = direction[0]
            t1, t2 = direction[1]
        
                
            if args.unit == "unit_event_phrases" or args.unit == "unit_event_phrases_2" or args.unit == "unit_event_phrases_3":
                if args.enrichment == "none":
                    score, cov = score_event_phrases_no_enrichment(args, [b1, b2], [t1, t2], all_score_unit, embedding_model)
                elif args.enrichment == "stage":
                    score, cov = score_event_phrases_with_stage_enrichment(args, [b1, b2], [t1, t2], all_enrichment, all_score_unit, embedding_model)
                elif "stage_rel" in args.enrichment:
                    score, cov = score_event_phrases_with_stage_rel_enrichment(args, [b1, b2], [t1, t2], all_enrichment, all_score_unit, embedding_model)
                    
                    
            
            total_score += round(score, 3)
            coverage += cov


        results.append({
            "best_mapping": mapping[0],
            "best_score": round(total_score, 3),
            "coverage": coverage
        })

    results.sort(key=lambda x: x["best_score"], reverse=True)
    return results


##### New methods on full dataset

# def generate_scores_sent(args, final_units):
#     if args.scoring_method == "verbalized":
#         sentence1 = " ".join(final_units)
#         return [sentence1]
#     elif args.scoring_method == "triple":
#         return final_units
#     elif args.scoring_method == "triple1":
#         final_units = [v.replace("_", " ").lower() for v in final_units]
#         new_units = [v for v1 in final_units for v in v1.split()[:2]]
#         return new_units
#     elif args.scoring_method == "triple2":
#         final_units = [v.replace("_", " ").lower() for v in final_units]
#         new_units = [v.split()[1] if len(v.split()) > 1 else v for v in final_units]
#         return new_units


# def score_event_phrases_no_enrichment_new(args, given_units, given_all_score_unit, given_enrichment):
        
#     if args.scoring_unit == "unit" or "only_abstractions" in args.scoring_constraint or "superunit" in args.scoring_unit:
#         if args.scoring_constraint == "soft":
#             stages_dict_pre = {"TP1" : "Introduction", "TP2" : "Event", "TP3" : "Challenge", "TP4" : "Action", "TP5" : "Conclusion"}
#             units1 = [item for u in given_units for item in (u, stages_dict_pre.get(given_enrichment.get(u, u), ""))]
#         else:
#             units1 = list(given_units)
#         return generate_scores_sent(args, units1)
#     elif "abstraction" in args.scoring_unit:
#         if args.scoring_constraint == "soft":
#             dicts = [given_all_score_unit, given_enrichment]
#             units1 = [d.get(u, u) for u in given_units for d in dicts]
#         else:
#             units1 = [given_all_score_unit.get(u, u) for u in given_units]

#         return generate_scores_sent(args, units1)    


def format_units_for_scoring(units, args):
    # Modify unit text before scoring.
    # Example: remove underscores, normalize casing, etc.
    return units


def prepare_units_for_scoring(given_units, all_units, args):
    # Change or enrich the units depending on the scoring setup.
    # Example: for soft scoring, add related abstraction units.
    if args.unit == "events":
        final_units = list(given_units)
    else:
        # TODO: handle abstraction-based units here.
        final_units = list(given_units)

    return format_units_for_scoring(final_units, args)


def score_pair(pair, all_units, args):
    final_units = prepare_units_for_scoring(pair, all_units, args)
    return generate_scores_sent(final_units, args)


def get_pairs_update(available_maps, units, args, all_stories_events): 
    # This function is the main function to loop over the mappings
    result_stories_events = dict(all_stories_events)
    for mapping in available_maps:
        for direction in mapping:
            b1, b2 = direction[0]
            t1, t2 = direction[1]

            if f"{b1}#{b2}" not in result_stories_events:
                result_stories_events[f"{b1}#{b2}"] = score_pair([b1, b2], units, args)
            if f"{t1}#{t2}" not in result_stories_events:
                result_stories_events[f"{t1}#{t2}"] = score_pair([t1, t2], units, args)

    return result_stories_events

def final_mahalanobis_similarity(B, T, mu, VI):
    B = np.asarray(B, dtype=np.float64)
    T = np.asarray(T, dtype=np.float64)
    mu = np.asarray(mu, dtype=np.float64)
    VI = np.asarray(VI, dtype=np.float64)

    D = (B - mu) - (T - mu)                    # (m, d)
    d2 = np.einsum('ij,ij->i', D @ VI, D)      # squared Mahalanobis per pair
    d2 = np.maximum(d2, 0.0)                   # numerical guard
    sims = np.exp(-0.5 * d2)                   # RBF similarity
    return float(sims.mean())

def safe_int(enrichments, i_position, key, default=100):
    try:
        return int(enrichments[i_position][key])
    except Exception:
        return default

def generate_local_mappings(available_maps, all_stories_events, embedding_dicts, mu, VI, args, enrichments):
    results = []
    for mapping in available_maps:
        total_score = 0
        coverage = 0
        for direction in mapping:
            b1, b2 = direction[0]
            t1, t2 = direction[1]

            if (args.scoring_constraint == "hard") and ("abstraction" in args.enrichment or "stage" in args.enrichment or "superunit" in args.enrichment):
                # b1_pos = safe_int(enrichments, 0, b1)
                # b2_pos = safe_int(enrichments, 0, b2)
                # t1_pos = safe_int(enrichments, 1, t1)
                # t2_pos = safe_int(enrichments, 1, t2)

                # if (b1_pos < b2_pos and t1_pos > t2_pos) or (b1_pos > b2_pos and t1_pos < t2_pos):
                #     total_score += 0
                #     coverage += 1
                #     continue 

                b1_pos = enrichments[0].get(b1, "").strip()
                b2_pos = enrichments[0].get(b2, "").strip()
                t1_pos = enrichments[1].get(t1, "").strip()
                t2_pos = enrichments[1].get(t2, "").strip()




                if b1_pos != t1_pos or b2_pos != t2_pos:
                    continue

                


            base_values_arr = all_stories_events[f"{b1}#{b2}"]
            target_values_arr = all_stories_events[f"{t1}#{t2}"]


            B = np.stack([embedding_dicts[x] for x in base_values_arr])
            T = np.stack([embedding_dicts[x] for x in target_values_arr])

            if args.scoring_constraint == "mahalanobis":
                score = final_mahalanobis_similarity(B, T, mu, VI)
            else:
                th12 = 0.1
                if "condition" in args.scoring_constraint:
                    if np.all([np.sum(B[0] * T[0]) > th12, np.sum(B[2] * T[2]) > th12]):
                        score = float(np.mean(np.sum(B[[1, 3]] * T[[1, 3]], axis=1)))
                    else:
                        score = 0.0

                    # if np.all([np.sum(B[1] * T[1]) > th12, np.sum(B[3] * T[3]) > th12]):
                    #     # score = float(np.mean(np.sum(B * T, axis=1)))
                    #     score = float(np.average(np.sum(B * T, axis=1), weights=[1, 2, 1, 2]))
                    # else:
                    #     score = 0.0
                else:
                    n = min(B.shape[0], T.shape[0])
                    score = float(np.mean(np.sum(B[:n] * T[:n], axis=1)))
                    #score = float(np.mean(np.sum(B * T, axis=1)))


            total_score += score
            coverage += 1

        results.append({
            "best_mapping": mapping[0],
            "best_score": round(total_score, 3),
            "coverage": coverage
        })

    results.sort(key=lambda x: x["best_score"], reverse=True)
    return results


def get_best_pair_mapping_for_current_iteration(available_maps, all_results, depth):
    flat = set()
    for pair in available_maps:
        flat.add(tuple(pair[0]))
        flat.add(tuple(pair[1]))

    new_results = [r for r in all_results if tuple(r["best_mapping"]) in flat]
    return new_results[:depth], new_results


def check_if_valid(pair_map, base_mapped, base_mapped_set, target_mapped, target_mapped_set, indices):
    b1, b2 = pair_map[0][0], pair_map[0][1]
    t1, t2 = pair_map[1][0], pair_map[1][1]

    if b1 in base_mapped_set and b2 in base_mapped_set:
        return False
    if b1 in base_mapped_set and t1 != target_mapped[indices["base"][b1]]:
        return False
    if b2 in base_mapped_set and t2 != target_mapped[indices["base"][b2]]:
        return False
    if t1 in target_mapped_set and t2 in target_mapped_set:
        return False
    if t1 in target_mapped_set and b1 != base_mapped[indices["target"][t1]]:
        return False
    if t2 in target_mapped_set and b2 != base_mapped[indices["target"][t2]]:
        return False
    return True


def update_paris_map(pairs_map, base_mapped, target_mapped, indices):
    return [
        m for m in pairs_map if check_if_valid(
            m[0],
            base_mapped,
            set(base_mapped),
            target_mapped,
            set(target_mapped),
            indices
        )
    ]
    
