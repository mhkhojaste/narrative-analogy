import json
import pickle
from pathlib import Path

from tqdm import tqdm

from utils.Extraction.abstraction_extraction import PATH_ABSTRACTION, convert_events_to_object_array, map_text_to_abstraction, map_text_to_stages, sort_list_by_dict
from utils.helper_utils import batched, get_openai_client, model_short_dict, task_abstraction_short


DEFAULT_JOB_DIRECTORY = "Data_new/OpenAI_Batches"
TARGET_NUMBERS = {"timeline_extraction": 1, "conceptual_abstraction_level0": 2, "conceptual_abstraction_level1": 3, "evaluative_abstraction": 4, "arc_abstraction": 5, "stage_abstraction": 6}


def get_batch_config(args):
    config = args.config if isinstance(args.config, dict) else {}
    abstraction_task = config.get("abstraction_task")

    if not abstraction_task:
        raise ValueError("The config must contain 'abstraction_task'.")

    return config, abstraction_task


def make_job_name(args, abstraction_task, config):
    configured_job_name = config.get("job_name")

    if configured_job_name:
        return str(configured_job_name)

    model_name = args.model.replace(".", "_").replace("/", "_")
    return f"{model_name}_{args.dataset.lower()}_{abstraction_task}_{args.unit}"


def extract_responses_batch_text(response_body):
    direct_text = response_body.get("output_text")

    if isinstance(direct_text, str) and direct_text:
        return direct_text

    text_parts = []

    for output_item in response_body.get("output", []):
        for content_item in output_item.get("content", []):
            if content_item.get("type") == "output_text":
                text = content_item.get("text", "")

                if text:
                    text_parts.append(text)

    return "".join(text_parts)


def save_remote_error_file(client, batch, state_path):
    if not batch.error_file_id:
        return None

    error_response = client.files.content(batch.error_file_id)
    error_path = state_path.with_name(state_path.name.replace(".state.json", ".remote_errors.jsonl"))
    error_path.write_text(error_response.text, encoding="utf-8")
    return error_path


def download_and_validate_outputs(client, batch, state, state_path):
    if not batch.output_file_id:
        raise RuntimeError("The Batch is marked completed but has no output_file_id.")

    output_response = client.files.content(batch.output_file_id)
    output_text = output_response.text
    output_path = state_path.with_name(state_path.name.replace(".state.json", ".output.jsonl"))
    output_path.write_text(output_text, encoding="utf-8")
    output_by_custom_id = {}
    failures = []
    total_input_tokens = 0
    total_cached_tokens = 0
    total_output_tokens = 0

    for line_number, line in enumerate(output_text.splitlines(), start=1):
        if not line.strip():
            continue

        result = json.loads(line)
        custom_id = result.get("custom_id")
        response = result.get("response")
        request_error = result.get("error")

        if request_error is not None:
            failures.append({"line": line_number, "custom_id": custom_id, "error": request_error})
            continue

        if response is None:
            failures.append({"line": line_number, "custom_id": custom_id, "error": "Missing response object."})
            continue

        if response.get("status_code") != 200:
            failures.append({"line": line_number, "custom_id": custom_id, "status_code": response.get("status_code"), "response": response})
            continue

        response_body = response.get("body", {})
        generated_text = extract_responses_batch_text(response_body)

        if not generated_text:
            failures.append({"line": line_number, "custom_id": custom_id, "error": "No output text was found in the response."})
            continue

        if custom_id in output_by_custom_id:
            failures.append({"line": line_number, "custom_id": custom_id, "error": "Duplicate custom_id in Batch output."})
            continue

        output_by_custom_id[custom_id] = generated_text
        usage = response_body.get("usage", {}) or {}
        input_details = usage.get("input_tokens_details", {}) or {}
        total_input_tokens += usage.get("input_tokens", 0) or 0
        total_cached_tokens += input_details.get("cached_tokens", 0) or 0
        total_output_tokens += usage.get("output_tokens", 0) or 0

    expected_custom_ids = set(state["prompt_custom_ids"])
    received_custom_ids = set(output_by_custom_id)
    missing_custom_ids = sorted(expected_custom_ids - received_custom_ids)
    unexpected_custom_ids = sorted(received_custom_ids - expected_custom_ids)

    if missing_custom_ids or unexpected_custom_ids or failures:
        failure_path = state_path.with_name(state_path.name.replace(".state.json", ".failures.json"))
        failure_report = {"missing_custom_ids": missing_custom_ids, "unexpected_custom_ids": unexpected_custom_ids, "request_failures": failures}
        failure_path.write_text(json.dumps(failure_report, ensure_ascii=False, indent=2), encoding="utf-8")
        raise RuntimeError(f"The Batch output is incomplete or invalid. See {failure_path}.")

    print(f"Batch output: {output_path}")
    print(f"Unique outputs: {len(output_by_custom_id)}")
    print(f"Total input tokens: {total_input_tokens}")
    print(f"Cached input tokens: {total_cached_tokens}")
    print(f"Total output tokens: {total_output_tokens}")

    if total_input_tokens:
        cache_rate = 100 * total_cached_tokens / total_input_tokens
        print(f"Cached-token rate: {cache_rate:.2f}%")

    return output_by_custom_id, output_path


