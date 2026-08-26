# narrative-analogy

python main.py --dataset dataset_name --model model_name --task "unit_extraction" --unit 
python main.py --dataset ARN --model Qwen3-8B-vllm --task "unit_extraction" --unit "events"


python main.py --dataset dataset_name --model model_name --task "abstraction_extractionX" --unit unit_name

python main.py --dataset ARN --model Qwen3-8B-vllm --task "timeline_extraction" --unit "events"
python main.py --dataset ARN --model Qwen3-8B-vllm --task "conceptual_abstraction_level0" --unit "events"
python main.py --dataset ARN --model Qwen3-8B-vllm --task "conceptual_abstraction_level1" --unit "events"
python main.py --dataset ARN --model Qwen3-8B-vllm --task "evaluative_abstraction" --unit "events"
python main.py --dataset ARN --model Qwen3-8B-vllm --task "arc_abstraction" --unit "events"
python main.py --dataset ARN --model Qwen3-8B-vllm --task "stage_abstraction" --unit "events"


python main.py --dataset ARN --model Qwen3-8B-vllm --task "mapping" --unit "events" --scoring_method "cosine" --global_map "Greedy" --config '{"version": 1, "top_output": 3}'
python main.py --dataset ARN --model Qwen3-8B-vllm --task "mapping" --unit "conceptual0" --scoring_method "cosine" --global_map "Greedy" --config '{"version": 3, "top_output": 3, "text_modify": "only_root"}'


This repository builds *structural maps* for two narratives. It extracts story units, abstracts them to higher-level concepts, groups them into stages and super-units, and finally computes local and global mappings between the narratives. The pipeline also produces scores that indicate how correct each mapping is.

---

## Quick Start

1. **Install dependencies** (see Installation).
2. **Run Unit Extraction** to produce base units.
3. **Run Abstraction Extraction** (optional but recommended).
4. **Run Stage Extraction** (optional, if you use stages).
5. **Run Super-unit Extraction** (optional, if you use super-units).
6. **Run Mapping** to produce local/global mappings and scores.

> **Important:** The examples below show the exact flags you must use. Feel free to change *values* like dataset names, model names, and unit/method identifiers **within the allowed sets** described in each task.

---

## Installation

This project uses Python and Hugging Face Transformers.

    # Install required packages
    pip install transformers


---

## Concepts & Terminology

- **Unit**: The smallest extracted narrative element (e.g., an event phrase). Units are the foundation for all subsequent steps.
- **Abstraction**: A higher-level representation of a unit (e.g., a generalized event or concept).
- **Stage**: A grouping of units or abstractions that represent a structural phase of the narrative.
- **Super-unit**: A higher-order grouping (often derived from stages) that captures broader structure.
- **Local mapping**: Alignment between specific items (e.g., unit ↔ unit, abstraction ↔ abstraction).
- **Global mapping**: A narrative-level alignment computed from local scores using a global matching algorithm.

---

## Datasets & Models

- **Datasets (`--dataset`)**: `MCQ_random` or `ARN_random`
- **Models (`--model`)**: currently `Qwen3-8B` or `Llama-3.1-8B`

You can add more models later.

---

## Running the Pipeline

We expose the pipeline via a single entry point:

    python main.py ...

Each task below explains the required flags and expected artifacts.

---

### 1) Unit Extraction

**Purpose:** Extract base “units” (e.g., event phrases) from the narratives. These are the inputs to all downstream steps.

**Command:**

    python main.py --dataset dataset_name --model model_name --task "unit_extraction" --unit unit_name

**Parameters**
- `--dataset` — dataset name. Choose one: `MCQ_random` / `ARN_random`.
- `--model` — model name. Choose one: `Qwen3-8B` / `Llama-3.1-8B`.
- `--task` — must be `"unit_extraction"`.
- `--unit` — the unit method/prompt to use (e.g., `unit_event_phrases_3`).

**Example**

    python main.py --dataset MCQ_random --model Qwen3-8B --task "unit_extraction" --unit "unit_event_phrases_3"

Here, `unit_event_phrases_3` selects a specific method in the pipeline.

**Add a New Model Name**
- Edit `utils/helper_utils.py`:
  - Add a model loading function.
  - Update how it is called from the `query_models` functions.
  - Add an entry to `model_short_dict` mapping the full name to a short name (e.g., `Qwen3-8B` → `Qwen8_`).

**Add a New Unit Name / Method**
- If it’s a new **prompt**, add it to `prompts_unit.py`.
- If it’s a new **method**, create a new file in the `utils/` directory.
- In `unit_extraction.py`, update `event_phrase_extraction_model` so it dispatches the new `--unit` to the correct prompt/method.

**Output**

    {PATH_UNITS}{model_short}{unit_name}_{dataset_name}.pkl

