import copy
from utils.Mapping.mappings import *

def beam_search(base, target, result_list, top_output):

    solutions = []

    # Step 1: Try top N initial seeds
    for result in result_list[:top_output]:
        b1, b2 = result["best_mapping"][0][0], result["best_mapping"][0][1]
        t1, t2 = result["best_mapping"][1][0], result["best_mapping"][1][1]
        
        if round(result["best_score"], 6) == 0:
            continue

        # Create base solution
        solution = {
            "mapping": [f"{b1} --> {t1}", f"{b2} --> {t2}"],
            "relations": [result["best_mapping"]],
            "scores": [result["best_score"]],
            "coverage": [result["coverage"]],
            "score": result["best_score"],
            "actual_base": [b1, b2],
            "actual_target": [t1, t2],
            "actual_indecies": {
                "base": {b1: 0, b2: 1},
                "target": {t1: 0, t2: 1}
            },
            "length": 2
        }

        # Prepare working pool
        remaining = [r for r in result_list if r != result]

        # Step 2: Greedily add valid mappings
        while remaining:
            valid = []
            for r in remaining:
                if check_if_valid(
                    r["best_mapping"],
                    solution["actual_base"],
                    set(solution["actual_base"]),
                    solution["actual_target"],
                    set(solution["actual_target"]),
                    solution["actual_indecies"]
                ):
                    valid.append(r)

            if not valid:
                break

            # Pick best valid match
            next_result = max(valid, key=lambda r: r["best_score"])
            if round(next_result["best_score"], 6) == 0:
                break
            
            remaining.remove(next_result)

            pair = next_result["best_mapping"]
            b1, b2 = pair[0][0], pair[0][1]
            t1, t2 = pair[1][0], pair[1][1]

            solution["relations"].append(pair)
            solution["scores"].append(round(next_result["best_score"], 3))
            solution["coverage"].append(next_result["coverage"])
            solution["score"] += next_result["best_score"]
            solution["score"] = round(solution["score"], 3)

            if b1 not in solution["actual_base"] and t1 not in solution["actual_target"]:
                solution["actual_base"].append(b1)
                solution["actual_target"].append(t1)
                solution["actual_indecies"]["base"][b1] = len(solution["actual_base"]) - 1
                solution["actual_indecies"]["target"][t1] = len(solution["actual_target"]) - 1

            if b2 not in solution["actual_base"] and t2 not in solution["actual_target"]:
                solution["actual_base"].append(b2)
                solution["actual_target"].append(t2)
                solution["actual_indecies"]["base"][b2] = len(solution["actual_base"]) - 1
                solution["actual_indecies"]["target"][t2] = len(solution["actual_target"]) - 1

            solution["mapping"] = [
                f"{b} --> {t}" for b, t in zip(solution["actual_base"], solution["actual_target"])
            ]
            solution["length"] = len(solution["actual_base"])

        # Save this solution
        solutions.append(solution)

    # Return top solutions by length and score
    return sorted(solutions, key=lambda s: (s["length"], s["score"]), reverse=True)
