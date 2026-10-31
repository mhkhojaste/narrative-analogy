from itertools import combinations
from typing import List, Tuple, Dict, Set
from tqdm import tqdm
from scipy.spatial.distance import mahalanobis

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
    
 

def format_units_for_scoring(units, args):
    if "text_modify" not in args.config:
        return units
    elif args.config["text_modify"] == "split":
        final_units = [v.replace("_", " ").lower() for v in units]
        new_units = [v for v1 in final_units for v in v1.split()[:2]]
        return new_units
    elif args.config["text_modify"] == "only_root":
        final_units = [v.replace("_", " ").lower() for v in units]
        new_units = [v.split()[1] if len(v.split()) > 1 else v for v in final_units]
        return new_units


def prepare_units_for_scoring(given_units, all_units, args):
    if args.unit == "events":
        final_units = list(given_units)
    elif args.unit == "conceptual0":
        final_units = [all_units.get(u, u) for u in given_units]
    elif args.unit == "conceptual1":
        final_units = [all_units.get(u, u) for u in given_units]
    elif args.unit == "conceptual0_evaluative":
        final_units = [value for u in given_units for value in all_units.get(u, [u])]
    elif args.unit == "stage":
        final_units = list(given_units)
    elif args.unit == "stage_arc":
        stages_dict_pre = {"TP1" : "Introduction", "TP2" : "Event", "TP3" : "Challenge", "TP4" : "Action", "TP5" : "Conclusion"}
        final_units = [item for u in given_units for item in (u, stages_dict_pre.get(all_units.get(u, ""), ""))]

    return final_units


def score_pair(pair, all_units, args):
    final_units = prepare_units_for_scoring(pair, all_units, args)
    return format_units_for_scoring(final_units, args)


def pairs_update(available_maps, units, stories_events, nli_pairs, args):
    result_stories_events = dict(stories_events)

    for mapping in available_maps:
        for direction in mapping:
            b1, b2 = direction[0]
            t1, t2 = direction[1]

            base_updated_pairs = score_pair([b1, b2], units[0], args)
            target_updated_pairs = score_pair([t1, t2], units[1], args)

            if f"{b1}#{b2}" not in result_stories_events:
                result_stories_events[f"{b1}#{b2}"] = base_updated_pairs

            if f"{t1}#{t2}" not in result_stories_events:
                result_stories_events[f"{t1}#{t2}"] = target_updated_pairs

            base_values = result_stories_events[f"{b1}#{b2}"]
            target_values = result_stories_events[f"{t1}#{t2}"]

            n = min(len(base_values), len(target_values))

            for i_n in range(n):
                nli_pairs.append((
                    base_values[i_n],
                    target_values[i_n]
                ))

    return result_stories_events, nli_pairs




def final_mahalanobis_similarity(B, T, VI, bandwidth=25.0):
    B = np.asarray(B, dtype=np.float64)
    T = np.asarray(T, dtype=np.float64)

    n = min(len(B), len(T))

    distances = np.array([
        mahalanobis(B[i], T[i], VI)
        for i in range(n)
    ])

    similarities = np.exp(
        -(distances ** 2) / (2 * bandwidth ** 2)
    )

    return float(np.mean(similarities))

def generate_local_mappings(available_maps, all_stories_events, embedding_dicts, units, VI, nli_cache, args):
    results = []
    for mapping in available_maps:
        total_score = 0
        coverage = 0
        for direction in mapping:
            b1, b2 = direction[0]
            t1, t2 = direction[1]

            base_values_arr = all_stories_events[f"{b1}#{b2}"]
            target_values_arr = all_stories_events[f"{t1}#{t2}"]

            B = np.stack([embedding_dicts[x] for x in base_values_arr])
            T = np.stack([embedding_dicts[x] for x in target_values_arr])

            if args.scoring_method == "mahalanobis":
                score = final_mahalanobis_similarity(B, T, VI)
            elif args.scoring_method == "nli":
                n = min(B.shape[0], T.shape[0])
                scores = []

                for i_n in range(n):
                    p_contra, p_neutral, p_ent = nli_cache[
                        (base_values_arr[i_n], target_values_arr[i_n])
                    ]

                    raw_cosine = float(np.dot(B[i_n], T[i_n]))
                    nonnegative_cosine = max(0.0, raw_cosine)
                    soft_sign = p_ent + p_neutral - p_contra

                    scores.append(nonnegative_cosine * soft_sign)

                score = float(np.min(scores)) if scores else -10.0
            else:
                n = min(B.shape[0], T.shape[0])
                score = float(np.mean(np.sum(B[:n] * T[:n], axis=1)))

            total_score += score
            coverage += 1

        results.append({
            "best_mapping": mapping[0],
            "best_score": round(total_score, 3),
            "coverage": coverage
        })

    results.sort(key=lambda x: x["best_score"], reverse=True)
    return results

def safe_int(enrichments, i_position, key, default=100):
    try:
        return int(enrichments[i_position][key])
    except Exception:
        return default


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
    
