import copy
import hashlib
import json
import pickle
from pathlib import Path

import pandas as pd

from utils.Extraction.abstraction_extraction import PATH_UNITS, build_all_prompts_abstraction
from utils.helper_utils import get_openai_client, model_short_dict


API_MODEL = "gpt-5.2-2025-12-11"
DEFAULT_JOB_DIRECTORY = "Data_new/OpenAI_Batches"


def get_abstraction_prompt_cache_key(prompt):
    stable_prefix, separator, _ = prompt.partition("### Your Turn")

    if not separator:
        return None

    prefix_hash = hashlib.sha256(stable_prefix.encode("utf-8")).hexdigest()[:20]
    return f"abstraction:{prefix_hash}"


def get_batch_config(args):
    config = args.config if isinstance(args.config, dict) else {}
    abstraction_task = config.get("abstraction_task")

    if not abstraction_task:
        raise ValueError("The config must contain 'abstraction_task'.")

    return config, abstraction_task


def load_experiment_data(args):
    if args.dataset == "ARN":
        dataset_data = pd.read_csv("Data/Datasets/Analogical Reasoning on Narratives (ARN) dataset.xlsx - Sheet1.csv")
    elif args.dataset == "MCQ":
        with open("Data/Datasets/storyanalogy_multiple_choice.json", encoding="utf-8") as dataset_file:
            dataset_data = json.load(dataset_file)
    else:
        raise ValueError(f"Unsupported dataset: {args.dataset}")

    model_short = model_short_dict.get(args.model)

    if model_short is None:
        raise ValueError(f"No short model name configured for {args.model}.")

    dataset_suffix = args.dataset.lower()
    event_path = f"{PATH_UNITS}{model_short}{args.unit}_{dataset_suffix}.pkl"

    with open(event_path, "rb") as event_file:
        dataset_event = pickle.load(event_file)

    return dataset_data, dataset_event, event_path


def make_job_name(args, abstraction_task, config):
    configured_job_name = config.get("job_name")

    if configured_job_name:
        return str(configured_job_name)

    model_name = args.model.replace(".", "_").replace("/", "_")
    return f"{model_name}_{args.dataset.lower()}_{abstraction_task}_{args.unit}"


def submit_abstraction_batch(args):
    if args.model != "GPT-5.2":
        raise ValueError("This Batch uploader currently supports only GPT-5.2.")

    config, abstraction_task = get_batch_config(args)
    prompt_args = copy.copy(args)
    prompt_args.task = abstraction_task
    dataset_data, dataset_event, event_path = load_experiment_data(args)
    prompts, index_map = build_all_prompts_abstraction(dataset_data, dataset_event, args.dataset, prompt_args)

    if len(prompts) != len(index_map):
        raise ValueError("Prompt/index-map size mismatch: " f"{len(prompts)} prompts and {len(index_map)} mappings.")

    unique_prompts = list(dict.fromkeys(prompts))
    prompt_to_custom_id = {prompt: f"prompt-{prompt_index:06d}" for prompt_index, prompt in enumerate(unique_prompts)}
    prompt_custom_ids = [prompt_to_custom_id[prompt] for prompt in prompts]
    serializable_index_map = [[int(row_index), str(field_name)] for row_index, field_name in index_map]

    print(f"Total prompts: {len(prompts)}")
    print(f"Unique prompts: {len(unique_prompts)}")
    print(f"Removed duplicate prompts: {len(prompts) - len(unique_prompts)}")

    job_directory = Path(config.get("job_directory", DEFAULT_JOB_DIRECTORY))
    job_directory.mkdir(parents=True, exist_ok=True)
    job_name = make_job_name(args, abstraction_task, config)
    input_path = job_directory / f"{job_name}.input.jsonl"
    state_path = job_directory / f"{job_name}.state.json"
    overwrite_state = bool(config.get("overwrite_state", False))

    if state_path.exists() and not overwrite_state:
        raise FileExistsError(f"Batch state already exists: {state_path}. Use another config job_name or set overwrite_state to true only if replacement is intentional.")

    with input_path.open("w", encoding="utf-8") as input_file:
        for prompt in unique_prompts:
            custom_id = prompt_to_custom_id[prompt]
            cache_key = get_abstraction_prompt_cache_key(prompt)
            request_body = {"model": API_MODEL, "input": prompt, "temperature": 0.0, "max_output_tokens": 3000}

            if cache_key is not None:
                request_body["prompt_cache_key"] = cache_key
                request_body["prompt_cache_retention"] = "24h"

            request = {"custom_id": custom_id, "method": "POST", "url": "/v1/responses", "body": request_body}
            input_file.write(json.dumps(request, ensure_ascii=False) + "\n")

    client = get_openai_client()

    with input_path.open("rb") as input_file:
        uploaded_file = client.files.create(file=input_file, purpose="batch")

    batch = client.batches.create(input_file_id=uploaded_file.id, endpoint="/v1/responses", completion_window="24h", metadata={"job_name": job_name, "task": "abstraction_extraction"})
    state = {
        "schema_version": 1,
        "job_name": job_name,
        "batch_id": batch.id,
        "input_file_id": uploaded_file.id,
        "api_model": API_MODEL,
        "model": args.model,
        "dataset": args.dataset,
        "task": abstraction_task,
        "unit": args.unit,
        "event_path": event_path,
        "input_path": str(input_path),
        "total_prompt_count": len(prompts),
        "unique_prompt_count": len(unique_prompts),
        "prompt_custom_ids": prompt_custom_ids,
        "index_map": serializable_index_map,
        "processed": False,
    }

    with state_path.open("w", encoding="utf-8") as state_file:
        json.dump(state, state_file, ensure_ascii=False, indent=2)

    print(f"Batch submitted successfully: {batch.id}")
    print(f"Batch status: {batch.status}")
    print(f"Batch input: {input_path}")
    print(f"Batch state: {state_path}")
    print("The process can now exit. OpenAI will continue the job.")
    return batch.id