def process_abstraction_outputs(state, output_by_custom_id, batch_size):
    task = state["task"]
    dataset_name = state["dataset"]
    model_name = state["model"]
    unit = state["unit"]

    if task not in TARGET_NUMBERS:
        raise ValueError(f"Unsupported task in Batch state: {task}")

    with open(state["event_path"], "rb") as event_file:
        dataset_event = pickle.load(event_file)

    prompt_custom_ids = state["prompt_custom_ids"]
    index_map = state["index_map"]

    if len(prompt_custom_ids) != len(index_map):
        raise ValueError("Stored prompt/index-map size mismatch: " f"{len(prompt_custom_ids)} prompt IDs and {len(index_map)} mappings.")

    model_short = model_short_dict.get(model_name)

    if model_short is None:
        raise ValueError(f"No short model name configured for {model_name}.")

    dataset_suffix = dataset_name.lower()
    target_number = TARGET_NUMBERS[task]
    timeline_abstractions = None

    if task in {"evaluative_abstraction", "arc_abstraction"}:
        timeline_path = f"{PATH_ABSTRACTION}{model_short}{unit}_timeline_{dataset_suffix}.pkl"

        with open(timeline_path, "rb") as timeline_file:
            timeline_abstractions = pickle.load(timeline_file)

    abstraction_dict = {}
    global_offset = 0

    print(f"Extracting abstractions for {dataset_name} dataset")

    for custom_id_chunk in tqdm(list(batched(prompt_custom_ids, batch_size)), desc="Processing Batch outputs"):
        raw_texts = [output_by_custom_id[custom_id] for custom_id in custom_id_chunk]
        slice_map = index_map[global_offset : global_offset + len(custom_id_chunk)]

        if len(raw_texts) != len(slice_map):
            raise ValueError(f"Output/index-map mismatch at offset {global_offset}.")

        for raw_text, mapping in zip(raw_texts, slice_map):
            row_index, field_name = mapping

            if task == "stage_abstraction":
                abstraction_output = map_text_to_stages(raw_text)
            else:
                events = dataset_event[row_index][field_name]

                if task in {"evaluative_abstraction", "arc_abstraction"}:
                    events = sort_list_by_dict(events, timeline_abstractions[row_index][field_name])

                abstraction_output = map_text_to_abstraction(convert_events_to_object_array(events), raw_text, target_number)

            abstraction_dict.setdefault(row_index, {})[field_name] = abstraction_output

        global_offset += len(custom_id_chunk)

    if global_offset != len(prompt_custom_ids):
        raise ValueError(f"Processed {global_offset} prompts, expected {len(prompt_custom_ids)}.")

    task_short = task_abstraction_short.get(task)

    if task_short is None:
        raise ValueError(f"No short name configured for task: {task}")

    result_path = f"{PATH_ABSTRACTION}{model_short}{unit}_{task_short}_{dataset_suffix}.pkl"

    with open(result_path, "wb") as result_file:
        pickle.dump(abstraction_dict, result_file)

    print(f"Saved abstraction results as: {result_path}")
    return result_path


def check_abstraction_batch(args):
    config, abstraction_task = get_batch_config(args)
    job_directory = Path(config.get("job_directory", DEFAULT_JOB_DIRECTORY))
    job_name = make_job_name(args, abstraction_task, config)
    state_path = job_directory / f"{job_name}.state.json"
    batch_size = int(config.get("batch_size", 16))

    if batch_size < 1:
        raise ValueError("batch_size must be greater than zero.")

    if not state_path.exists():
        raise FileNotFoundError(f"Batch state does not exist: {state_path}")

    with state_path.open("r", encoding="utf-8") as state_file:
        state = json.load(state_file)

    expected_configuration = {"model": args.model, "dataset": args.dataset, "task": abstraction_task, "unit": args.unit}

    for key, expected_value in expected_configuration.items():
        actual_value = state.get(key)

        if actual_value != expected_value:
            raise ValueError(f"Batch state mismatch for {key}: expected {expected_value!r}, found {actual_value!r}.")

    client = get_openai_client()
    batch = client.batches.retrieve(state["batch_id"])

    print(f"Batch ID: {batch.id}")
    print(f"Batch status: {batch.status}")

    if batch.request_counts is not None:
        print(f"Request counts: {batch.request_counts}")

    running_statuses = {"validating", "in_progress", "finalizing", "cancelling"}
    failed_statuses = {"failed", "expired", "cancelled", "canceled"}

    if batch.status in running_statuses:
        print("The Batch is not finished. Check again later.")
        return None

    if batch.status in failed_statuses:
        error_path = save_remote_error_file(client, batch, state_path)
        message = f"Batch ended with status {batch.status!r}."

        if error_path is not None:
            message += f" Error details were saved to {error_path}."

        raise RuntimeError(message)

    if batch.status != "completed":
        print(f"Batch has status {batch.status!r}. No processing was performed.")
        return None

    output_by_custom_id, output_path = download_and_validate_outputs(client, batch, state, state_path)
    result_path = process_abstraction_outputs(state, output_by_custom_id, batch_size)
    state["processed"] = True
    state["output_file_id"] = batch.output_file_id
    state["output_path"] = str(output_path)
    state["result_path"] = result_path

    with state_path.open("w", encoding="utf-8") as state_file:
        json.dump(state, state_file, ensure_ascii=False, indent=2)

    print(f"Updated Batch state: {state_path}")
    return result_path