This file contains the extracted units used by later steps.

---

### 2) Abstraction Extraction

**Purpose:** Convert previously extracted units into higher-level abstractions.

**Command:**

    python main.py --dataset dataset_name --model model_name --task "abstraction_extractionX" --unit unit_name

**Parameters**
- `--task` — must **start** with `abstraction_extraction` and be followed by a number or version string that selects the method (e.g., `abstraction_extraction4`).
- `--unit` — the same unit name used during Unit Extraction. The file `{PATH_UNITS}{model_short}{unit_name}_{dataset_name}.pkl` **must already exist**.

**Example**

    python main.py --dataset ARN_random --model Qwen3-8B --task "abstraction_extraction4" --unit "unit_event_phrases_3"

This loads the units from:

    {PATH_UNITS}{Qwen8_}{unit_event_phrases_3}_{arn_random}.pkl

and extracts abstractions using the method `abstraction_extraction4`.

**Add a New Abstraction Method**
- Add the prompt in the appropriate file or implement your new method module.
- Update `abstraction_extraction_model` in `abstraction_extraction.py`.
- Update `task_abstraction_short` in `utils/helper_utils.py` to assign a short alias.

**Output**

    {PATH_ABSTRACTION}{model_short}{unit_name}_{task_short}_dict_{dataset_name}.pkl

---

### 3) Stage Extraction

**Purpose:** Group units/abstractions into narrative **stages**. This is structurally similar to Abstraction Extraction.

**Command:**

    python main.py --dataset ARN_random --model Qwen3-8B --task "stage_extraction2" --unit "unit_event_phrases_2"

**Parameters**
- Same pattern as Abstraction Extraction, but with `stage_extraction*` methods.

**Add a New Stage Extraction Method**
- Add the prompt in the specific file or implement a new method.
- Update `stage_extraction_model` in `stage_extraction.py`.
- Update `task_stage_short` in `utils/helper_utils.py`.

**Output**

    {PATH_STAGE}{model_short}{unit_name}_{task_short}_{dataset_name}.pkl

---

### 4) Super-unit Extraction

**Purpose:** Build higher-order groupings (super-units), typically leveraging previously extracted **stages**.

**Command:**

    python main.py --dataset ARN_random --model Qwen3-8B --task "stage2_super1" --unit "unit_event_phrases_2"

**Parameters**
- Same pattern as Abstraction Extraction.
- For `--task`, the first part names the **stage** you want to use (e.g., `stage2`), and the second part names the **super-unit extraction method** (e.g., `super1`).

**Add a New Super-unit Extraction Method**
- Add the prompt in the specific file or implement your method.
- Update `superunit_extraction_model` in `superunit_extraction.py`.

**Output**

    {PATH_SUPERUNIT}{model_short}{unit}_{task_short}_{dataset_name}.pkl


---

### 5) Mapping

**Purpose:** Produce local and global mappings between the two narratives and assign scores to each mapping.

**Command:**

    python main.py --dataset dataset_name --model model_name --task "mapping" --unit unit_name --enrichment enrichment_method --scoring_unit scoring_unit_name --scoring_method scoring_method --scoring_constraint scoring_constraint --global_match mathing_algorithm --top_output number_output --version version_number

**Parameters**
- `--dataset` — `MCQ_random` / `ARN_random`.
- `--model` — `Qwen3-8B` / `Llama-3.1-8B`.
- `--task` — must be `"mapping"`.
- `--unit` — the unit method name you used when extracting information (ensures consistent file loading).
- `--enrichment` — whether to enrich the scoring units. Use `"none"` (default) or `"stages"` to incorporate stage information.
- `--scoring_unit` — the representation used for scoring; supports **units**, **abstractions** (e.g., `abstraction1`, `abstraction2`, ...), or **super-units** (e.g., `stage_abstraction`).
- `--scoring_method` — `"verbalized"` or `"triple"`, indicating how elements are compared/represented for scoring.
- `--scoring_constraint` — `"hard"`, `"soft_simple"`, `"soft_parentheses"`, or `"soft_sentence"`, controlling how strictly matches must align when stages are used.
- `--global_match` — the global mapping algorithm: `"Beam-search"` or `"Beam-search2"`.
- `--top_output` — the number of best global mapping solutions to return.
- `--version` — a new version number used to label outputs (choose a number you haven’t used before).

**Example**

    python main.py --dataset ARN_random --model Qwen3-8B --task "mapping" --unit "unit_event_phrases" --enrichment "none" --scoring_unit "stage_abstraction" --scoring_method "verbalized" --scoring_constraint "hard" --global_match "Beam-search" --top_output 3 --version 73

**Remember**
- All required files must **exist** before mapping.
- Ensure data is loaded in the **expected formats**.
- Check `main_mapping.py` for implementation details and data handling.
