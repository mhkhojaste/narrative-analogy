prompt_abstraction_extraction1 = """

### Role Assignment
You are an analytical assistant that generalizes specific narrative phrases into higher-level conceptual “kernel names.”
You read a short **Story** and an accompanying list of extracted **Phrases**.
For each phrase you output a concise, more abstract kernel name capturing its core idea while considering its role in, and relation to, the other phrases.

---------

### Task Definition
Given:
1. A *Story* describing a situation.
2. A list of *Phrases* already extracted from that story (each phrase is a concrete element, event, feeling, judgment, or action).

Produce for **each** phrase a **kernel name** that:
- Expresses the central concept of the phrase in a **more general / abstract** manner than the original wording.
- Reflects the phrase’s **role** in the overall story (e.g., event, cause, symptom, evaluation, decision, coping attempt) and its **relationship** to other phrases (e.g., consequence of another phrase).
- Avoids duplicating surface wording from the phrase; prefer conceptual nouns or noun phrases (1–5 words).
- Is neutral in tone (no exaggeration), unless sentiment is essential.
- Does **not** introduce new specific details absent from the story.

Also provide a brief **rationale** (1 short sentence) explaining how the kernel name generalizes the original phrase. The rationale must state the reasoning (what features of the phrase and/or its role or relations justify the chosen kernel), not a tautology (avoid templates like “Abstracts X into Y”).

---------

### Term Definitions
- **Phrase:** A specific textual fragment extracted from the story, describing an event, state, perception, emotion, evaluation, or decision.
- **Kernel Name:** A concise, more abstract concept label summarizing the essential meaning of a phrase (e.g., “performance anxiety symptoms” for “Hands shaking and talking too fast”).
- **Abstraction / More General:** Removing incidental specifics (time, place, actors’ proper nouns) to reveal a broader category or concept.
- **Role / Relations:** The functional contribution of the phrase within the story (e.g., cause, effect, symptom, coping action, decision) and how it connects conceptually to other phrases.

### Output Explanation
Return a JSON object with an array `results`. Each element corresponds to one input phrase and contains:
- `id`: the phrase identifier copied exactly from the input (e.g., "p1", "p2", ...).
- `original_phrase`: the exact input phrase text (byte-for-byte, including case and punctuation).
- `kernel_name`: your generalized concept (string).
- `rationale`: a short explanation of why this kernel name captures and abstracts the phrase (state the reason based on features/role/relations, not a tautology).

Order the results in the same order as the input phrases. Use the same `id` values as provided.

---------

### Examples
**Example 1**

Story:
“David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better.”

Phrases:
[
  {{ "id":"p1","text":"David noticed weight gain" }},
  {{ "id":"p2","text":"Examined his habits for a reason" }},
  {{ "id":"p3","text":"Realized he ate too much fast food" }},
  {{ "id":"p4","text":"Stopped going to burger places" }},
  {{ "id":"p5","text":"Started a vegetarian diet" }},
  {{ "id":"p6","text":"Felt better after a few weeks" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "David noticed weight gain",
      "kernel_name": "weight gain awareness",
      "rationale": "The speaker recognizes a bodily change, marking initial problem detection that motivates later actions."
    }},
    {{
      "id": "p2",
      "original_phrase": "Examined his habits for a reason",
      "kernel_name": "causal self-assessment",
      "rationale": "He analyzes his own behaviors to identify contributing factors behind the problem."
    }},
    {{
      "id": "p3",
      "original_phrase": "Realized he ate too much fast food",
      "kernel_name": "dietary cause identification",
      "rationale": "He infers excessive fast-food intake as a likely driver of the issue, specifying a modifiable cause."
    }},
    {{
      "id": "p4",
      "original_phrase": "Stopped going to burger places",
      "kernel_name": "trigger avoidance",
      "rationale": "He removes environmental cues associated with the problematic behavior as a control strategy."
    }},
    {{
      "id": "p5",
      "original_phrase": "Started a vegetarian diet",
      "kernel_name": "health-oriented diet change",
      "rationale": "He adopts a structured eating pattern aimed at improving health rather than targeting a single food."
    }},
    {{
      "id": "p6",
      "original_phrase": "Felt better after a few weeks",
      "kernel_name": "improved well-being",
      "rationale": "A positive outcome emerges over time, plausibly as a consequence of the dietary and behavioral changes."
    }}
  ]
}}
</JSON>

---------

**Example 2**

Story:
“Eric and his wife had a daughter named Meg. Eric and Meg were very sad when Eric's wife passed away. Eric met a woman and married her 5 years after his wife died. Meg is finally happy with her new stepmother.”

Phrases:
[
  {{ "id":"p1","text":"Eric and his wife had Meg" }},
  {{ "id":"p2","text":"Erics wife passed away" }},
  {{ "id":"p3","text":"Eric and Meg were very sad" }},
  {{ "id":"p4","text":"Eric met a woman" }},
  {{ "id":"p5","text":"Five years later Eric married the woman" }},
  {{ "id":"p6","text":"Meg was happy with her stepmother" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Eric and his wife had Meg",
      "kernel_name": "childbirth event",
      "rationale": "This establishes the family unit by noting the birth of a child without focusing on names or timing."
    }},
    {{
      "id": "p2",
      "original_phrase": "Erics wife passed away",
      "kernel_name": "spousal bereavement",
      "rationale": "The death of a spouse introduces a major loss shaping subsequent emotions and choices."
    }},
    {{
      "id": "p3",
      "original_phrase": "Eric and Meg were very sad",
      "kernel_name": "grief response",
      "rationale": "Their intense sadness functions as the emotional consequence of the bereavement."
    }},
    {{
      "id": "p4",
      "original_phrase": "Eric met a woman",
      "kernel_name": "new partner encounter",
      "rationale": "A post-loss meeting signals the start of a potential relationship trajectory."
    }},
    {{
      "id": "p5",
      "original_phrase": "Five years later Eric married the woman",
      "kernel_name": "remarriage after bereavement",
      "rationale": "A significant time gap culminates in forming a new marital bond following the prior loss."
    }},
    {{
      "id": "p6",
      "original_phrase": "Meg was happy with her stepmother",
      "kernel_name": "positive stepfamily adjustment",
      "rationale": "The child’s contentment indicates successful adaptation to the new family structure."
    }}
  ]
}}
</JSON>

---------

**Example 3**

Story:
“There was a bug on the wall by the bed. Kate grabbed a shoe and killed it.”

Phrases:
[
  {{ "id":"p1","text":"Bug was on the wall by the bed" }},
  {{ "id":"p2","text":"Kate grabbed a shoe" }},
  {{ "id":"p3","text":"Kate killed the bug" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Bug was on the wall by the bed",
      "kernel_name": "household pest presence",
      "rationale": "An insect is present in a living space near a resting area, creating a nuisance to be addressed."
    }},
    {{
      "id": "p2",
      "original_phrase": "Kate grabbed a shoe",
      "kernel_name": "improvised tool selection",
      "rationale": "She selects a readily available object as a means to handle the problem."
    }},
    {{
      "id": "p3",
      "original_phrase": "Kate killed the bug",
      "kernel_name": "pest elimination",
      "rationale": "The action resolves the nuisance by removing the pest."
    }}
  ]
}}
</JSON>

---------

**Example 4**

Story:
“I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

Phrases:
[
  {{ "id":"p1","text":"Bought a cheap jacket" }},
  {{ "id":"p2","text":"Jacket fell apart the next day" }},
  {{ "id":"p3","text":"Concluded more expensive clothes last longer" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Bought a cheap jacket",
      "kernel_name": "low-cost purchase decision",
      "rationale": "The buyer opts for a minimal-price item, setting up a quality tradeoff."
    }},
    {{
      "id": "p2",
      "original_phrase": "Jacket fell apart the next day",
      "kernel_name": "premature product failure",
      "rationale": "The item quickly breaks, providing negative feedback on durability."
    }},
    {{
      "id": "p3",
      "original_phrase": "Concluded more expensive clothes last longer",
      "kernel_name": "quality-over-cost heuristic",
      "rationale": "From the failure, the buyer generalizes a purchasing rule favoring durability over low price."
    }}
  ]
}}
</JSON>

---------

### Your Turn

#### Input Format
Story:
{story}

Phrases:
{phrases}

---------

#### Output Format
#### Remember:
- Read the Story and Phrases. For each phrase, output a generalized kernel name and rationale following the given rules.
- **Always use the same `id` and `original_phrase` as in the input.** Copy `original_phrase` exactly from the input `text` (preserve case and punctuation). Use the same `id` value.
- The rationale must state the reason (features/role/relations that justify the kernel), not a tautology.

Output: A single JSON object exactly matching the schema described in Output Explanation.

Return ONLY one JSON array. Do not output anything before or after it.
Wrap the array inside <JSON> ... </JSON> tags.
Provide output in the following format:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": ...,
      "kernel_name": ...,
      "rationale": ...
    }},
    ...
  ]
}}
</JSON>

"""


prompt_abstraction_extraction2 = """
### Role Assignment
You are an analytical assistant that generalizes specific narrative phrases into higher-level conceptual “kernel names.”
You read a short **Story** and an accompanying list of extracted **Phrases**.
For each phrase you output a concise, more abstract kernel name capturing its core idea while considering its role in, and relation to, the other phrases.

---------

### Task Definition
Given:
1. A *Story* describing a situation.
2. A list of *Phrases* already extracted from that story (each phrase is a concrete element, event, feeling, judgment, or action).

Produce for **each** phrase a **kernel name** that:
- Expresses the central concept of the phrase in a **more general / abstract** manner than the original wording.
- Reflects the phrase’s **role** in the overall story (e.g., event, cause, symptom, evaluation, decision, coping attempt) and its **relationship** to other phrases (e.g., consequence of another phrase).
- Avoids duplicating surface wording from the phrase; prefer conceptual nouns or noun phrases (1–5 words before any prepositional phrase).
- Is neutral in tone (no exaggeration), unless sentiment is essential.
- Does **not** introduce new specific details absent from the story.

**Naming Format Constraint (required):**
- Form: **[optional adjective] + [root noun] + [optional prepositional phrase]**.
- **Root noun (mandatory):** choose a single general noun that best captures the phrase’s role (e.g., *evaluation, decision, preparation, recognition, improvement, conflict, request, loss*). Do **not** rely on a fixed list; choose the most fitting root per phrase.
- **Adjective (optional):** use at most one neutral/diagnostic adjective when polarity/degree/temporal quality is essential (e.g., *negative, positive, insufficient, excessive, gradual, sudden, perceived*).
- **Prepositional phrase (optional, at most one):** use a short noun phrase **without** proper nouns, time, or place details unless essential to the concept. Prefer prepositions like **of, about, with, for, toward, from, due to, between, by, to, in**. Use at most one PP to encode target/partner/theme/cause.
- If the format would be awkward, omit the adjective and/or the prepositional phrase rather than forcing them.

---------

### Term Definitions
- **Phrase:** A specific textual fragment extracted from the story, describing an event, state, perception, emotion, evaluation, or decision.
- **Kernel Name:** A concise, more abstract concept label (noun phrase) following the required format: *[optional adjective] + [root noun] + [optional PP]* (e.g., “negative self-evaluation,” “coping attempt about rumination,” “workload imbalance between team members”).
- **Abstraction / More General:** Removing incidental specifics (time, place, actors’ proper nouns) to reveal a broader category or concept.
- **Role / Relations:** The functional contribution of the phrase within the story (e.g., cause, effect, symptom, coping action, decision) and how it connects conceptually to other phrases.

### Output Explanation
Return a JSON object with an array `results`. Each element corresponds to one input phrase and contains:
- `id`: the phrase identifier copied exactly from the input (e.g., "p1", "p2", ...).
- `original_phrase`: the exact input phrase text (byte-for-byte, including case and punctuation).
- `kernel_name`: your generalized concept (string) in the required format.
- `rationale`: a short explanation of why this kernel name captures and abstracts the phrase (state the reason based on features/role/relations, not a tautology).

Order the results in the same order as the input phrases. Use the same `id` values as provided.

---------

### Examples
**Example 1**

Story:
“David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better.”

Phrases:
[
  {{ "id":"p1","text":"David noticed weight gain" }},
  {{ "id":"p2","text":"Examined his habits for a reason" }},
  {{ "id":"p3","text":"Realized he ate too much fast food" }},
  {{ "id":"p4","text":"Stopped going to burger places" }},
  {{ "id":"p5","text":"Started a vegetarian diet" }},
  {{ "id":"p6","text":"Felt better after a few weeks" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "David noticed weight gain",
      "kernel_name": "personal awareness of weight gain",
      "rationale": "The phrase reports noticing a health change; the kernel abstracts this as general awareness of the condition."
    }},
    {{
      "id": "p2",
      "original_phrase": "Examined his habits for a reason",
      "kernel_name": "behavioral analysis for cause",
      "rationale": "The action is inspecting routines to find reasons; the kernel frames it as an analysis aimed at causation."
    }},
    {{
      "id": "p3",
      "original_phrase": "Realized he ate too much fast food",
      "kernel_name": "causal recognition of fast-food overconsumption",
      "rationale": "The phrase identifies overuse of fast food as the reason; the kernel generalizes this as recognizing a causal dietary factor."
    }},
    {{
      "id": "p4",
      "original_phrase": "Stopped going to burger places",
      "kernel_name": "behavioral cessation of fast-food visits",
      "rationale": "It describes discontinuing a behavior; the kernel abstracts this as stopping exposure to fast-food outlets."
    }},
    {{
      "id": "p5",
      "original_phrase": "Started a vegetarian diet",
      "kernel_name": "dietary change to vegetarianism",
      "rationale": "The phrase reports adopting a new eating pattern; the kernel names a general diet change without menu specifics."
    }},
    {{
      "id": "p6",
      "original_phrase": "Felt better after a few weeks",
      "kernel_name": "subjective improvement in well-being",
      "rationale": "It describes improved feeling; the kernel abstracts this as a general improvement in well-being without time details."
    }}
  ]
}}
</JSON>

---------

**Example 2**

Story:
“Eric and his wife had a daughter named Meg. Eric and Meg were very sad when Eric's wife passed away. Eric met a woman and married her 5 years after his wife died. Meg is finally happy with her new stepmother.”

Phrases:
[
  {{ "id":"p1","text":"Eric and his wife had Meg" }},
  {{ "id":"p2","text":"Erics wife passed away" }},
  {{ "id":"p3","text":"Eric and Meg were very sad" }},
  {{ "id":"p4","text":"Eric met a woman" }},
  {{ "id":"p5","text":"Five years later Eric married the woman" }},
  {{ "id":"p6","text":"Meg was happy with her stepmother" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Eric and his wife had Meg",
      "kernel_name": "parenthood event of daughter",
      "rationale": "The phrase establishes the child’s arrival; the kernel names the general parenthood event without proper nouns."
    }},
    {{
      "id": "p2",
      "original_phrase": "Erics wife passed away",
      "kernel_name": "spousal loss by death",
      "rationale": "It reports the spouse’s death; the kernel generalizes this as loss within the family unit."
    }},
    {{
      "id": "p3",
      "original_phrase": "Eric and Meg were very sad",
      "kernel_name": "intense sadness about loss",
      "rationale": "It states strong negative affect linked to the death; the kernel captures emotion directed at the loss."
    }},
    {{
      "id": "p4",
      "original_phrase": "Eric met a woman",
      "kernel_name": "new acquaintance with woman",
      "rationale": "The phrase describes meeting someone; the kernel abstracts it as initiating a new acquaintance."
    }},
    {{
      "id": "p5",
      "original_phrase": "Five years later Eric married the woman",
      "kernel_name": "subsequent marriage event with the woman",
      "rationale": "It reports a later marriage; the kernel frames this as a subsequent marriage event involving the same person."
    }},
    {{
      "id": "p6",
      "original_phrase": "Meg was happy with her stepmother",
      "kernel_name": "positive adjustment with stepmother",
      "rationale": "It reports Meg’s improved affect toward the new family member; the kernel abstracts this as positive adjustment."
    }}
  ]
}}
</JSON>

---------

**Example 3**

Story:
“There was a bug on the wall by the bed. Kate grabbed a shoe and killed it.”

Phrases:
[
  {{ "id":"p1","text":"Bug was on the wall by the bed" }},
  {{ "id":"p2","text":"Kate grabbed a shoe" }},
  {{ "id":"p3","text":"Kate killed the bug" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Bug was on the wall by the bed",
      "kernel_name": "pest presence near sleeping area",
      "rationale": "It indicates a pest located by the bed; the kernel abstracts to presence near a general sleeping area."
    }},
    {{
      "id": "p2",
      "original_phrase": "Kate grabbed a shoe",
      "kernel_name": "immediate tool acquisition for pest removal",
      "rationale": "The action secures an object to act on the pest; the kernel generalizes this as obtaining a tool for removal."
    }},
    {{
      "id": "p3",
      "original_phrase": "Kate killed the bug",
      "kernel_name": "pest elimination",
      "rationale": "It describes destroying the pest; the kernel names the general outcome without method details."
    }}
  ]
}}
</JSON>

---------

**Example 4**

Story:
“I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

Phrases:
[
  {{ "id":"p1","text":"Bought a cheap jacket" }},
  {{ "id":"p2","text":"Jacket fell apart the next day" }},
  {{ "id":"p3","text":"Concluded more expensive clothes last longer" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Bought a cheap jacket",
      "kernel_name": "low-cost purchase of jacket",
      "rationale": "It describes acquiring an inexpensive item; the kernel captures the purchase with cost quality abstracted."
    }},
    {{
      "id": "p2",
      "original_phrase": "Jacket fell apart the next day",
      "kernel_name": "premature product failure of jacket",
      "rationale": "It reports rapid deterioration; the kernel generalizes this as an early failure of the product."
    }},
    {{
      "id": "p3",
      "original_phrase": "Concluded more expensive clothes last longer",
      "kernel_name": "general conclusion about price–durability",
      "rationale": "It states a learned rule linking price and longevity; the kernel abstracts this as a broad conclusion about that relation."
    }}
  ]
}}
</JSON>

---------

### Your Turn

#### Input Format
Story:
{story}

Phrases:
{phrases}

---------

#### Output Format
#### Remember:
- Read the Story and Phrases. For each phrase, output a generalized kernel name and rationale following the given rules and the required naming format.
- **Always use the same `id` and `original_phrase` as in the input.** Copy `original_phrase` exactly from the input `text` (preserve case and punctuation). Use the same `id` value.
- The rationale must state the reason (features/role/relations that justify the kernel), not a tautology.

Output: A single JSON object exactly matching the schema described in Output Explanation.

Return ONLY one JSON array. Do not output anything before or after it.
Wrap the array inside <JSON> ... </JSON> tags.
Provide output in the following format:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": ...,
      "kernel_name": ...,
      "rationale": ...
    }},
    ...
  ]
}}
</JSON>

"""


prompt_abstraction_extraction3 = """
### Role Assignment
You are an analytical assistant that generalizes specific narrative phrases into higher-level conceptual “kernel names.”
You read a short **Story** and an accompanying list of extracted **Phrases**.
For each phrase you output a concise, more abstract kernel name capturing its core idea and its functional **role** in the narrative.

---------

### Task Definition
Given:
1. A *Story* describing a situation.
2. A list of *Phrases* already extracted from that story (each phrase is a concrete element, event, feeling, judgment, or action).

Produce for **each** phrase a **kernel name** and **rationale**:

- **kernel_name**: a concise **noun phrase (1–5 words)** that is a true **hypernym** of the phrase and encodes the phrase’s **role** via its head (e.g., *… awareness, … identification, … regulation, … constraint, … mechanism, … outcome, … pattern, … placement, … access, … adjustment*).
- **rationale**: **one short sentence** stating the reasoning (features/role/relations that justify the kernel). Avoid tautologies like “Abstracts X into Y.”

**Strict Delexicalization Rules**
- **Never** reuse story-specific surface words or named entities in `kernel_name` (e.g., character names, brand names, specific places).
- Replace participants with **roles** in your *reasoning* (AGENT, RECIPIENT, RESOURCE, LOCATION, INSTRUMENT), but do **not** output these role tokens in `kernel_name`.
- Keep mechanisms **only if central and causal**, expressed generally.
- **Do not reuse** the **specific entities** (e.g., names, places, objects, characters) that appear in the original story.
  - **Replace** each entity with a **higher-level hypernym** — a broader, more **general category** term.
  - Ensure that the substitution **maintains the logical flow** and meaning of the story.
  - Examples: “Sparrow”: “Bird” “Violin”: “Musical instrument” “Paris”: “City”

**Granularity**
- Default to **mid-level abstraction**: remove concrete items and proper nouns; keep core mechanisms if they are essential to causality; otherwise generalize to domain-neutral heads.

**Quality Gates** *(perform silently; output only the JSON array)*
1) **Hypernym test**: “A(n) [original phrase] is an instance of [kernel_name]” should read true.
2) **Leakage test**: `kernel_name` contains **no** story-specific content words after stopword removal.
3) **Replacement test**: Substituting the phrase with the kernel preserves the narrative gist and role.
4) **Concision test**: 1–5 words, neutral tone.
5) **Consistency**: If multiple kernels would be synonymous, keep them distinct by emphasizing their **role** (e.g., *awareness* vs *regulation*).

---------

### Term Definitions
- **Phrase:** A specific textual fragment extracted from the story, describing an event, state, perception, emotion, evaluation, or decision.
- **Kernel Name:** A concise, more abstract concept label summarizing the essential meaning of a phrase.
- **Role / Relations:** The functional contribution of the phrase within the story (e.g., cause, effect, symptom, decision, boundary-setting) and how it connects conceptually to other phrases.

---------

### Output Explanation
Return a JSON object with an array `results`. Each element corresponds to one input phrase and contains:
- `id`: the phrase identifier copied exactly from the input (e.g., "p1", "p2", ...).
- `original_phrase`: the exact input phrase text (byte-for-byte, including case and punctuation).
- `kernel_name`: your generalized concept (string) — use an abstract head that conveys the role (e.g., *… awareness, … identification, … regulation, … constraint, … mechanism, … outcome*).
- `rationale`: a short explanation of why this kernel name captures and abstracts the phrase (state the reason based on features/role/relations, not a tautology).

Order the results in the same order as the input phrases. Use the same `id` values as provided.

---------

### Examples
**Example 1**

Story:
“David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.”

Phrases:
[
  {{ "id":"p1","text":"David noticed weight gain" }},
  {{ "id":"p2","text":"David examined his habits for a reason" }},
  {{ "id":"p3","text":"David Realized he ate too much fast food" }},
  {{ "id":"p4","text":"David Stopped going to burger places" }},
  {{ "id":"p5","text":"David Started a vegetarian diet" }},
  {{ "id":"p6","text":"David Felt better after a few weeks" }},
  {{ "id":"p7","text":"David had stopped eating unhealthy foods" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "David noticed weight gain",
      "kernel_name": "weight gain awareness",
      "rationale": "Recognition of a bodily change functions as initial problem detection that motivates subsequent steps."
    }},
    {{
      "id": "p2",
      "original_phrase": "David examined his habits for a reason",
      "kernel_name": "causal self-assessment",
      "rationale": "He analyzes personal behaviors to identify contributors to the issue."
    }},
    {{
      "id": "p3",
      "original_phrase": "David Realized he ate too much fast food",
      "kernel_name": "dietary cause identification",
      "rationale": "He attributes the problem to an excessive eating pattern that is modifiable."
    }},
    {{
      "id": "p4",
      "original_phrase": "David Stopped going to burger places",
      "kernel_name": "trigger avoidance",
      "rationale": "He removes environmental cues that facilitate the undesired intake."
    }},
    {{
      "id": "p5",
      "original_phrase": "David Started a vegetarian diet",
      "kernel_name": "health-oriented diet adoption",
      "rationale": "He implements a structured dietary pattern aimed at improving health outcomes."
    }},
    {{
      "id": "p6",
      "original_phrase": "David Felt better after a few weeks",
      "kernel_name": "improved well-being",
      "rationale": "A positive outcome follows the behavior changes over time."
    }},
    {{
      "id": "p7",
      "original_phrase": "David had stopped eating unhealthy foods",
      "kernel_name": "dietary risk reduction",
      "rationale": "Reduced intake of harmful items serves as a proximal mechanism supporting the improvement."
    }}
  ]
}}
</JSON>

---------

**Example 2**

Story:
“Eric and his wife had a daughter named Meg. Eric and Meg were very sad when Eric's wife passed away. Eric met a woman and married her 5 years after his wife died. Meg is finally happy with her new stepmother as she is very kind to her.”

Phrases:
[
  {{ "id":"p1","text":"Eric and his wife had Meg" }},
  {{ "id":"p2","text":"Erics wife passed away" }},
  {{ "id":"p3","text":"Eric and Meg were very sad" }},
  {{ "id":"p4","text":"Eric met a woman" }},
  {{ "id":"p5","text":"Eric married the woman five years later " }},
  {{ "id":"p6","text":"Meg was happy with her stepmother" }},
  {{ "id":"p7","text":"Megs stepmother is kind to her" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Eric and his wife had Meg",
      "kernel_name": "childbirth event",
      "rationale": "Establishes the family unit via the birth of a child without relying on names or timing specifics."
    }},
    {{
      "id": "p2",
      "original_phrase": "Erics wife passed away",
      "kernel_name": "spousal bereavement",
      "rationale": "A major loss that shapes subsequent emotions and choices."
    }},
    {{
      "id": "p3",
      "original_phrase": "Eric and Meg were very sad",
      "kernel_name": "grief response",
      "rationale": "Intense sadness arises as the emotional consequence of the loss."
    }},
    {{
      "id": "p4",
      "original_phrase": "Eric met a woman",
      "kernel_name": "new partner encounter",
      "rationale": "An initial contact begins a potential relationship trajectory."
    }},
    {{
      "id": "p5",
      "original_phrase": "Eric married the woman five years later ",
      "kernel_name": "remarriage after bereavement",
      "rationale": "A substantial delay culminates in forming a new marital bond following prior loss."
    }},
    {{
      "id": "p6",
      "original_phrase": "Meg was happy with her stepmother",
      "kernel_name": "positive stepfamily adjustment",
      "rationale": "The child’s contentment indicates successful adaptation to the new family structure."
    }},
    {{
      "id": "p7",
      "original_phrase": "Megs stepmother is kind to her",
      "kernel_name": "caregiver kindness",
      "rationale": "Supportive behavior from the caregiver plausibly contributes to the child’s positive adjustment."
    }}
  ]
}}
</JSON>

---------

**Example 3**

Story:
“There was a bug on the wall by the bed. Kate grabbed a shoe and killed it.”

Phrases:
[
  {{ "id":"p1","text":"Bug was on the wall by the bed" }},
  {{ "id":"p2","text":"Kate grabbed a shoe" }},
  {{ "id":"p3","text":"Kate killed the bug" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Bug was on the wall by the bed",
      "kernel_name": "household pest presence",
      "rationale": "An unwanted organism appears in a living space near a resting area, creating a nuisance context."
    }},
    {{
      "id": "p2",
      "original_phrase": "Kate grabbed a shoe",
      "kernel_name": "improvised tool selection",
      "rationale": "A readily available object is chosen to address the nuisance."
    }},
    {{
      "id": "p3",
      "original_phrase": "Kate killed the bug",
      "kernel_name": "pest elimination",
      "rationale": "The nuisance is resolved through direct removal."
    }}
  ]
}}
</JSON>

---------

**Example 4**

Story:
“I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

Phrases:
[
  {{ "id":"p1","text":"I bought a cheap jacket" }},
  {{ "id":"p2","text":"Jacket fell apart the next day" }},
  {{ "id":"p3","text":"I concluded more expensive clothes last longer" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "I bought a cheap jacket",
      "kernel_name": "low-cost purchase decision",
      "rationale": "The buyer prioritizes minimal price, setting up a durability tradeoff."
    }},
    {{
      "id": "p2",
      "original_phrase": "Jacket fell apart the next day",
      "kernel_name": "premature product failure",
      "rationale": "Rapid breakdown provides negative durability feedback."
    }},
    {{
      "id": "p3",
      "original_phrase": "I concluded more expensive clothes last longer",
      "kernel_name": "quality-over-cost heuristic",
      "rationale": "A generalized purchasing rule is inferred that favors durability over low price."
    }}
  ]
}}
</JSON>

---------

### Your Turn

#### Input Format
Story:
{story}

Phrases:
{phrases}

---------

#### Output Format
#### Remember:
- Read the Story and Phrases. For each phrase, output a generalized kernel name and rationale following the given rules.
- **Always use the same `id` and `original_phrase` as in the input.** Copy `original_phrase` exactly from the input `text` (preserve case and punctuation). Use the same `id` value.
- The rationale must state the reason (features/role/relations that justify the kernel), not a tautology.
- Apply all **Delexicalization Rules** and **Quality Gates**.
- The generated abstractions phrase **must exclude** all **story-specific content words**.
- No traces of the **original entities should appear**.
- All content words **must be replaced** with **higher-level hypernyms**.


Output: A single JSON object exactly matching the schema described in Output Explanation.

Return ONLY one JSON object. Do not output anything before or after it.
Wrap the array inside <JSON> ... </JSON> tags.
Provide output in the following format:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": ...,
      "kernel_name": ...,
      "rationale": ...
    }},
    ...
  ]
}}
</JSON>

"""



prompt_abstraction_extraction4 = """
### Role Assignment
You are an assistant that generalizes narrative phrases into higher-level conceptual **kernel names**.
You read a short **Story** and a list of extracted **Phrases**.
For each phrase, output a concise abstract kernel name and a brief rationale.

---

### Task Definition
Input:
1. A *Story*.
2. A list of *Phrases* (concrete events, feelings, judgments, or actions).

Output for each phrase:
- **kernel_name**: a concise **noun phrase (1–5 words)** that is a true **hypernym** and reflects the phrase’s **role** (e.g., *awareness, identification, regulation, constraint, mechanism, outcome*).  
- **rationale**: **one short sentence** explaining why the kernel fits (state features/role/relations; avoid tautologies).

---

### Delexicalization Rules
- **No story-specific surface words** in `kernel_name`.  
- Replace names/places/objects with **general categories** (e.g., *bird*, *city*, *musical instrument*).  
- Mention participants in reasoning as roles (*AGENT, RECIPIENT, RESOURCE, LOCATION, INSTRUMENT*), but never output them in `kernel_name`.  
- Keep mechanisms only if central/causal.  
- Default to **mid-level abstraction**: remove concrete items and proper nouns but preserve essential causal mechanisms.

---

### Quality Checks *(silent; output only JSON array)*
1. **Hypernym**: “A(n) [phrase] is an instance of [kernel_name]” must be true.  
2. **Leakage**: No story-specific words in `kernel_name`.  
3. **Replacement**: Substituting with the kernel preserves the narrative gist.  
4. **Concision**: 1–5 words.  
5. **Consistency**: Distinguish near-synonyms by narrative role (e.g., *awareness* vs *regulation*).

---

### Output Format
Return a JSON object with array `results`. Each element must include:
- `id`: copied exactly from input.  
- `original_phrase`: copied exactly.  
- `kernel_name`: generalized concept.  
- `rationale`: one short explanatory sentence.  

Keep results in the same order as input.
---------

### Examples
**Example 1**

Story:
“David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.”

Phrases:
[
  {{ "id":"p1","text":"David noticed weight gain" }},
  {{ "id":"p2","text":"David examined his habits for a reason" }},
  {{ "id":"p3","text":"David Realized he ate too much fast food" }},
  {{ "id":"p4","text":"David Stopped going to burger places" }},
  {{ "id":"p5","text":"David Started a vegetarian diet" }},
  {{ "id":"p6","text":"David Felt better after a few weeks" }},
  {{ "id":"p7","text":"David had stopped eating unhealthy foods" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "David noticed weight gain",
      "kernel_name": "weight gain awareness",
      "rationale": "Recognition of a bodily change functions as initial problem detection that motivates subsequent steps."
    }},
    {{
      "id": "p2",
      "original_phrase": "David examined his habits for a reason",
      "kernel_name": "causal self-assessment",
      "rationale": "He analyzes personal behaviors to identify contributors to the issue."
    }},
    {{
      "id": "p3",
      "original_phrase": "David Realized he ate too much fast food",
      "kernel_name": "dietary cause identification",
      "rationale": "He attributes the problem to an excessive eating pattern that is modifiable."
    }},
    {{
      "id": "p4",
      "original_phrase": "David Stopped going to burger places",
      "kernel_name": "trigger avoidance",
      "rationale": "He removes environmental cues that facilitate the undesired intake."
    }},
    {{
      "id": "p5",
      "original_phrase": "David Started a vegetarian diet",
      "kernel_name": "health-oriented diet adoption",
      "rationale": "He implements a structured dietary pattern aimed at improving health outcomes."
    }},
    {{
      "id": "p6",
      "original_phrase": "David Felt better after a few weeks",
      "kernel_name": "improved well-being",
      "rationale": "A positive outcome follows the behavior changes over time."
    }},
    {{
      "id": "p7",
      "original_phrase": "David had stopped eating unhealthy foods",
      "kernel_name": "dietary risk reduction",
      "rationale": "Reduced intake of harmful items serves as a proximal mechanism supporting the improvement."
    }}
  ]
}}
</JSON>

---------

**Example 2**

Story:
“Eric and his wife had a daughter named Meg. Eric and Meg were very sad when Eric's wife passed away. Eric met a woman and married her 5 years after his wife died. Meg is finally happy with her new stepmother as she is very kind to her.”

Phrases:
[
  {{ "id":"p1","text":"Eric and his wife had Meg" }},
  {{ "id":"p2","text":"Erics wife passed away" }},
  {{ "id":"p3","text":"Eric and Meg were very sad" }},
  {{ "id":"p4","text":"Eric met a woman" }},
  {{ "id":"p5","text":"Eric married the woman five years later " }},
  {{ "id":"p6","text":"Meg was happy with her stepmother" }},
  {{ "id":"p7","text":"Megs stepmother is kind to her" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Eric and his wife had Meg",
      "kernel_name": "childbirth event",
      "rationale": "Establishes the family unit via the birth of a child without relying on names or timing specifics."
    }},
    {{
      "id": "p2",
      "original_phrase": "Erics wife passed away",
      "kernel_name": "spousal bereavement",
      "rationale": "A major loss that shapes subsequent emotions and choices."
    }},
    {{
      "id": "p3",
      "original_phrase": "Eric and Meg were very sad",
      "kernel_name": "grief response",
      "rationale": "Intense sadness arises as the emotional consequence of the loss."
    }},
    {{
      "id": "p4",
      "original_phrase": "Eric met a woman",
      "kernel_name": "new partner encounter",
      "rationale": "An initial contact begins a potential relationship trajectory."
    }},
    {{
      "id": "p5",
      "original_phrase": "Eric married the woman five years later ",
      "kernel_name": "remarriage after bereavement",
      "rationale": "A substantial delay culminates in forming a new marital bond following prior loss."
    }},
    {{
      "id": "p6",
      "original_phrase": "Meg was happy with her stepmother",
      "kernel_name": "positive stepfamily adjustment",
      "rationale": "The child’s contentment indicates successful adaptation to the new family structure."
    }},
    {{
      "id": "p7",
      "original_phrase": "Megs stepmother is kind to her",
      "kernel_name": "caregiver kindness",
      "rationale": "Supportive behavior from the caregiver plausibly contributes to the child’s positive adjustment."
    }}
  ]
}}
</JSON>

---------

**Example 3**

Story:
“There was a bug on the wall by the bed. Kate grabbed a shoe and killed it.”

Phrases:
[
  {{ "id":"p1","text":"Bug was on the wall by the bed" }},
  {{ "id":"p2","text":"Kate grabbed a shoe" }},
  {{ "id":"p3","text":"Kate killed the bug" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Bug was on the wall by the bed",
      "kernel_name": "household pest presence",
      "rationale": "An unwanted organism appears in a living space near a resting area, creating a nuisance context."
    }},
    {{
      "id": "p2",
      "original_phrase": "Kate grabbed a shoe",
      "kernel_name": "improvised tool selection",
      "rationale": "A readily available object is chosen to address the nuisance."
    }},
    {{
      "id": "p3",
      "original_phrase": "Kate killed the bug",
      "kernel_name": "pest elimination",
      "rationale": "The nuisance is resolved through direct removal."
    }}
  ]
}}
</JSON>

---------

**Example 4**

Story:
“I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

Phrases:
[
  {{ "id":"p1","text":"I bought a cheap jacket" }},
  {{ "id":"p2","text":"Jacket fell apart the next day" }},
  {{ "id":"p3","text":"I concluded more expensive clothes last longer" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "I bought a cheap jacket",
      "kernel_name": "low-cost purchase decision",
      "rationale": "The buyer prioritizes minimal price, setting up a durability tradeoff."
    }},
    {{
      "id": "p2",
      "original_phrase": "Jacket fell apart the next day",
      "kernel_name": "premature product failure",
      "rationale": "Rapid breakdown provides negative durability feedback."
    }},
    {{
      "id": "p3",
      "original_phrase": "I concluded more expensive clothes last longer",
      "kernel_name": "quality-over-cost heuristic",
      "rationale": "A generalized purchasing rule is inferred that favors durability over low price."
    }}
  ]
}}
</JSON>

---------

### Your Turn

#### Input Format
Story:
{story}

Phrases:
{phrases}

---------

#### Output Format
#### Remember:
- Read the Story and Phrases. For each phrase, output a generalized kernel name and rationale following the given rules.
- **Always use the same `id` and `original_phrase` as in the input.** Copy `original_phrase` exactly from the input `text` (preserve case and punctuation). Use the same `id` value.
- The rationale must state the reason (features/role/relations that justify the kernel), not a tautology.
- Apply all **Delexicalization Rules** and **Quality Gates**.
- The generated abstractions phrase **must exclude** all **story-specific content words**.
- No traces of the **original entities should appear**.
- All content words **must be replaced** with **higher-level hypernyms**.


Output: A single JSON object exactly matching the schema described in Output Explanation.

Return ONLY one JSON object. Do not output anything before or after it.
Wrap the array inside <JSON> ... </JSON> tags.
Provide output in the following format:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": ...,
      "kernel_name": ...,
      "rationale": ...
    }},
    ...
  ]
}}
</JSON>

"""

prompt_abstraction_extraction5 = """

### Role Assignment
You are a frame-extraction assistant. 
Your job is to read a short **Story** and a list of extracted **Phrases**, then assign exactly one concise semantic **Frame** to each phrase based on Frame Semantics. 
The **Frame** should capture the phrase’s core meaning in the context of the story.

### Task Definition
You will:
- Map each **Phrase** to one and only one **Frame** that best captures its meaning given the surrounding **Story** context.
- Use compact, nouny labels of at most **3 words**, **UPPERCASE** with **underscores**.
- Balance **specificity** and **generality**: avoid ultra-generic frames (e.g., ACTIVITY_START/STOP) and overfitted one-offs. Add a **domain** modifier only if it **materially disambiguates**.
- Encode **causal roles** when the narrative implies them.
- Avoid **metaphorical** frames and **meta** frames (no “reasoning,” “answering,” etc.). Focus on situational semantics grounded in the story.
- Be consistent across similar events (e.g., PROBLEM_RECOGNITION → CAUSE_IDENTIFICATION → TARGETED_CHANGE → OUTCOME → OUTCOME_CAUSE).

### Output Format
Return a single JSON object wrapped in **<JSON> ... </JSON>** tags with a top-level **results** array. For each phrase:
- **id**: the phrase identifier from input.
- **original_phrase**: the exact phrase text from input.
- **rationale**: a brief, step-by-step explanation (1–2 sentences) of how the frame was chosen using story context.
- **frame_name**: the final frame name (≤3 words, UPPERCASE_WITH_UNDERSCORES).

### Examples

**Example 1**

Story:
“David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.”

Phrases:
[
  {{ "id":"p1","text":"David noticed weight gain" }},
  {{ "id":"p2","text":"David examined his habits for a reason" }},
  {{ "id":"p3","text":"David Realized he ate too much fast food" }},
  {{ "id":"p4","text":"David Stopped going to burger places" }},
  {{ "id":"p5","text":"David Started a vegetarian diet" }},
  {{ "id":"p6","text":"David Felt better after a few weeks" }},
  {{ "id":"p7","text":"David had stopped eating unhealthy foods" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "David noticed weight gain",
      "rationale": "The phrase depicts recognition of a change in personal physical state, initiating the problem-awareness stage.",
      "frame_name": "WEIGHT_GAIN_RECOGNITION"
    }},
    {{
      "id": "p2",
      "original_phrase": "David examined his habits for a reason",
      "rationale": "He systematically reviews his own routines to identify a cause, which is scrutiny directed at habits.",
      "frame_name": "HABIT_SCRUTINY"
    }},
    {{
      "id": "p3",
      "original_phrase": "David Realized he ate too much fast food",
      "rationale": "He identifies a specific dietary factor as the cause of the problem, moving from suspicion to recognition.",
      "frame_name": "DIETARY_CAUSE_IDENTIFICATION"
    }},
    {{
      "id": "p4",
      "original_phrase": "David Stopped going to burger places",
      "rationale": "He targets the implicated source and avoids it as a corrective behavioral change.",
      "frame_name": "RESTAURANT_AVOIDANCE"
    }},
    {{
      "id": "p5",
      "original_phrase": "David Started a vegetarian diet",
      "rationale": "He adopts a new, sustained dietary practice as a solution strategy.",
      "frame_name": "VEGETARIAN_DIET_ADOPTION"
    }},
    {{
      "id": "p6",
      "original_phrase": "David Felt better after a few weeks",
      "rationale": "Following the interventions and some time, his health state improves.",
      "frame_name": "HEALTH_IMPROVEMENT"
    }},
    {{
      "id": "p7",
      "original_phrase": "David had stopped eating unhealthy foods",
      "rationale": "This event functions as the reason that explains the improvement reported earlier.",
      "frame_name": "HEALTH_IMPROVEMENT_CAUSE"
    }}
  ]
}}
</JSON>

**Example 2**

Story:
“Eric and his wife had a daughter named Meg. Eric and Meg were very sad when Eric's wife passed away. Eric met a woman and married her 5 years after his wife died. Meg is finally happy with her new stepmother as she is very kind to her.”

Phrases:
[
  {{ "id":"p1","text":"Eric and his wife had Meg" }},
  {{ "id":"p2","text":"Erics wife passed away" }},
  {{ "id":"p3","text":"Eric and Meg were very sad" }},
  {{ "id":"p4","text":"Eric met a woman" }},
  {{ "id":"p5","text":"Eric married the woman five years later " }},
  {{ "id":"p6","text":"Meg was happy with her stepmother" }},
  {{ "id":"p7","text":"Megs stepmother is kind to her" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Eric and his wife had Meg",
      "rationale": "This introduces the child’s birth and establishes the family relationship.",
      "frame_name": "CHILD_BIRTH"
    }},
    {{
      "id": "p2",
      "original_phrase": "Erics wife passed away",
      "rationale": "A spouse dies, creating loss and setting up the bereavement context.",
      "frame_name": "SPOUSE_DEATH"
    }},
    {{
      "id": "p3",
      "original_phrase": "Eric and Meg were very sad",
      "rationale": "Emotional response of grief due to the spouse/mother’s death.",
      "frame_name": "BEREAVEMENT_GRIEF"
    }},
    {{
      "id": "p4",
      "original_phrase": "Eric met a woman",
      "rationale": "A meeting that introduces a potential partner, preceding later marriage.",
      "frame_name": "PROSPECTIVE_PARTNER_MEETING"
    }},
    {{
      "id": "p5",
      "original_phrase": "Eric married the woman five years later ",
      "rationale": "After a delay, he enters a new marital union following prior spousal loss.",
      "frame_name": "REMARRIAGE"
    }},
    {{
      "id": "p6",
      "original_phrase": "Meg was happy with her stepmother",
      "rationale": "Meg’s affect indicates satisfaction with the new stepparent relationship.",
      "frame_name": "STEPPARENT_RELATIONSHIP_SATISFACTION"
    }},
    {{
      "id": "p7",
      "original_phrase": "Megs stepmother is kind to her",
      "rationale": "Kind behavior functions as the reason for Meg’s satisfaction.",
      "frame_name": "RELATIONSHIP_SATISFACTION_CAUSE"
    }}
  ]
}}
</JSON>

**Example 3**

Story:
“There was a bug on the wall by the bed. Kate grabbed a shoe and killed it.”

Phrases:
[
  {{ "id":"p1","text":"Bug was on the wall by the bed" }},
  {{ "id":"p2","text":"Kate grabbed a shoe" }},
  {{ "id":"p3","text":"Kate killed the bug" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Bug was on the wall by the bed",
      "rationale": "The scene establishes the presence of a pest at a specific location.",
      "frame_name": "PEST_PRESENCE"
    }},
    {{
      "id": "p2",
      "original_phrase": "Kate grabbed a shoe",
      "rationale": "She acquires an object as a tool to act on the situation.",
      "frame_name": "TOOL_ACQUISITION"
    }},
    {{
      "id": "p3",
      "original_phrase": "Kate killed the bug",
      "rationale": "She eliminates the identified pest, resolving the nuisance.",
      "frame_name": "PEST_ELIMINATION"
    }}
  ]
}}
</JSON>

**Example 4**

Story:
“I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

Phrases:
[
  {{ "id":"p1","text":"I bought a cheap jacket" }},
  {{ "id":"p2","text":"Jacket fell apart the next day" }},
  {{ "id":"p3","text":"I concluded more expensive clothes last longer" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "I bought a cheap jacket",
      "rationale": "The purchase emphasizes very low cost, setting up a later quality issue.",
      "frame_name": "LOW_COST_PURCHASE"
    }},
    {{
      "id": "p2",
      "original_phrase": "Jacket fell apart the next day",
      "rationale": "The item quickly fails, indicating poor durability.",
      "frame_name": "DURABILITY_FAILURE"
    }},
    {{
      "id": "p3",
      "original_phrase": "I concluded more expensive clothes last longer",
      "rationale": "The narrator generalizes from the failure and adopts a new buying principle.",
      "frame_name": "PURCHASING_STRATEGY_ADOPTION"
    }}
  ]
}}
</JSON>

### Your Turn

#### Input Format
Story:
{story}

Phrases:
{phrases}

#### Output Format

#### Remember:
- Assign exactly **one** best-fitting **Frame** per **Phrase** using the **Story** context.
- Keep frames ≤ **3 words**, **UPPERCASE_WITH_UNDERSCORES**; avoid metaphors and meta-frames.
- Balance specificity vs. generality; add domain modifiers only when they clarify meaning.
- Encode causal roles explicitly (**..._CAUSE** or **..._RESULT**) when appropriate.
- Avoid overly generic buckets (e.g., ACTIVITY_START/STOP) when a targeted alternative exists.
- Provide a brief, step-by-step **rationale** (1–2 sentences) explaining the mapping.


Output: A single JSON object exactly matching the schema described in Output Explanation.

Return ONLY one JSON object. Do not output anything before or after it.
Wrap the array inside <JSON> ... </JSON> tags.
Provide output in the following format:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": ...,
      "rationale": ...,
      "frame_name": ...
    }},
    ...
  ]
}}

"""


prompt_abstraction_extraction6 = """

### Role Assignment
You are a frame-generalization assistant. 
Your job is to read a short **Story**, a set of **Phrases**, and their existing **Previous_Frames**, then produce a more **General_Frame** (a parent-class abstraction) for each phrase that remains faithful to the story’s meaning.

### Task Definition
You will:
- Generalize each **Previous_Frame** to a broader, cross-domain **General_Frame** that still captures the phrase’s core meaning in the **Story** context.
- Aim for **parent classes** of the current frames by abstracting the **head concept**.
- Keep **causal roles explicit** when the narrative implies them because they generalize robustly across domains.
- **Drop domain modifiers** unless they are essential for disambiguation; prefer **cross-domain** applicability over narrow specifics.
- Use **≤ 3 words**, **UPPERCASE_WITH_UNDERSCORES**, and prefer concise, noun-like labels.
- Avoid metaphorical or meta frames; keep frames grounded in situational semantics.

### Output Format
Return a single JSON object wrapped in **<JSON> ... </JSON>** tags with a top-level **results** array. For each phrase, include:
- **id**: the phrase identifier from input.
- **original_phrase**: the phrase text from input.
- **previous_frame**: the original, more specific frame provided.
- **rationale**: a brief (1–2 sentences) explanation of how you generalized from **previous_frame** to the new **frame_name**, using story context.
- **frame_name**: the final, more general frame name (≤3 words, UPPERCASE_WITH_UNDERSCORES).

### Examples

**Example 1**

Story:
“David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.”

Phrases and previous frames
[
  {{ "id":"p1","phrase":"David noticed weight gain", "previous_frame":"WEIGHT_GAIN_RECOGNITION" }},
  {{ "id":"p2","phrase":"David examined his habits for a reason", "previous_frame":"HABIT_SCRUTINY" }},
  {{ "id":"p3","phrase":"David Realized he ate too much fast food", "previous_frame":"DIETARY_CAUSE_IDENTIFICATION" }},
  {{ "id":"p4","phrase":"David Stopped going to burger places", "previous_frame":"RESTAURANT_AVOIDANCE" }},
  {{ "id":"p5","phrase":"David Started a vegetarian diet", "previous_frame":"VEGETARIAN_DIET_ADOPTION" }},
  {{ "id":"p6","phrase":"David Felt better after a few weeks", "previous_frame":"HEALTH_IMPROVEMENT" }},
  {{ "id":"p7","phrase":"David had stopped eating unhealthy foods", "previous_frame":"HEALTH_IMPROVEMENT_CAUSE" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "David noticed weight gain",
      "previous_frame": "WEIGHT_GAIN_RECOGNITION",
      "rationale": "Abstract from a weight-specific recognition to a domain-agnostic recognition of a problem/change.",
      "frame_name": "PROBLEM_RECOGNITION"
    }},
    {{
      "id": "p2",
      "original_phrase": "David examined his habits for a reason",
      "previous_frame": "HABIT_SCRUTINY",
      "rationale": "Generalize targeted habit review to a broader self-directed assessment process.",
      "frame_name": "SELF_ASSESSMENT"
    }},
    {{
      "id": "p3",
      "original_phrase": "David Realized he ate too much fast food",
      "previous_frame": "DIETARY_CAUSE_IDENTIFICATION",
      "rationale": "Remove the dietary modifier and keep the core act of finding a cause.",
      "frame_name": "CAUSE_IDENTIFICATION"
    }},
    {{
      "id": "p4",
      "original_phrase": "David Stopped going to burger places",
      "previous_frame": "RESTAURANT_AVOIDANCE",
      "rationale": "Lift from a specific target (restaurants) to general purposeful avoidance behavior.",
      "frame_name": "BEHAVIOR_AVOIDANCE"
    }},
    {{
      "id": "p5",
      "original_phrase": "David Started a vegetarian diet",
      "previous_frame": "VEGETARIAN_DIET_ADOPTION",
      "rationale": "Drop the dietary subtype and keep the adoption of a new sustained behavior.",
      "frame_name": "BEHAVIOR_ADOPTION"
    }},
    {{
      "id": "p6",
      "original_phrase": "David Felt better after a few weeks",
      "previous_frame": "HEALTH_IMPROVEMENT",
      "rationale": "Keep the improvement concept but broaden from health-specific to general wellbeing.",
      "frame_name": "WELLBEING_IMPROVEMENT"
    }},
    {{
      "id": "p7",
      "original_phrase": "David had stopped eating unhealthy foods",
      "previous_frame": "HEALTH_IMPROVEMENT_CAUSE",
      "rationale": "Retain the causal role while removing domain detail to make it cross-domain.",
      "frame_name": "IMPROVEMENT_CAUSE"
    }}
  ]
}}
</JSON>

**Example 2**

Story:
“Eric and his wife had a daughter named Meg. Eric and Meg were very sad when Eric's wife passed away. Eric met a woman and married her 5 years after his wife died. Meg is finally happy with her new stepmother as she is very kind to her.”

Phrases and previous frames
[
  {{ "id":"p1","phrase":"Eric and his wife had Meg", "previous_frame":"CHILD_BIRTH" }},
  {{ "id":"p2","phrase":"Erics wife passed away", "previous_frame":"SPOUSE_DEATH" }},
  {{ "id":"p3","phrase":"Eric and Meg were very sad", "previous_frame":"BEREAVEMENT_GRIEF" }},
  {{ "id":"p4","phrase":"Eric met a woman", "previous_frame":"PROSPECTIVE_PARTNER_MEETING" }},
  {{ "id":"p5","phrase":"Eric married the woman five years later ", "previous_frame":"REMARRIAGE" }},
  {{ "id":"p6","phrase":"Meg was happy with her stepmother", "previous_frame":"STEPPARENT_RELATIONSHIP_SATISFACTION" }},
  {{ "id":"p7","phrase":"Megs stepmother is kind to her", "previous_frame":"RELATIONSHIP_SATISFACTION_CAUSE" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Eric and his wife had Meg",
      "previous_frame": "CHILD_BIRTH",
      "rationale": "Lift from the specific birthing event to a broader family expansion concept.",
      "frame_name": "FAMILY_ADDITION"
    }},
    {{
      "id": "p2",
      "original_phrase": "Erics wife passed away",
      "previous_frame": "SPOUSE_DEATH",
      "rationale": "Remove the spouse subtype and keep the generic death event.",
      "frame_name": "DEATH_EVENT"
    }},
    {{
      "id": "p3",
      "original_phrase": "Eric and Meg were very sad",
      "previous_frame": "BEREAVEMENT_GRIEF",
      "rationale": "Generalize from grief due to loss to a broader negative emotional state.",
      "frame_name": "EMOTIONAL_DISTRESS"
    }},
    {{
      "id": "p4",
      "original_phrase": "Eric met a woman",
      "previous_frame": "PROSPECTIVE_PARTNER_MEETING",
      "rationale": "Drop the partner intention and keep the social encounter.",
      "frame_name": "SOCIAL_MEETING"
    }},
    {{
      "id": "p5",
      "original_phrase": "Eric married the woman five years later ",
      "previous_frame": "REMARRIAGE",
      "rationale": "Abstract from remarriage to the general entering of a marital union.",
      "frame_name": "MARITAL_UNION"
    }},
    {{
      "id": "p6",
      "original_phrase": "Meg was happy with her stepmother",
      "previous_frame": "STEPPARENT_RELATIONSHIP_SATISFACTION",
      "rationale": "Remove the stepparent subtype and retain satisfaction within a relationship.",
      "frame_name": "RELATIONSHIP_SATISFACTION"
    }},
    {{
      "id": "p7",
      "original_phrase": "Megs stepmother is kind to her",
      "previous_frame": "RELATIONSHIP_SATISFACTION_CAUSE",
      "rationale": "Preserve the causal role while generalizing away from specific traits.",
      "frame_name": "SATISFACTION_CAUSE"
    }}
  ]
}}
</JSON>

**Example 3**

Story:
“There was a bug on the wall by the bed. Kate grabbed a shoe and killed it.”

Phrases and previous frames
[
  {{ "id":"p1","phrase":"Bug was on the wall by the bed", "previous_frame":"PEST_PRESENCE" }},
  {{ "id":"p2","phrase":"Kate grabbed a shoe", "previous_frame":"TOOL_ACQUISITION" }},
  {{ "id":"p3","phrase":"Kate killed the bug", "previous_frame":"PEST_ELIMINATION" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Bug was on the wall by the bed",
      "previous_frame": "PEST_PRESENCE",
      "rationale": "Generalize from pest-specific context to any unwanted entity being present.",
      "frame_name": "UNWANTED_PRESENCE"
    }},
    {{
      "id": "p2",
      "original_phrase": "Kate grabbed a shoe",
      "previous_frame": "TOOL_ACQUISITION",
      "rationale": "Abstract from tool-specific grabbing to acquiring a resource for action.",
      "frame_name": "RESOURCE_ACQUISITION"
    }},
    {{
      "id": "p3",
      "original_phrase": "Kate killed the bug",
      "previous_frame": "PEST_ELIMINATION",
      "rationale": "Lift from pest-killing to a general resolution of the identified problem.",
      "frame_name": "PROBLEM_RESOLUTION"
    }}
  ]
}}
</JSON>

**Example 4**

Story:
“I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

Phrases and previous frames
[
  {{ "id":"p1","phrase":"I bought a cheap jacket", "previous_frame":"LOW_COST_PURCHASE" }},
  {{ "id":"p2","phrase":"Jacket fell apart the next day", "previous_frame":"DURABILITY_FAILURE" }},
  {{ "id":"p3","phrase":"I concluded more expensive clothes last longer", "previous_frame":"PURCHASING_STRATEGY_ADOPTION" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "I bought a cheap jacket",
      "previous_frame": "LOW_COST_PURCHASE",
      "rationale": "Remove the cost qualifier and retain the core purchasing event.",
      "frame_name": "PURCHASE_EVENT"
    }},
    {{
      "id": "p2",
      "original_phrase": "Jacket fell apart the next day",
      "previous_frame": "DURABILITY_FAILURE",
      "rationale": "Generalize from durability-specific failure to a broad product failure outcome.",
      "frame_name": "PRODUCT_FAILURE"
    }},
    {{
      "id": "p3",
      "original_phrase": "I concluded more expensive clothes last longer",
      "previous_frame": "PURCHASING_STRATEGY_ADOPTION",
      "rationale": "Keep the adoption-of-approach concept while dropping domain details.",
      "frame_name": "STRATEGY_ADOPTION"
    }}
  ]
}}
</JSON>

### Your Turn

#### Input Format
Story:
{story}

Phrases and previous frames
{phrases}

#### Remember:
- Generalize each **Previous_Frame** to a broader **General_Frame** while preserving the phrase’s meaning in the **Story**.
- Prefer parent-class abstractions; keep **causal roles** (**..._CAUSE**, **..._RESULT**) when present.
- Drop domain modifiers unless needed for clarity; aim for **cross-domain** applicability.
- Keep frames **≤ 3 words**, **UPPERCASE_WITH_UNDERSCORES**, concise and noun-like.
- Provide a brief, concrete **rationale** (1–2 sentences) explaining your generalization.

Output: A single JSON object exactly matching the schema described in Output Explanation.

Return ONLY one JSON object. Do not output anything before or after it.
Wrap the array inside <JSON> ... </JSON> tags.
Provide output in the following format:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": ...,
      "previous_frame": ...,
      "rationale": ...,
      "frame_name": ...
    }},
    ...
  ]
}}


"""


prompt_abstraction_extraction7 = """

### Role Assignment
You are a frame-generalization assistant. 
Your job is to read a short **Story**, a set of **Phrases**, and their existing **Previous_Frames**, then produce a more **General_Frame** (a higher-level parent abstraction) for each phrase that remains faithful to the story’s meaning.

### Task Definition
You will:
- Roll up each **Previous_Frame** to a broader, cross-domain **General_Frame** by collapsing domain-specific and event-type modifiers into very broad “head concepts.”
- Preserve explicit **causal roles** when indicated (e.g., **..._CAUSE**, **..._RESULT**) because these generalize well across domains.
- Prefer concise, noun-like heads; keep labels **≤ 3 words**, **UPPERCASE_WITH_UNDERSCORES**.
- Avoid metaphorical or meta frames; keep frames grounded in situational semantics.
- Ensure the new **General_Frame** still correctly represents the phrase in the context of the **Story**.

### Output Format
Return a single JSON object wrapped in **<JSON> ... </JSON>** tags with a top-level **results** array. For each phrase, include:
- **id**: the phrase identifier from input.
- **original_phrase**: the phrase text from input.
- **previous_frame**: the provided, more specific frame.
- **rationale**: a brief (1–2 sentences) explanation of how you generalized from **previous_frame** to the new **frame_name**, using story context.
- **frame_name**: the final, more general frame name (≤3 words, UPPERCASE_WITH_UNDERSCORES).

### Examples

**Example 1**

Story:
“David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.”

Phrases and previous frames
[
  {{ "id":"p1","phrase":"David noticed weight gain", "previous_frame":"PROBLEM_RECOGNITION" }},
  {{ "id":"p2","phrase":"David examined his habits for a reason", "previous_frame":"SELF_ASSESSMENT" }},
  {{ "id":"p3","phrase":"David Realized he ate too much fast food", "previous_frame":"CAUSE_IDENTIFICATION" }},
  {{ "id":"p4","phrase":"David Stopped going to burger places", "previous_frame":"BEHAVIOR_AVOIDANCE" }},
  {{ "id":"p5","phrase":"David Started a vegetarian diet", "previous_frame":"BEHAVIOR_ADOPTION" }},
  {{ "id":"p6","phrase":"David Felt better after a few weeks", "previous_frame":"WELLBEING_IMPROVEMENT" }},
  {{ "id":"p7","phrase":"David had stopped eating unhealthy foods", "previous_frame":"IMPROVEMENT_CAUSE" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "David noticed weight gain",
      "previous_frame": "PROBLEM_RECOGNITION",
      "rationale": "Generalize from recognizing a problem to the broad head concept of becoming aware.",
      "frame_name": "AWARENESS"
    }},
    {{
      "id": "p2",
      "original_phrase": "David examined his habits for a reason",
      "previous_frame": "SELF_ASSESSMENT",
      "rationale": "Lift from self-assessment to a broad internal contemplation/evaluation process.",
      "frame_name": "REFLECTION"
    }},
    {{
      "id": "p3",
      "original_phrase": "David Realized he ate too much fast food",
      "previous_frame": "CAUSE_IDENTIFICATION",
      "rationale": "Collapse to a head that encodes inferring causality without domain detail.",
      "frame_name": "CAUSAL_INFERENCE"
    }},
    {{
      "id": "p4",
      "original_phrase": "David Stopped going to burger places",
      "previous_frame": "BEHAVIOR_AVOIDANCE",
      "rationale": "Retain the avoidance notion while dropping behavioral specificity.",
      "frame_name": "AVOIDANCE"
    }},
    {{
      "id": "p5",
      "original_phrase": "David Started a vegetarian diet",
      "previous_frame": "BEHAVIOR_ADOPTION",
      "rationale": "Reduce to the broad head concept of taking on something new.",
      "frame_name": "ADOPTION"
    }},
    {{
      "id": "p6",
      "original_phrase": "David Felt better after a few weeks",
      "previous_frame": "WELLBEING_IMPROVEMENT",
      "rationale": "Abstract to the general notion of a positive change.",
      "frame_name": "IMPROVEMENT"
    }},
    {{
      "id": "p7",
      "original_phrase": "David had stopped eating unhealthy foods",
      "previous_frame": "IMPROVEMENT_CAUSE",
      "rationale": "Preserve the causal role while removing domain specifics.",
      "frame_name": "CAUSE"
    }}
  ]
}}
</JSON>

**Example 2**

Story:
“Eric and his wife had a daughter named Meg. Eric and Meg were very sad when Eric's wife passed away. Eric met a woman and married her 5 years after his wife died. Meg is finally happy with her new stepmother as she is very kind to her.”

Phrases and previous frames
[
  {{ "id":"p1","phrase":"Eric and his wife had Meg", "previous_frame":"FAMILY_ADDITION" }},
  {{ "id":"p2","phrase":"Erics wife passed away", "previous_frame":"DEATH_EVENT" }},
  {{ "id":"p3","phrase":"Eric and Meg were very sad", "previous_frame":"EMOTIONAL_DISTRESS" }},
  {{ "id":"p4","phrase":"Eric met a woman", "previous_frame":"SOCIAL_MEETING" }},
  {{ "id":"p5","phrase":"Eric married the woman five years later ", "previous_frame":"MARITAL_UNION" }},
  {{ "id":"p6","phrase":"Meg was happy with her stepmother", "previous_frame":"RELATIONSHIP_SATISFACTION" }},
  {{ "id":"p7","phrase":"Megs stepmother is kind to her", "previous_frame":"SATISFACTION_CAUSE" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Eric and his wife had Meg",
      "previous_frame": "FAMILY_ADDITION",
      "rationale": "Generalize the family-specific addition to a broad notion of adding/expanding.",
      "frame_name": "ADDITION"
    }},
    {{
      "id": "p2",
      "original_phrase": "Erics wife passed away",
      "previous_frame": "DEATH_EVENT",
      "rationale": "Lift from a specific death event to the abstract concept of loss.",
      "frame_name": "LOSS"
    }},
    {{
      "id": "p3",
      "original_phrase": "Eric and Meg were very sad",
      "previous_frame": "EMOTIONAL_DISTRESS",
      "rationale": "Keep the negative affect but condense to a broad distress head.",
      "frame_name": "DISTRESS"
    }},
    {{
      "id": "p4",
      "original_phrase": "Eric met a woman",
      "previous_frame": "SOCIAL_MEETING",
      "rationale": "Reduce to the general notion of encountering another person.",
      "frame_name": "ENCOUNTER"
    }},
    {{
      "id": "p5",
      "original_phrase": "Eric married the woman five years later ",
      "previous_frame": "MARITAL_UNION",
      "rationale": "Abstract the marital subtype to the broader union concept.",
      "frame_name": "UNION"
    }},
    {{
      "id": "p6",
      "original_phrase": "Meg was happy with her stepmother",
      "previous_frame": "RELATIONSHIP_SATISFACTION",
      "rationale": "Keep the positive evaluation but collapse to the general satisfaction head.",
      "frame_name": "SATISFACTION"
    }},
    {{
      "id": "p7",
      "original_phrase": "Megs stepmother is kind to her",
      "previous_frame": "SATISFACTION_CAUSE",
      "rationale": "Maintain the causal role while removing specific attributes.",
      "frame_name": "CAUSE"
    }}
  ]
}}
</JSON>

**Example 3**

Story:
“There was a bug on the wall by the bed. Kate grabbed a shoe and killed it.”

Phrases and previous frames
[
  {{ "id":"p1","phrase":"Bug was on the wall by the bed", "previous_frame":"UNWANTED_PRESENCE" }},
  {{ "id":"p2","phrase":"Kate grabbed a shoe", "previous_frame":"RESOURCE_ACQUISITION" }},
  {{ "id":"p3","phrase":"Kate killed the bug", "previous_frame":"PROBLEM_RESOLUTION" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Bug was on the wall by the bed",
      "previous_frame": "UNWANTED_PRESENCE",
      "rationale": "Strip the 'unwanted' qualifier to the bare presence head.",
      "frame_name": "PRESENCE"
    }},
    {{
      "id": "p2",
      "original_phrase": "Kate grabbed a shoe",
      "previous_frame": "RESOURCE_ACQUISITION",
      "rationale": "Generalize to the acquisition head, independent of resource/tool type.",
      "frame_name": "ACQUISITION"
    }},
    {{
      "id": "p3",
      "original_phrase": "Kate killed the bug",
      "previous_frame": "PROBLEM_RESOLUTION",
      "rationale": "Collapse to the broad concept of resolving a situation.",
      "frame_name": "RESOLUTION"
    }}
  ]
}}
</JSON>

**Example 4**

Story:
“I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

Phrases and previous frames
[
  {{ "id":"p1","phrase":"I bought a cheap jacket", "previous_frame":"PURCHASE_EVENT" }},
  {{ "id":"p2","phrase":"Jacket fell apart the next day", "previous_frame":"PRODUCT_FAILURE" }},
  {{ "id":"p3","phrase":"I concluded more expensive clothes last longer", "previous_frame":"STRATEGY_ADOPTION" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "I bought a cheap jacket",
      "previous_frame": "PURCHASE_EVENT",
      "rationale": "Lift from purchase-event to the abstract head for obtaining something.",
      "frame_name": "ACQUISITION"
    }},
    {{
      "id": "p2",
      "original_phrase": "Jacket fell apart the next day",
      "previous_frame": "PRODUCT_FAILURE",
      "rationale": "Reduce to the general notion of failure without domain qualifiers.",
      "frame_name": "FAILURE"
    }},
    {{
      "id": "p3",
      "original_phrase": "I concluded more expensive clothes last longer",
      "previous_frame": "STRATEGY_ADOPTION",
      "rationale": "Retain the adoption act while removing strategy/purchasing specifics.",
      "frame_name": "ADOPTION"
    }}
  ]
}}
</JSON>

### Your Turn

#### Input Format
Story:
{story}

Phrases and previous frames
{phrases}


#### Remember:
- Roll up each **Previous_Frame** to a broader **General_Frame** by collapsing domain/event-type details into head concepts.
- Preserve explicit **causal roles** (**..._CAUSE**, **..._RESULT**) when present.
- Prefer concise, noun-like heads; keep **≤ 3 words**, **UPPERCASE_WITH_UNDERSCORES**.
- Keep frames grounded in situational semantics (no metaphors or meta frames).
- Ensure each **frame_name** still fits the **Story** context; provide a clear 1–2 sentence **rationale**.

Output: A single JSON object exactly matching the schema described in Output Explanation.

Return ONLY one JSON object. Do not output anything before or after it.
Wrap the array inside <JSON> ... </JSON> tags.
Provide output in the following format:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": ...,
      "previous_frame": ...,
      "rationale": ...,
      "frame_name": ...
    }},
    ...
  ]
}}


"""



prompt_abstraction_extraction9 = """

### Role Assignment
You are a frame-extraction assistant. 
Your job is to read a short **Story** and a list of extracted **Phrases**, then assign exactly one concise semantic **Frame** to each phrase. 
Each **Frame** must follow the schema **[DETAIL]_[ROOT]**, capturing the phrase’s core meaning in the context of the story.

### Task Definition
Use the following specification to construct each **Frame**:

**ROOT**
- One word, **noun-like**, capturing the event type.

**DETAIL**
- Clarifies what specifically the ROOT applies to; provides minimal story signal.
- 1–2 words (tokens) joined by underscores.

**[DETAIL]_[ROOT] frames — story-aware**
- **Form:** `[DETAIL]_[ROOT]`
- **Goal:** precisely capture the event with a minimal but meaningful story signal.

**Rules**
- **Pick the ROOT first** (what the event is mainly about). Exactly **one word**.
- **Choose the smallest informative DETAIL** that grounds the ROOT (1–2 tokens).
- **Formatting:** all **UPPERCASE_WITH_UNDERSCORES**; total tokens ≤ **3** (DETAIL can be 1–2; ROOT is 1).
- Avoid ultra-generic frames (e.g., ACTIVITY_START/STOP) and avoid overfitted one-offs.
- Encode causal roles only when explicit in the text (e.g., …_CAUSE, …_RESULT).
- **Hard consistency rule:** the ROOT named in your rationale must exactly match the suffix of **frame_name**.

### Output Format
Return a single JSON object wrapped in **<JSON> ... </JSON>** tags with a top-level **results** array. For each phrase include:
- **id**: the phrase identifier from input.
- **original_phrase**: the exact phrase text from input.
- **rationale**: write in three explicit parts:
  - **ROOT:** “the event is about … because … ; so a good root is **ROOT_NAME**.”
  - **DETAIL:** “in this story, it applies to … because … ; so a good detail name is **DETAIL_NAME**.”
  - **FRAME:** “**DETAIL_NAME**_**ROOT_NAME**.”
- **frame_name**: the final frame name in **[DETAIL]_[ROOT]** form (UPPERCASE_WITH_UNDERSCORES, ≤3 tokens).

### Examples

**Example 1**

Story:
“David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.”

Phrases:
[
  {{ "id":"p1","text":"David noticed weight gain" }},
  {{ "id":"p2","text":"David examined his habits for a reason" }},
  {{ "id":"p3","text":"David Realized he ate too much fast food" }},
  {{ "id":"p4","text":"David Stopped going to burger places" }},
  {{ "id":"p5","text":"David Started a vegetarian diet" }},
  {{ "id":"p6","text":"David Felt better after a few weeks" }},
  {{ "id":"p7","text":"David had stopped eating unhealthy foods" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "David noticed weight gain",
      "rationale": "ROOT: the event is about becoming aware of a state because David explicitly notices a change; so a good root is RECOGNITION. DETAIL: in this story, it applies to a specific condition—gaining weight—because that is the state recognized; so a good detail name is WEIGHT_GAIN. FRAME: WEIGHT_GAIN_RECOGNITION.",
      "frame_name": "WEIGHT_GAIN_RECOGNITION"
    }},
    {{
      "id": "p2",
      "original_phrase": "David examined his habits for a reason",
      "rationale": "ROOT: the event is about systematic checking because he inspects behavior to find an explanation; so a good root is SCRUTINY. DETAIL: in this story, it applies to his habits because the examination targets routines; so a good detail name is HABIT. FRAME: HABIT_SCRUTINY.",
      "frame_name": "HABIT_SCRUTINY"
    }},
    {{
      "id": "p3",
      "original_phrase": "David Realized he ate too much fast food",
      "rationale": "ROOT: the event is about pinpointing a cause because he recognizes what explains the issue; so a good root is IDENTIFICATION. DETAIL: in this story, it applies to diet because overconsuming fast food is the causal factor; so a good detail name is DIETARY_CAUSE. FRAME: DIETARY_CAUSE_IDENTIFICATION.",
      "frame_name": "DIETARY_CAUSE_IDENTIFICATION"
    }},
    {{
      "id": "p4",
      "original_phrase": "David Stopped going to burger places",
      "rationale": "ROOT: the event is about deliberately steering clear because he chooses not to attend certain places; so a good root is AVOIDANCE. DETAIL: in this story, it applies to restaurants because burger places are the target; so a good detail name is RESTAURANT. FRAME: RESTAURANT_AVOIDANCE.",
      "frame_name": "RESTAURANT_AVOIDANCE"
    }},
    {{
      "id": "p5",
      "original_phrase": "David Started a vegetarian diet",
      "rationale": "ROOT: the event is about taking on a new practice because he begins a sustained dietary pattern; so a good root is ADOPTION. DETAIL: in this story, it applies to a vegetarian regimen because that is the new practice; so a good detail name is VEGETARIAN_DIET. FRAME: VEGETARIAN_DIET_ADOPTION.",
      "frame_name": "VEGETARIAN_DIET_ADOPTION"
    }},
    {{
      "id": "p6",
      "original_phrase": "David Felt better after a few weeks",
      "rationale": "ROOT: the event is about a positive change of state because his condition improves; so a good root is IMPROVEMENT. DETAIL: in this story, it applies to health because feeling better refers to wellbeing; so a good detail name is HEALTH. FRAME: HEALTH_IMPROVEMENT.",
      "frame_name": "HEALTH_IMPROVEMENT"
    }},
    {{
      "id": "p7",
      "original_phrase": "David had stopped eating unhealthy foods",
      "rationale": "ROOT: the event is about providing a reason because it explains why improvement occurred; so a good root is CAUSE. DETAIL: in this story, it applies to the health improvement because that is what the cause explains; so a good detail name is HEALTH_IMPROVEMENT. FRAME: HEALTH_IMPROVEMENT_CAUSE.",
      "frame_name": "HEALTH_IMPROVEMENT_CAUSE"
    }}
  ]
}}
</JSON>

**Example 2**

Story:
“Eric and his wife had a daughter named Meg. Eric and Meg were very sad when Eric's wife passed away. Eric met a woman and married her 5 years after his wife died. Meg is finally happy with her new stepmother as she is very kind to her.”

Phrases:
[
  {{ "id":"p1","text":"Eric and his wife had Meg" }},
  {{ "id":"p2","text":"Erics wife passed away" }},
  {{ "id":"p3","text":"Eric and Meg were very sad" }},
  {{ "id":"p4","text":"Eric met a woman" }},
  {{ "id":"p5","text":"Eric married the woman five years later " }},
  {{ "id":"p6","text":"Meg was happy with her stepmother" }},
  {{ "id":"p7","text":"Megs stepmother is kind to her" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Eric and his wife had Meg",
      "rationale": "ROOT: the event is about a birth because a new person enters the family; so a good root is BIRTH. DETAIL: in this story, it applies to a child because the newborn is their daughter; so a good detail name is CHILD. FRAME: CHILD_BIRTH.",
      "frame_name": "CHILD_BIRTH"
    }},
    {{
      "id": "p2",
      "original_phrase": "Erics wife passed away",
      "rationale": "ROOT: the event is about death because a person’s life ends; so a good root is DEATH. DETAIL: in this story, it applies to the spouse because the deceased is Eric’s wife; so a good detail name is SPOUSE. FRAME: SPOUSE_DEATH.",
      "frame_name": "SPOUSE_DEATH"
    }},
    {{
      "id": "p3",
      "original_phrase": "Eric and Meg were very sad",
      "rationale": "ROOT: the event is about grief because strong sorrow follows a loss; so a good root is GRIEF. DETAIL: in this story, it applies to bereavement because the sadness is due to the death; so a good detail name is BEREAVEMENT. FRAME: BEREAVEMENT_GRIEF.",
      "frame_name": "BEREAVEMENT_GRIEF"
    }},
    {{
      "id": "p4",
      "original_phrase": "Eric met a woman",
      "rationale": "ROOT: the event is about a social encounter because a meeting occurs; so a good root is MEETING. DETAIL: in this story, it applies to a prospective partner because the encounter precedes marriage; so a good detail name is PROSPECTIVE_PARTNER. FRAME: PROSPECTIVE_PARTNER_MEETING.",
      "frame_name": "PROSPECTIVE_PARTNER_MEETING"
    }},
    {{
      "id": "p5",
      "original_phrase": "Eric married the woman five years later ",
      "rationale": "ROOT: the event is about forming a union because marriage is entered; so a good root is UNION. DETAIL: in this story, it applies to remarriage because this union follows prior loss; so a good detail name is REMARRIAGE. FRAME: REMARRIAGE_UNION.",
      "frame_name": "REMARRIAGE_UNION"
    }},
    {{
      "id": "p6",
      "original_phrase": "Meg was happy with her stepmother",
      "rationale": "ROOT: the event is about satisfaction because it expresses positive evaluation; so a good root is SATISFACTION. DETAIL: in this story, it applies to the stepparent relationship because that is the evaluated bond; so a good detail name is STEPPARENT_RELATIONSHIP. FRAME: STEPPARENT_RELATIONSHIP_SATISFACTION.",
      "frame_name": "STEPPARENT_RELATIONSHIP_SATISFACTION"
    }},
    {{
      "id": "p7",
      "original_phrase": "Megs stepmother is kind to her",
      "rationale": "ROOT: the event is about giving a reason because kindness explains the satisfaction; so a good root is CAUSE. DETAIL: in this story, it applies to relationship satisfaction because that is what is explained; so a good detail name is RELATIONSHIP_SATISFACTION. FRAME: RELATIONSHIP_SATISFACTION_CAUSE.",
      "frame_name": "RELATIONSHIP_SATISFACTION_CAUSE"
    }}
  ]
}}
</JSON>

**Example 3**

Story:
“There was a bug on the wall by the bed. Kate grabbed a shoe and killed it.”

Phrases:
[
  {{ "id":"p1","text":"Bug was on the wall by the bed" }},
  {{ "id":"p2","text":"Kate grabbed a shoe" }},
  {{ "id":"p3","text":"Kate killed the bug" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Bug was on the wall by the bed",
      "rationale": "ROOT: the event is about presence because the entity exists at a location; so a good root is PRESENCE. DETAIL: in this story, it applies to a pest because the entity is an unwanted bug; so a good detail name is PEST. FRAME: PEST_PRESENCE.",
      "frame_name": "PEST_PRESENCE"
    }},
    {{
      "id": "p2",
      "original_phrase": "Kate grabbed a shoe",
      "rationale": "ROOT: the event is about acquisition because she obtains something to use; so a good root is ACQUISITION. DETAIL: in this story, it applies to a tool because the shoe is used instrumentally; so a good detail name is TOOL. FRAME: TOOL_ACQUISITION.",
      "frame_name": "TOOL_ACQUISITION"
    }},
    {{
      "id": "p3",
      "original_phrase": "Kate killed the bug",
      "rationale": "ROOT: the event is about elimination because the unwanted entity is removed; so a good root is ELIMINATION. DETAIL: in this story, it applies to a pest because the target is the bug; so a good detail name is PEST. FRAME: PEST_ELIMINATION.",
      "frame_name": "PEST_ELIMINATION"
    }}
  ]
}}
</JSON>

**Example 4**

Story:
“I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

Phrases:
[
  {{ "id":"p1","text":"I bought a cheap jacket" }},
  {{ "id":"p2","text":"Jacket fell apart the next day" }},
  {{ "id":"p3","text":"I concluded more expensive clothes last longer" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "I bought a cheap jacket",
      "rationale": "ROOT: the event is about purchase because the narrator acquires an item via buying; so a good root is PURCHASE. DETAIL: in this story, it applies to low cost because the price is emphasized as a dollar; so a good detail name is LOW_COST. FRAME: LOW_COST_PURCHASE.",
      "frame_name": "LOW_COST_PURCHASE"
    }},
    {{
      "id": "p2",
      "original_phrase": "Jacket fell apart the next day",
      "rationale": "ROOT: the event is about failure because the item breaks quickly; so a good root is FAILURE. DETAIL: in this story, it applies to durability because the breakdown concerns build quality over time; so a good detail name is DURABILITY. FRAME: DURABILITY_FAILURE.",
      "frame_name": "DURABILITY_FAILURE"
    }},
    {{
      "id": "p3",
      "original_phrase": "I concluded more expensive clothes last longer",
      "rationale": "ROOT: the event is about adoption because the narrator adopts a buying principle; so a good root is ADOPTION. DETAIL: in this story, it applies to purchasing strategy because the rule governs future purchases; so a good detail name is PURCHASING_STRATEGY. FRAME: PURCHASING_STRATEGY_ADOPTION.",
      "frame_name": "PURCHASING_STRATEGY_ADOPTION"
    }}
  ]
}}
</JSON>

### Your Turn

#### Input Format
Story:
{story}

Phrases:
{phrases}


#### Remember:
- Choose **ROOT** first (one word, noun-like), then the minimal **DETAIL** (1–2 tokens).
- Keep frames ≤ **3 tokens**, **UPPERCASE_WITH_UNDERSCORES**.
- Use explicit causal roots (**…_CAUSE**, **…_RESULT**) only when supported by the text.
- Avoid ultra-generic or metaphorical/meta frames; stay faithful to the story context.
- In the **rationale**, use the exact pattern:  
  “ROOT: the event is about … because … ; so a good root is ROOT_NAME.  
  DETAIL: in this story, it applies to … because … ; so a good detail name is DETAIL_NAME.  
  FRAME: DETAIL_NAME_ROOT_NAME.”
- **Consistency check:** the suffix of **frame_name** must equal the ROOT you declared in the rationale.


Output: A single JSON object exactly matching the schema described in Output Explanation.

Return ONLY one JSON object. Do not output anything before or after it.
Wrap the array inside <JSON> ... </JSON> tags.
Provide output in the following format:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": ...,
      "rationale": ...,
      "frame_name": ...
    }},
    ...
  ]
}}


"""

#########################################



prompt_abstraction_extraction12 = """
### Role Assignment
You are a narrative-role extraction assistant. 
Your job is to read a short **Story**, a set of **Phrases**, and their **Previous_Frames** (concise semantic labels), then assign exactly one **Role** to each phrase from a fixed inventory. 
Your assignments should capture **why** each event is in the story (its function in the narrative arc), not just what the event is.

### Task Definition
You will assign one **Role** to each phrase, using the following inventory and detailed definitions. 
Use the **Story** context and the provided **Previous_Frames** as helpful signals (but the phrase text and story context take precedence if there is a conflict). 
Roles must be **UPPERCASE_WITH_UNDERSCORES** and chosen from this set:

- **BACKGROUND** — Setup or contextual information that is not essential to the main causal arc. It may introduce characters, setting, or prior conditions. If the event could be removed with minimal impact on the core problem–solution–outcome chain, classify it as BACKGROUND.
- **FOCAL_SITUATION** — The main situation or issue the story is about. This can be a problem (e.g., an undesirable state) or a neutral focal event (e.g., a purchase, a move, a discovery) that anchors the narrative. It typically establishes “what this episode is about.” Prefer FOCAL_SITUATION over RESULT when the text is introducing the central episode rather than reporting an outcome.
- **DIAGNOSIS** — Analytical steps that characterize or explain the focal situation: investigating, inferring causes, identifying what specifically is wrong, or clarifying why the situation is as it is. Use DIAGNOSIS when the phrase advances understanding (e.g., recognizing the cause), even if no action has yet been taken. Do not confuse with RESULT; DIAGNOSIS explains the state/problem rather than reporting a post-action outcome.
- **INTERVENTION** — Actions taken in response to the focal situation to change, improve, or address it. This includes avoiding something, adopting a new behavior, replacing, repairing, or otherwise executing a strategy. If the phrase is an intentional step to alter the situation, assign INTERVENTION (even if the effect is not yet stated).
- **RESULT** — Outcomes that occur after interventions (or after time passes in a way the story frames as a consequence). RESULT reports what happened as a consequence phase, not the process of understanding. Avoid labeling DIAGNOSIS as RESULT: only use RESULT when the narrative frames it as what happened following the intervention(s).
- **RESULT_ATTRIBUTION** — An explicit statement that explains **why** the result occurred, linking the outcome to a cause or prior action. Use this when the text provides a reason/explanation for the outcome (e.g., “since…,” “because…,” “as a result of…”). Do not use RESULT_ATTRIBUTION if the text merely states an outcome without an explicit reason.
- **LESSON** — A generalized rule, policy, or principle derived from the episode. This is not a specific action or result, but a takeaway that applies beyond the immediate story. Assign LESSON only when the text explicitly generalizes.

General requirements:
- Assign exactly **one** Role per phrase from the set above.
- Roles are **functions** in the narrative, not event types; multiple different frames may share the same Role.
- Use **Previous_Frames** as a hint to disambiguate (e.g., BEHAVIOR_ADOPTION suggests INTERVENTION), but always confirm against the **Story** context.
- Be consistent across similar events: several phrases may map to the same Role if they serve the same function.

### Output Format
Return a single JSON object wrapped in **<JSON> ... </JSON>** tags with a top-level **results** array. For each phrase, include:
- **id**: the phrase identifier from input.
- **original_phrase**: the phrase text from input.
- **previous_frame**: the provided semantic frame label.
- **rationale**: a brief (1–2 sentences) explanation of why the selected **role_name** fits, referencing the story context and previous_frame when helpful.
- **role_name**: one of {{BACKGROUND, FOCAL_SITUATION, DIAGNOSIS, INTERVENTION, RESULT, RESULT_ATTRIBUTION, LESSON}} in **UPPERCASE_WITH_UNDERSCORES**.

### Examples

**Example 1**

Story:
“David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.”

Phrases and previous frames
[
  {{ "id":"p1","phrase":"David noticed weight gain", "previous_frame":"PROBLEM_RECOGNITION" }},
  {{ "id":"p2","phrase":"David examined his habits for a reason", "previous_frame":"SELF_ASSESSMENT" }},
  {{ "id":"p3","phrase":"David Realized he ate too much fast food", "previous_frame":"CAUSE_IDENTIFICATION" }},
  {{ "id":"p4","phrase":"David Stopped going to burger places", "previous_frame":"BEHAVIOR_AVOIDANCE" }},
  {{ "id":"p5","phrase":"David Started a vegetarian diet", "previous_frame":"BEHAVIOR_ADOPTION" }},
  {{ "id":"p6","phrase":"David Felt better after a few weeks", "previous_frame":"WELLBEING_IMPROVEMENT" }},
  {{ "id":"p7","phrase":"David had stopped eating unhealthy foods", "previous_frame":"IMPROVEMENT_CAUSE" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "David noticed weight gain",
      "previous_frame": "PROBLEM_RECOGNITION",
      "rationale": "This introduces what the episode is about—recognizing a weight-related issue—so it functions as the narrative anchor.",
      "role_name": "FOCAL_SITUATION"
    }},
    {{
      "id": "p2",
      "original_phrase": "David examined his habits for a reason",
      "previous_frame": "SELF_ASSESSMENT",
      "rationale": "He analyzes the situation to find an explanation, which advances understanding rather than reporting an outcome.",
      "role_name": "DIAGNOSIS"
    }},
    {{
      "id": "p3",
      "original_phrase": "David Realized he ate too much fast food",
      "previous_frame": "CAUSE_IDENTIFICATION",
      "rationale": "He identifies the cause of the issue, a core explanatory step in the narrative.",
      "role_name": "DIAGNOSIS"
    }},
    {{
      "id": "p4",
      "original_phrase": "David Stopped going to burger places",
      "previous_frame": "BEHAVIOR_AVOIDANCE",
      "rationale": "A deliberate action taken to address the problem by removing a harmful behavior.",
      "role_name": "INTERVENTION"
    }},
    {{
      "id": "p5",
      "original_phrase": "David Started a vegetarian diet",
      "previous_frame": "BEHAVIOR_ADOPTION",
      "rationale": "Another intentional change aimed at solving the problem by adopting a new behavior.",
      "role_name": "INTERVENTION"
    }},
    {{
      "id": "p6",
      "original_phrase": "David Felt better after a few weeks",
      "previous_frame": "WELLBEING_IMPROVEMENT",
      "rationale": "This reports the outcome phase following the interventions.",
      "role_name": "RESULT"
    }},
    {{
      "id": "p7",
      "original_phrase": "David had stopped eating unhealthy foods",
      "previous_frame": "IMPROVEMENT_CAUSE",
      "rationale": "It explicitly attributes the improvement to a cause, using a because/since relation.",
      "role_name": "RESULT_ATTRIBUTION"
    }}
  ]
}}
</JSON>

**Example 2**

Story:
“Eric and his wife had a daughter named Meg. Eric and Meg were very sad when Eric's wife passed away. Eric met a woman and married her 5 years after his wife died. Meg is finally happy with her new stepmother as she is very kind to her.”

Phrases and previous frames
[
  {{ "id":"p1","phrase":"Eric and his wife had Meg", "previous_frame":"FAMILY_ADDITION" }},
  {{ "id":"p2","phrase":"Erics wife passed away", "previous_frame":"DEATH_EVENT" }},
  {{ "id":"p3","phrase":"Eric and Meg were very sad", "previous_frame":"EMOTIONAL_DISTRESS" }},
  {{ "id":"p4","phrase":"Eric met a woman", "previous_frame":"SOCIAL_MEETING" }},
  {{ "id":"p5","phrase":"Eric married the woman five years later ", "previous_frame":"MARITAL_UNION" }},
  {{ "id":"p6","phrase":"Meg was happy with her stepmother", "previous_frame":"RELATIONSHIP_SATISFACTION" }},
  {{ "id":"p7","phrase":"Megs stepmother is kind to her", "previous_frame":"SATISFACTION_CAUSE" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Eric and his wife had Meg",
      "previous_frame": "FAMILY_ADDITION",
      "rationale": "This provides family context that frames later events but is not essential to the causal chain.",
      "role_name": "BACKGROUND"
    }},
    {{
      "id": "p2",
      "original_phrase": "Erics wife passed away",
      "previous_frame": "DEATH_EVENT",
      "rationale": "The death sets the central situation the story revolves around.",
      "role_name": "FOCAL_SITUATION"
    }},
    {{
      "id": "p3",
      "original_phrase": "Eric and Meg were very sad",
      "previous_frame": "EMOTIONAL_DISTRESS",
      "rationale": "Their grief characterizes the central situation and its immediate impact, continuing the focus of the episode.",
      "role_name": "FOCAL_SITUATION"
    }},
    {{
      "id": "p4",
      "original_phrase": "Eric met a woman",
      "previous_frame": "SOCIAL_MEETING",
      "rationale": "A purposeful step toward changing the situation.",
      "role_name": "INTERVENTION"
    }},
    {{
      "id": "p5",
      "original_phrase": "Eric married the woman five years later ",
      "previous_frame": "MARITAL_UNION",
      "rationale": "A decisive action that further alters the life context initiated by the loss.",
      "role_name": "INTERVENTION"
    }},
    {{
      "id": "p6",
      "original_phrase": "Meg was happy with her stepmother",
      "previous_frame": "RELATIONSHIP_SATISFACTION",
      "rationale": "This reports a positive outcome phase following the new family structure.",
      "role_name": "RESULT"
    }},
    {{
      "id": "p7",
      "original_phrase": "Megs stepmother is kind to her",
      "previous_frame": "SATISFACTION_CAUSE",
      "rationale": "It states the reason for Meg’s satisfaction explicitly.",
      "role_name": "RESULT_ATTRIBUTION"
    }}
  ]
}}
</JSON>

**Example 3**

Story:
“There was a bug on the wall by the bed. Kate grabbed a shoe and killed it.”

Phrases and previous frames
[
  {{ "id":"p1","phrase":"Bug was on the wall by the bed", "previous_frame":"UNWANTED_PRESENCE" }},
  {{ "id":"p2","phrase":"Kate grabbed a shoe", "previous_frame":"RESOURCE_ACQUISITION" }},
  {{ "id":"p3","phrase":"Kate killed the bug", "previous_frame":"PROBLEM_RESOLUTION" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Bug was on the wall by the bed",
      "previous_frame": "UNWANTED_PRESENCE",
      "rationale": "This sets what the episode is about—the presence of a pest.",
      "role_name": "FOCAL_SITUATION"
    }},
    {{
      "id": "p2",
      "original_phrase": "Kate grabbed a shoe",
      "previous_frame": "RESOURCE_ACQUISITION",
      "rationale": "An intentional step taken to address the situation.",
      "role_name": "INTERVENTION"
    }},
    {{
      "id": "p3",
      "original_phrase": "Kate killed the bug",
      "previous_frame": "PROBLEM_RESOLUTION",
      "rationale": "Reports the outcome/consequence phase of the intervention.",
      "role_name": "RESULT"
    }}
  ]
}}
</JSON>

**Example 4**

Story:
“I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

Phrases and previous frames
[
  {{ "id":"p1","phrase":"I bought a cheap jacket", "previous_frame":"PURCHASE_EVENT" }},
  {{ "id":"p2","phrase":"Jacket fell apart the next day", "previous_frame":"PRODUCT_FAILURE" }},
  {{ "id":"p3","phrase":"I concluded more expensive clothes last longer", "previous_frame":"STRATEGY_ADOPTION" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "I bought a cheap jacket",
      "previous_frame": "PURCHASE_EVENT",
      "rationale": "Introduces what this episode is about—the purchase—anchoring the narrative.",
      "role_name": "FOCAL_SITUATION"
    }},
    {{
      "id": "p2",
      "original_phrase": "Jacket fell apart the next day",
      "previous_frame": "PRODUCT_FAILURE",
      "rationale": "Identifies what is wrong with the focal item, characterizing the issue rather than reporting a post-action outcome.",
      "role_name": "DIAGNOSIS"
    }},
    {{
      "id": "p3",
      "original_phrase": "I concluded more expensive clothes last longer",
      "previous_frame": "STRATEGY_ADOPTION",
      "rationale": "States a generalized takeaway derived from the episode.",
      "role_name": "LESSON"
    }}
  ]
}}
</JSON>

### Your Turn

#### Input Format
Story:
{story}

Phrases and previous frames
{phrases}



#### Remember:
- Assign exactly **one** Role per phrase from the fixed inventory.
- Roles capture **function** in the narrative arc, not event type; multiple phrases may share the same Role.
- Use **Previous_Frames** as hints but rely on the **Story** context and phrase meaning.
- Prefer **FOCAL_SITUATION** for episode anchors; use **DIAGNOSIS** for understanding/explanation steps; reserve **RESULT** for the consequence phase after interventions.
- Use **RESULT_ATTRIBUTION** only when the text explicitly explains **why** the result occurred.
- Keep rationales brief (1–2 sentences) and specific to the story context.
- **role_name** must be one of: BACKGROUND, FOCAL_SITUATION, DIAGNOSIS, INTERVENTION, RESULT, RESULT_ATTRIBUTION, LESSON (UPPERCASE_WITH_UNDERSCORES).


Output: A single JSON object exactly matching the schema described in Output Explanation.

Return ONLY one JSON object. Do not output anything before or after it.
Wrap the array inside <JSON> ... </JSON> tags.
Provide output in the following format:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": ...,
      "previous_frame": ...,
      "rationale": ...,
      "role_name": ...
    }},
    ...
  ]
}}

"""


prompt_abstraction_extraction13 = """
### Role Assignment
You are a frame-abstraction assistant. 
Given a short **Story** and a list of **Phrases**, produce three abstraction levels for each event phrase using the schema **[DETAIL]_[ROOT]** at two levels and a single-word **ROOT** at the highest level.

### Task Definition
For each event phrase, extract and construct:

**Level 1 (specific, story-aware)**
- **root_l1**: a one-word, noun-like head that captures the event type.
- **detail_l1**: a minimal domain descriptor (1–2 tokens, UPPERCASE_WITH_UNDERSCORES) clarifying what the root applies to.
- **frame_l1**: `[DETAIL_L1]_[ROOT_L1]`.

**Level 2 (generalized detail, same root)**
- **root_l2**: MUST equal **root_l1** (do not change the root at this level).
- **detail_l2**: a broader category for **detail_l1**, based on the context of the story.
- **frame_l2**: `[DETAIL_L2]_[ROOT_L2]`.

**Level 3 (root-only head)**
- **root_l3**: a more general head (single token) derived from **root_l2** and the **frame_l2** from the story context. It MUST be **different from root_l2** (i.e., **root_l3 != root_l2**). 
- **frame_l3**: exactly equal to **root_l3**.

**Formatting & Constraints**
- All labels are **UPPERCASE_WITH_UNDERSCORES**.
- Token limits: **detail_l1** ≤ 2 tokens; each **root** is exactly 1 token.
- `frame_l1 = detail_l1 + '_' + root_l1`
- `root_l2 = root_l1`
- `frame_l2 = detail_l2 + '_' + root_l2`
- `root_l3 != root_l2`
- `frame_l3 = root_l3`


### Output Format
Return a single JSON object wrapped in **<JSON> ... </JSON>** tags with a top-level **results** array. For each phrase, include:
- **id**: the phrase identifier from input.
- **original_phrase**: the phrase text from input.
- **root_l1**: the first level root.
- **detail_l1**: the first level detail.
- **frame_l1**: the first level frame. detail_l1 + '_' + root_l1`
- **root_l2**: the second level root, same as the first level.
- **detail_l2**: the second level detail, a generelaziation over the detail_l1.
- **frame_l2**: the second level frame. detail_l2 + '_' + root_l2
- **root_l3**: a generalization over the root_l2, with the help of the story context.
- **frame_l3**: the third level frame. root_l2


### Examples

**Example 1**

Story:
“David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.”

Phrases:
[
  {{ "id":"p1","text":"David noticed weight gain" }},
  {{ "id":"p2","text":"David examined his habits for a reason" }},
  {{ "id":"p3","text":"David Realized he ate too much fast food" }},
  {{ "id":"p4","text":"David Stopped going to burger places" }},
  {{ "id":"p5","text":"David Started a vegetarian diet" }},
  {{ "id":"p6","text":"David Felt better after a few weeks" }},
  {{ "id":"p7","text":"David had stopped eating unhealthy foods" }}
]

Output:
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "David noticed weight gain",
      "root_l1": "RECOGNITION",
      "detail_l1": "WEIGHT_GAIN",
      "frame_l1": "WEIGHT_GAIN_RECOGNITION",
      "root_l2": "RECOGNITION",
      "detail_l2": "PROBLEM",
      "frame_l2": "PROBLEM_RECOGNITION",
      "root_l3": "AWARENESS",
      "frame_l3": "AWARENESS"
    }},
    {{
      "id": "p2",
      "original_phrase": "David examined his habits for a reason",
      "root_l1": "EXAMINE",
      "detail_l1": "HABIT",
      "frame_l1": "HABIT_EXAMINE",
      "root_l2": "EXAMINE",
      "detail_l2": "BEHAVIOR",
      "frame_l2": "BEHAVIOR_EXAMINE",
      "root_l3": "SCRUTINY",
      "frame_l3": "SCRUTINY"
    }},
    {{
      "id": "p3",
      "original_phrase": "David Realized he ate too much fast food",
      "root_l1": "REALIZATION",
      "detail_l1": "HARMFUL_DIETARY",
      "frame_l1": "HARMFUL_DIETARY_REALIZATION",
      "root_l2": "REALIZATION",
      "detail_l2": "MISTAKE",
      "frame_l2": "MISTAKE_REALIZATION",
      "root_l3": "IDENTIFICATION",
      "frame_l3": "IDENTIFICATION"
    }},
    {{
      "id": "p4",
      "original_phrase": "David Stopped going to burger places",
      "root_l1": "AVOIDANCE",
      "detail_l1": "RESTAURANT",
      "frame_l1": "RESTAURANT_AVOIDANCE",
      "root_l2": "AVOIDANCE",
      "detail_l2": "HABIT",
      "frame_l2": "HABIT_AVOIDANCE",
      "root_l3": "CHANGE",
      "frame_l3": "CHANGE"
    }},
    {{
      "id": "p5",
      "original_phrase": "David Started a vegetarian diet",
      "root_l1": "ADOPTION",
      "detail_l1": "VEGETARIAN_DIET",
      "frame_l1": "VEGETARIAN_DIET_ADOPTION",
      "root_l2": "ADOPTION",
      "detail_l2": "BEHAVIOR",
      "frame_l2": "BEHAVIOR_ADOPTION",
      "root_l3": "CHANGE",
      "frame_l3": "CHANGE"
    }},
    {{
      "id": "p6",
      "original_phrase": "David Felt better after a few weeks",
      "root_l1": "IMPROVEMENT",
      "detail_l1": "HEALTH",
      "frame_l1": "HEALTH_IMPROVEMENT",
      "root_l2": "IMPROVEMENT",
      "detail_l2": "LIFE",
      "frame_l2": "LIFE_IMPROVEMENT",
      "root_l3": "ENHANCEMENT",
      "frame_l3": "ENHANCEMENT"
    }},
    {{
      "id": "p7",
      "original_phrase": "David had stopped eating unhealthy foods",
      "root_l1": "CAUSE",
      "detail_l1": "HEALTH_IMPROVEMENT",
      "frame_l1": "HEALTH_IMPROVEMENT_CAUSE",
      "root_l2": "CAUSE",
      "detail_l2": "IMPROVEMENT",
      "frame_l2": "IMPROVEMENT_CAUSE",
      "root_l3": "REASON",
      "frame_l3": "REASON"
    }}
  ]
}}

**Example 2**

Story:
“Eric and his wife had a daughter named Meg. Eric and Meg were very sad when Eric's wife passed away. Eric met a woman and married her 5 years after his wife died. Meg is finally happy with her new stepmother as she is very kind to her.”

Phrases:
[
  {{ "id":"p1","text":"Eric and his wife had Meg" }},
  {{ "id":"p2","text":"Erics wife passed away" }},
  {{ "id":"p3","text":"Eric and Meg were very sad" }},
  {{ "id":"p4","text":"Eric met a woman" }},
  {{ "id":"p5","text":"Eric married the woman five years later " }},
  {{ "id":"p6","text":"Meg was happy with her stepmother" }},
  {{ "id":"p7","text":"Megs stepmother is kind to her" }}
]

Output:
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Eric and his wife had Meg",
      "root_l1": "BIRTH",
      "detail_l1": "NEW_CHILD",
      "frame_l1": "NEW_CHILD_BIRTH",
      "root_l2": "BIRTH",
      "detail_l2": "RELATIONSHIP",
      "frame_l2": "RELATIONSHIP_BIRTH",
      "root_l3": "FAMILY",
      "frame_l3": "FAMILY"
    }},
    {{
      "id": "p2",
      "original_phrase": "Erics wife passed away",
      "root_l1": "DEATH",
      "detail_l1": "TRAGIC_SPOUSE",
      "frame_l1": "TRAGIC_SPOUSE_DEATH",
      "root_l2": "DEATH",
      "detail_l2": "BELOVED",
      "frame_l2": "BELOVED_DEATH",
      "root_l3": "LOSS",
      "frame_l3": "LOSS"
    }},
    {{
      "id": "p3",
      "original_phrase": "Eric and Meg were very sad",
      "root_l1": "GRIEF",
      "detail_l1": "DEATH",
      "frame_l1": "DEATH_GRIEF",
      "root_l2": "GRIEF",
      "detail_l2": "LOSS",
      "frame_l2": "LOSS_GRIEF",
      "root_l3": "SUFFERING",
      "frame_l3": "SUFFERING"
    }},
    {{
      "id": "p4",
      "original_phrase": "Eric met a woman",
      "root_l1": "MEETING",
      "detail_l1": "PROSPECTIVE_PARTNER",
      "frame_l1": "PROSPECTIVE_PARTNER_MEETING",
      "root_l2": "MEETING",
      "detail_l2": "NEW_SITUATION",
      "frame_l2": "NEW_SITUATION_MEETING",
      "root_l3": "ENCOUNTER",
      "frame_l3": "ENCOUNTER"
    }},
    {{
      "id": "p5",
      "original_phrase": "Eric married the woman five years later ",
      "root_l1": "UNION",
      "detail_l1": "REMARRIAGE",
      "frame_l1": "REMARRIAGE_UNION",
      "root_l2": "UNION",
      "detail_l2": "RELATIONSHIP",
      "frame_l2": "RELATIONSHIP_UNION",
      "root_l3": "MARRIAGE",
      "frame_l3": "MARRIAGE"
    }},
    {{
      "id": "p6",
      "original_phrase": "Meg was happy with her stepmother",
      "root_l1": "SATISFACTION",
      "detail_l1": "STEPPARENT_RELATIONSHIP",
      "frame_l1": "STEPPARENT_RELATIONSHIP_SATISFACTION",
      "root_l2": "SATISFACTION",
      "detail_l2": "RELATIONSHIP",
      "frame_l2": "RELATIONSHIP_SATISFACTION",
      "root_l3": "HAPPINESS",
      "frame_l3": "HAPPINESS"
    }},
    {{
      "id": "p7",
      "original_phrase": "Megs stepmother is kind to her",
      "root_l1": "CAUSE",
      "detail_l1": "RELATIONSHIP_SATISFACTION",
      "frame_l1": "RELATIONSHIP_SATISFACTION_CAUSE",
      "root_l2": "CAUSE",
      "detail_l2": "HAPPINESS",
      "frame_l2": "HAPPINESS_CAUSE",
      "root_l3": "REASON",
      "frame_l3": "REASON"
    }}
  ]
}}

**Example 3**

Story:
“There was a bug on the wall by the bed. Kate grabbed a shoe and killed it.”

Phrases:
[
  {{ "id":"p1","text":"Bug was on the wall by the bed" }},
  {{ "id":"p2","text":"Kate grabbed a shoe" }},
  {{ "id":"p3","text":"Kate killed the bug" }}
]

Output:
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "Bug was on the wall by the bed",
      "root_l1": "PRESENCE",
      "detail_l1": "PEST",
      "frame_l1": "PEST_PRESENCE",
      "root_l2": "PRESENCE",
      "detail_l2": "NUISANCE",
      "frame_l2": "NUISANCE_PRESENCE",
      "root_l3": "EXISTENCE",
      "frame_l3": "EXISTENCE"
    }},
    {{
      "id": "p2",
      "original_phrase": "Kate grabbed a shoe",
      "root_l1": "ACQUISITION",
      "detail_l1": "TOOL",
      "frame_l1": "TOOL_ACQUISITION",
      "root_l2": "ACQUISITION",
      "detail_l2": "RESOURCE",
      "frame_l2": "RESOURCE_ACQUISITION",
      "root_l3": "PROCUREMENT",
      "frame_l3": "PROCUREMENT"
    }},
    {{
      "id": "p3",
      "original_phrase": "Kate killed the bug",
      "root_l1": "ELIMINATION",
      "detail_l1": "PEST",
      "frame_l1": "PEST_ELIMINATION",
      "root_l2": "ELIMINATION",
      "detail_l2": "NUISANCE",
      "frame_l2": "NUISANCE_ELIMINATION",
      "root_l3": "MITIGATION",
      "frame_l3": "MITIGATION"
    }}
  ]
}}

**Example 4**

Story:
“I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

Phrases:
[
  {{ "id":"p1","text":"I bought a cheap jacket" }},
  {{ "id":"p2","text":"Jacket fell apart the next day" }},
  {{ "id":"p3","text":"I concluded more expensive clothes last longer" }}
]

Output:
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "I bought a cheap jacket",
      "root_l1": "PURCHASE",
      "detail_l1": "LOW_COST",
      "frame_l1": "LOW_COST_PURCHASE",
      "root_l2": "PURCHASE",
      "detail_l2": "CHEAP",
      "frame_l2": "CHEAP_PURCHASE",
      "root_l3": "ACQUISITION",
      "frame_l3": "ACQUISITION"
    }},
    {{
      "id": "p2",
      "original_phrase": "Jacket fell apart the next day",
      "root_l1": "FAILURE",
      "detail_l1": "PURCHASE",
      "frame_l1": "PURCHASE_FAILURE",
      "root_l2": "FAILURE",
      "detail_l2": "DURABILITY",
      "frame_l2": "DURABILITY_FAILURE",
      "root_l3": "MALFUNCTION",
      "frame_l3": "MALFUNCTION"
    }},
    {{
      "id": "p3",
      "original_phrase": "I concluded more expensive clothes last longer",
      "root_l1": "ADOPTION",
      "detail_l1": "PURCHASING_STRATEGY",
      "frame_l1": "PURCHASING_STRATEGY_ADOPTION",
      "root_l2": "ADOPTION",
      "detail_l2": "METHOD",
      "frame_l2": "METHOD_ADOPTION",
      "root_l3": "CHANGE",
      "frame_l3": "CHANGE"
    }}
  ]
}}

### Your Turn

#### Input
Story:
{story}

Phrases:
{phrases}


#### Remember
- Choose **root_l1** first based on the main event type in the phrase, then **detail_l1** to elaborate the root, then build **frame_l1**.
- Generalize **detail_l1 → detail_l2**. Do this based on the context of the story and the role of the root. 
- Normalize to a broader **root_l3** so that **root_l3 != root_l2**; set **frame_l3 = root_l3**.
- Obey all five construction checks and output only the JSON object.

#### Output
Return exactly one JSON object with this shape (and nothing else):
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "...",
      "root_l1": "...",
      "detail_l1": "...",
      "frame_l1": "...",
      "root_l2": "...",
      "detail_l2": "...",
      "frame_l2": "...",
      "root_l3": "...",
      "frame_l3": "..."
    }},
    ...
  ]
}}

"""

prompt_abstraction_extraction14 = """

### Role Assignment
You are a frame-abstraction assistant. 
Given a short **Story** and a list of **Phrases**, produce three abstraction levels for each phrase using the schema **[DETAIL]_[ROOT]** at two levels and a single-word **ROOT** at the highest level.

### Task Definition

For each event phrase, extract and construct:

**Level 1 (specific, story-aware)**
- **root_l1**: a one-word, noun-like head that captures the event type.
- **detail_l1**: a minimal domain descriptor (1–2 tokens, UPPERCASE_WITH_UNDERSCORES) clarifying what the root applies to.
- **frame_l1**: `[DETAIL_L1]_[ROOT_L1]`.

**Level 2 (generalized detail, same root)**
- **root_l2**: MUST equal **root_l1** (do not change the root at this level).
- **detail_l2**: a broader category for **detail_l1**, based on the context of the story.
- **frame_l2**: `[DETAIL_L2]_[ROOT_L2]`.

**Level 3 (root-only head)**
- **root_l3**: a more general head (single token) derived from **root_l2** and the **detail_l2** from the story context. It MUST be **different from root_l2** (i.e., **root_l3 != root_l2**). 
- **frame_l3**: exactly equal to **root_l3**.


#### How to get `root_l1` (event head)
- **Definition:** the **minimal semantic function** of the phrase’s **main predicate** in context—what kind of situation the phrase is doing in the story.
- **Form:** one word, noun-like, **UPPERCASE**.
- **Method:** identify the main predicate; abstract its function or type.

#### How to get `detail_l1` (explanation, ≤2 tokens)
- **Definition:** the **minimal explanation** to which the root applies in this story. It must explain root_l1 based on the context of the story.
- **Allowed forms (UPPERCASE_WITH_UNDERSCORES):** **NOUN**, **NOUN_NOUN**, **ADJ**, **ADJ_NOUN**.
- **Method:** keeps the total ≤2 tokens.

#### How to generalize `detail_l1` into `detail_l2` (role/type)
- **Definition:** a one-token generalization of `detail_l1` naming the anchor’s **role/type** in the situation.
- **Role/Type (what to capture):** the anchor’s **function relative to the phrase’s root** (what it does in this event), not its topic.
- **Method:** isolate the anchor’s head; determine its function in the event.

#### How to get `root_l3` from `root_l2` and `detail_l2`
- **Definition:** a single-token, domain-neutral **super-head** (most general functional class of the event); **must differ from `root_l2`**.
- **Method:** use `root_l2` to identify the event’s functional family; when ambiguous, use `detail_l2` (role/type) to disambiguate.
- **Normalization:** replace `root_l2` with the family’s canonical super-head (drop domain/topic and phase modifiers).
- **Constraints:** one token, **UPPERCASE**; **root_l3 != root_l2**; stable mapping for the same family across the dataset.
- **Orthogonality:** `detail_l2` carries role/type; `root_l3` carries broad function—do not mix them.

### Output Format
Return exactly **one** JSON object (no extra text) with a top-level **results** array. Each item must include:
- **id**, **original_phrase**
- **root_l1**, **detail_l1**, **frame_l1** (=`detail_l1 + '_' + root_l1`)
- **root_l2** (must equal **root_l1**), **detail_l2**, **frame_l2** (=`detail_l2 + '_' + root_l2`)
- **root_l3** (must differ from **root_l2**), **frame_l3** (exactly equal to **root_l3**)

**Global constraints (must hold):**
1) `frame_l1 == detail_l1 + '_' + root_l1`
2) `root_l2 == root_l1`
3) `frame_l2 == detail_l2 + '_' + root_l2`
4) `root_l3 != root_l2`
5) `frame_l3 == root_l3`
6) All labels UPPERCASE_WITH_UNDERSCORES; `detail_l1` ≤ 2 tokens; each root is exactly 1 token.

### Examples

**Example 1**

Story:
“David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.”

Phrases:
[
  {{ "id":"p1","text":"David noticed weight gain" }},
  {{ "id":"p2","text":"David examined his habits for a reason" }},
  {{ "id":"p3","text":"David Realized he ate too much fast food" }},
  {{ "id":"p4","text":"David Stopped going to burger places" }},
  {{ "id":"p5","text":"David Started a vegetarian diet" }},
  {{ "id":"p6","text":"David Felt better after a few weeks" }},
  {{ "id":"p7","text":"David had stopped eating unhealthy foods" }}
]

Output:
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "David noticed weight gain",
      "root_l1": "RECOGNITION",
      "detail_l1": "WEIGHT_GAIN",
      "frame_l1": "WEIGHT_GAIN_RECOGNITION",
      "root_l2": "RECOGNITION",
      "detail_l2": "PROBLEM",
      "frame_l2": "PROBLEM_RECOGNITION",
      "root_l3": "AWARENESS",
      "frame_l3": "AWARENESS"
    }},
    {{
      "id": "p2",
      "original_phrase": "David examined his habits for a reason",
      "root_l1": "EXAMINE",
      "detail_l1": "HABIT",
      "frame_l1": "HABIT_EXAMINE",
      "root_l2": "EXAMINE",
      "detail_l2": "BEHAVIOR",
      "frame_l2": "BEHAVIOR_EXAMINE",
      "root_l3": "SCRUTINY",
      "frame_l3": "SCRUTINY"
    }},
    {{
      "id": "p3",
      "original_phrase": "David Realized he ate too much fast food",
      "root_l1": "REALIZATION",
      "detail_l1": "HARMFUL_DIETARY",
      "frame_l1": "HARMFUL_DIETARY_REALIZATION",
      "root_l2": "REALIZATION",
      "detail_l2": "MISTAKE",
      "frame_l2": "MISTAKE_REALIZATION",
      "root_l3": "IDENTIFICATION",
      "frame_l3": "IDENTIFICATION"
    }},
    {{
      "id": "p4",
      "original_phrase": "David Stopped going to burger places",
      "root_l1": "AVOIDANCE",
      "detail_l1": "RESTAURANT",
      "frame_l1": "RESTAURANT_AVOIDANCE",
      "root_l2": "AVOIDANCE",
      "detail_l2": "HABIT",
      "frame_l2": "HABIT_AVOIDANCE",
      "root_l3": "CHANGE",
      "frame_l3": "CHANGE"
    }},
    {{
      "id": "p5",
      "original_phrase": "David Started a vegetarian diet",
      "root_l1": "ADOPTION",
      "detail_l1": "VEGETARIAN_DIET",
      "frame_l1": "VEGETARIAN_DIET_ADOPTION",
      "root_l2": "ADOPTION",
      "detail_l2": "BEHAVIOR",
      "frame_l2": "BEHAVIOR_ADOPTION",
      "root_l3": "CHANGE",
      "frame_l3": "CHANGE"
    }},
    {{
      "id": "p6",
      "original_phrase": "David Felt better after a few weeks",
      "root_l1": "IMPROVEMENT",
      "detail_l1": "HEALTH",
      "frame_l1": "HEALTH_IMPROVEMENT",
      "root_l2": "IMPROVEMENT",
      "detail_l2": "LIFE",
      "frame_l2": "LIFE_IMPROVEMENT",
      "root_l3": "ENHANCEMENT",
      "frame_l3": "ENHANCEMENT"
    }},
    {{
      "id": "p7",
      "original_phrase": "David had stopped eating unhealthy foods",
      "root_l1": "CAUSE",
      "detail_l1": "HEALTH_IMPROVEMENT",
      "frame_l1": "HEALTH_IMPROVEMENT_CAUSE",
      "root_l2": "CAUSE",
      "detail_l2": "IMPROVEMENT",
      "frame_l2": "IMPROVEMENT_CAUSE",
      "root_l3": "REASON",
      "frame_l3": "REASON"
    }}
  ]
}}


**Example 2**

Story:
“I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

Phrases:
[
  {{ "id":"p1","text":"I bought a cheap jacket" }},
  {{ "id":"p2","text":"Jacket fell apart the next day" }},
  {{ "id":"p3","text":"I concluded more expensive clothes last longer" }}
]

Output:
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "I bought a cheap jacket",
      "root_l1": "PURCHASE",
      "detail_l1": "LOW_COST",
      "frame_l1": "LOW_COST_PURCHASE",
      "root_l2": "PURCHASE",
      "detail_l2": "CHEAP",
      "frame_l2": "CHEAP_PURCHASE",
      "root_l3": "ACQUISITION",
      "frame_l3": "ACQUISITION"
    }},
    {{
      "id": "p2",
      "original_phrase": "Jacket fell apart the next day",
      "root_l1": "FAILURE",
      "detail_l1": "PURCHASE",
      "frame_l1": "PURCHASE_FAILURE",
      "root_l2": "FAILURE",
      "detail_l2": "DURABILITY",
      "frame_l2": "DURABILITY_FAILURE",
      "root_l3": "MALFUNCTION",
      "frame_l3": "MALFUNCTION"
    }},
    {{
      "id": "p3",
      "original_phrase": "I concluded more expensive clothes last longer",
      "root_l1": "ADOPTION",
      "detail_l1": "PURCHASING_STRATEGY",
      "frame_l1": "PURCHASING_STRATEGY_ADOPTION",
      "root_l2": "ADOPTION",
      "detail_l2": "METHOD",
      "frame_l2": "METHOD_ADOPTION",
      "root_l3": "CHANGE",
      "frame_l3": "CHANGE"
    }}
  ]
}}

### Your Turn

#### Input
Story:
{story}

Phrases:
{phrases}

#### Remember
- Choose **root_l1** first, then **detail_l1**, then build **frame_l1**.
- Generalize **detail_l1 → detail_l2** using the the role/type of the root. keep **root_l2 = root_l1**.
- Normalize to a broader **root_l3** so that **root_l3 != root_l2**; set **frame_l3 = root_l3**.
- Obey all five construction checks and output only the JSON object.


#### Output
Return exactly one JSON object with this shape (and nothing else):
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "...",
      "root_l1": "...",
      "detail_l1": "...",
      "frame_l1": "...",
      "root_l2": "...",
      "detail_l2": "...",
      "frame_l2": "...",
      "root_l3": "...",
      "frame_l3": "..."
    }}
  ]
}}


"""

################################################

prompt_abstraction_extraction20 = """
### Role Assignment
You are a frame-extraction assistant. 
Your job is to read a short **Story** and a list of extracted **Phrases**, then assign exactly one concise semantic **Frame** to each phrase. 
Each **Frame** must follow the schema **[MODIFIER]_[ROOT]**, capturing the phrase’s core meaning in the context of the story.

### Task Definition
Use the following specification to construct each **Frame**:

**ROOT**
- **Purpose:** Name the core event/state/concept in **one noun-like word**.
- **How to extract the candidate word:**
  1) Identify the **semantic head** of the phrase — what happened or what state holds.
  2) Convert it to a **noun-like** form if needed (e.g., verb → nominalization) while preserving meaning.
- **Candidate evaluation (fixed pros/cons to consider):**
  - **pros:** with story signal; more general than the phrase
  - **cons:** without any story signal; too general
- **Not allowed (hard ban):**
  - Words that are **overly general and story-agnostic**: ACTION, EVENT, ACTIVITY, SITUATION, OCCURRENCE, THING, ITEM, OBJECT, PROCESS, INFORMATION, KNOWLEDGE, STUFF.  
  - *Why:* These carry no useful signal from the story and fail to convey meaning.

**MODIFIER**
- **Purpose:** Provide an **explanation** for the ROOT in **one word**.
- **How to choose it:**
  - **Domain or category option:** Choose a **domain-level or category-level** noun that clearly ties the ROOT to this story while avoiding single-instance items or names.  
  - **Quality option:** You may instead use a **single-word quality adjective** when the phrase focuses on **tempo, degree, polarity, or quality** rather than domain.  
  - **Focus choice:** Decide whether **domain** or **quality** is more relevant by identifying the main focus of the phrase.
  - **Non-redundancy:** The modifier must be **completely different from the ROOT** and add **new information** rather than restating or paraphrasing the ROOT.
- **Candidate evaluation (fixed pros/cons to consider):**
  - **pros:** anchors phrase focus; minimal but informative
  - **cons:** too generic or no signal; redundant with ROOT; overfitted
- **Not allowed (hard ban):**
  - Generic or meta modifiers that **do not add story signal**: GENERAL, QUALITY, THING, STUFF, EVENT, CONTEXT, TOPIC, AREA, DOMAIN, PEOPLE, PERSON, ENTITY, KNOWLEDGE, INFORMATION.  
  - Overly specific **proper names** or **single-instance items** when a domain or category (or a salient quality adjective) is available.  
  - *Why:* These either fail to anchor the ROOT to the story or overfit to a one-off instance.

**[MODIFIER]_[ROOT] frames — story-aware**
- **Form:** `[MODIFIER]_[ROOT]`
- **Goal:** precisely capture the event with a minimal but meaningful story signal.

**Rules**
- **Pick the ROOT first** (what the event is mainly about). Exactly **one word** (noun-like).
- **Then choose the MODIFIER** as the smallest informative **domain/category** (or role/attribute when appropriate) in **one word**.
- **Formatting:** both tokens **UPPERCASE**; exactly **two tokens** separated by a single underscore; total tokens = **2**.
- Avoid ultra-generic frames and avoid overfitted one-offs.
- **Hard consistency rule:** the ROOT you cite in the rationale must exactly match the suffix of **frame_name**.

### Rationale Style (Self-talk)
For each phrase, write a **short self-talk rationale** in **5–7 sentences** with **no commas and no semicolons**. Use only periods. Follow this flow and wording style:
- Start with: **This event is about ...**  
- Then: **So the possible roots are ...** where you list 2–4 single-word roots.
- Then: **Between these X is better because ...** where **X** is your chosen ROOT and your reason mentions story signal and being more general than the phrase.  
- Then: **To explain this root we can focus on ...** briefly naming the **domain or category** or **attribute or quality** that anchors the root without being overly specific.  
- Then: **So the candidate modifiers are ...** where you list 2–4 single-word modifiers including **at least one domain/category** and **at least one quality adjective** and **none may be a near synonym of the root**.  
- Then: **I think Y is better because ...** where **Y** is your chosen MODIFIER and your reason mentions adding new information beyond the root and being neither too specific nor too general. 
- End with: **So the final frame would be Y_X.**  
Keep everything UPPERCASE for the chosen ROOT and MODIFIER inside the sentences.

### Output Format
Return a single JSON object wrapped in **<JSON> ... </JSON>** tags with a top-level **results** array. For each phrase include:
- **id**: the phrase identifier from input.
- **original_phrase**: the exact phrase text from input.
- **rationale**: your self-talk text following the **Rationale Style (Self-talk)** section above.
- **frame_name**: the final frame name in **[MODIFIER]_[ROOT]** form (UPPERCASE, exactly 2 tokens).

### Examples

**Example 1**

Story:
“David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.”

Phrases:
[
  {{ "id":"p1","text":"David noticed weight gain" }},
  {{ "id":"p2","text":"David examined his habits for a reason" }},
  {{ "id":"p3","text":"David Realized he ate too much fast food" }},
  {{ "id":"p4","text":"David Stopped going to burger places" }},
  {{ "id":"p5","text":"David Started a vegetarian diet" }},
  {{ "id":"p6","text":"David Felt better after a few weeks" }},
  {{ "id":"p7","text":"David had stopped eating unhealthy foods" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "David noticed weight gain",
      "rationale": "This event is about recognizing a change in personal condition. So the possible roots are PERCEPTION AWARENESS and OBSERVATION. Between these AWARENESS is better because it keeps the story meaning and is more general than the phrase. To explain this root we can focus on the health domain. So the candidate modifiers are BODY HEALTH and WELLBEING. I think HEALTH is better because it anchors the domain and stays minimal. So the final frame would be HEALTH_AWARENESS.",
      "frame_name": "HEALTH_AWARENESS"
    }},
    {{
      "id": "p2",
      "original_phrase": "David examined his habits for a reason",
      "rationale": "This event is about looking into behavior to find an explanation. So the possible roots are REFLECTION ANALYSIS and INVESTIGATION. Between these ANALYSIS is better because it preserves the story signal and is more general than the phrase. To explain this root we can focus on the behavior category. So the candidate modifiers are HABIT ROUTINE and LIFESTYLE. I think HABIT is better because it anchors the category and is minimal. So the final frame would be HABIT_ANALYSIS.",
      "frame_name": "HABIT_ANALYSIS"
    }},
    {{
      "id": "p3",
      "original_phrase": "David Realized he ate too much fast food",
      "rationale": "This event is about gaining insight into eating behavior. So the possible roots are LEARNING REALIZATION and AWARENESS. Between these REALIZATION is better because it matches the insight and is more general than the verb form. To explain this root we can focus on the diet domain. So the candidate modifiers are DIET FOOD and NUTRITION. I think DIET is better because it anchors the domain and is minimal. So the final frame would be DIET_REALIZATION.",
      "frame_name": "DIET_REALIZATION"
    }},
    {{
      "id": "p4",
      "original_phrase": "David Stopped going to burger places",
      "rationale": "This event is about ending a repeated behavior. So the possible roots are REDUCTION AVOIDANCE and CESSATION. Between these CESSATION is better because it captures stopping fully and is more general than the surface wording. To explain this root we can focus on the behavior category. So the candidate modifiers are HABIT ROUTINE and DIET. I think HABIT is better because it anchors the category and is minimal. So the final frame would be HABIT_CESSATION.",
      "frame_name": "HABIT_CESSATION"
    }},
    {{
      "id": "p5",
      "original_phrase": "David Started a vegetarian diet",
      "rationale": "This event is about taking up a new ongoing practice. So the possible roots are INITIATION ADOPTION and START. Between these ADOPTION is better because it is noun like with story signal and more general than the verb. To explain this root we can focus on the diet domain. So the candidate modifiers are DIET NUTRITION and EATING. I think DIET is better because it anchors the domain and stays minimal. So the final frame would be DIET_ADOPTION.",
      "frame_name": "DIET_ADOPTION"
    }},
    {{
      "id": "p6",
      "original_phrase": "David Felt better after a few weeks",
      "rationale": "This event is about a positive change in condition. So the possible roots are RECOVERY WELLBEING and IMPROVEMENT. Between these IMPROVEMENT is better because it preserves the story signal and is more general than the phrase. To explain this root we can focus on the health domain. So the candidate modifiers are HEALTH WELLBEING and CONDITION. I think HEALTH is better because it anchors the domain and is minimal. So the final frame would be HEALTH_IMPROVEMENT.",
      "frame_name": "HEALTH_IMPROVEMENT"
    }},
    {{
      "id": "p7",
      "original_phrase": "David had stopped eating unhealthy foods",
      "rationale": "This event is about ending a food behavior. So the possible roots are ABSTINENCE REDUCTION and CESSATION. Between these CESSATION is better because it fits stopping and is more general than the surface action. To explain this root we can focus on the diet domain. So the candidate modifiers are DIET NUTRITION and FOOD. I think DIET is better because it anchors the domain and is minimal. So the final frame would be DIET_CESSATION.",
      "frame_name": "DIET_CESSATION"
    }}
  ]
}}
</JSON>

**Example 2**

Story:
“I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

Phrases:
[
  {{ "id":"p1","text":"I bought a cheap jacket" }},
  {{ "id":"p2","text":"Jacket fell apart the next day" }},
  {{ "id":"p3","text":"I concluded more expensive clothes last longer" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "I bought a cheap jacket",
      "rationale": "This event is about acquiring an item by paying. So the possible roots are SPENDING PURCHASE and ACQUISITION. Between these PURCHASE is better because it preserves the story signal and is more general than the verb. To explain this root we can focus on the price attribute. So the candidate modifiers are PRODUCT CLOTHING and CHEAP. I think CHEAP is better because it anchors the cost aspect and is minimal. So the final frame would be CHEAP_PURCHASE.",
      "frame_name": "CHEAP_PURCHASE"
    }},
    {{
      "id": "p2",
      "original_phrase": "Jacket fell apart the next day",
      "rationale": "This event is about an item not functioning as intended. So the possible roots are BREAKAGE FAILURE and DETERIORATION. Between these FAILURE is better because it captures the outcome and is more general than the surface description. To explain this root we can focus on the item category. So the candidate modifiers are PRODUCT CLOTHING and GARMENT. I think PRODUCT is better because it anchors the category and is minimal. So the final frame would be PRODUCT_FAILURE.",
      "frame_name": "PRODUCT_FAILURE"
    }},
    {{
      "id": "p3",
      "original_phrase": "I concluded more expensive clothes last longer",
      "rationale": "This event is about forming an insight from experience. So the possible roots are BELIEF REALIZATION and INFERENCE. Between these REALIZATION is better because it captures the insight and is more general than the phrasing. To explain this root we can focus on the source of knowledge. So the candidate modifiers are EXPERIENCE SHOPPING and CLOTHING. I think EXPERIENCE is better because it anchors the source without overfitting. So the final frame would be EXPERIENCE_REALIZATION.",
      "frame_name": "EXPERIENCE_REALIZATION"
    }}
  ]
}}
</JSON>

### Your Turn

#### Input Format
Story:
{story}

Phrases:
{phrases}

#### Remember:
- Choose **ROOT** first (one word, noun-like) by extracting the semantic head and nominalizing if needed.
- Choose **MODIFIER** as **one word**: either a **domain/category** or a **quality adjective**, based on phrase focus. It must be different from the root, carry story signal, avoid meta words.
- Keep frames **exactly two tokens**, **UPPERCASE**, with **one underscore**: `MODIFIER_ROOT`.
- **Banned ROOTs:** EVENT, ACTION, ACTIVITY, SITUATION, OCCURRENCE, THING, ITEM, OBJECT, PROCESS, INFORMATION, KNOWLEDGE, STUFF. You are not allowed to use these for roots.
- **Banned MODIFIERs:** GENERAL, QUALITY, THING, STUFF, EVENT, CONTEXT, TOPIC, AREA, DOMAIN, PEOPLE, PERSON, ENTITY, KNOWLEDGE, INFORMATION; plus specific names and single-instance items when a domain or category is available.
- In the **rationale**, use the **Self-talk** style exactly. Use periods only. No commas and no semicolons.
- **Consistency:** The suffix of **frame_name** must equal the chosen ROOT. The frame must be interpretable without the story.

Output: A single JSON object exactly matching the schema described in Output Format.

Return ONLY one JSON object. Do not output anything before or after it.
Wrap the array inside <JSON> ... </JSON> tags.
Provide output in the following format:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": ...,
      "rationale": ...,
      "frame_name": ...
    }},
    ...
  ]
}}
</JSON>

"""


prompt_abstraction_extraction21 = """"
### Role Assignment
You are a frame-generalization assistant.
Your job is to read a short **Story**, a set of **Phrases**, and their existing **Previous_Frames**, then produce a more **General_Frame** (a parent-class abstraction) for each phrase that remains faithful to the story’s meaning.

### What the Previous_Frames look like
Each **Previous_Frame** comes from an upstream extractor and is always in the form:
**[MODIFIER]_[ROOT]**
- Exactly **two tokens**, **UPPERCASE**, separated by **one underscore**.
- **MODIFIER** is a one-word domain/category noun or a one-word quality adjective.
- **ROOT** is a one-word noun-like label for the core event/state/concept.

### Task Definition
You will:
- Generalize each **Previous_Frame** to a broader, cross-domain **General_Frame** that still captures the phrase’s core meaning in the **Story** context.
- **Generalize BOTH parts** of the frame:
  - Make the new **ROOT** more general than the previous ROOT (a parent concept).
  - Make the new **MODIFIER** more general than the previous MODIFIER (a parent category/quality).
- Keep **causal roles explicit** when present (e.g., if a ROOT explicitly contains CAUSE or RESULT, preserve that role while generalizing the rest).
- Drop narrow domain detail unless essential for disambiguation; prefer cross-domain applicability over story-specific subtypes.
- Avoid metaphorical or meta frames; keep frames grounded in situational semantics.

### Frame Naming Constraints
- Output frame must be exactly: **MODIFIER_ROOT**
- Exactly **two tokens** total.
- Each token is **one word**, **UPPERCASE**, noun-like when possible.
- No extra underscores and no more than 2 tokens.

### Output Format
Return a single JSON object wrapped in **<JSON> ... </JSON>** tags with a top-level **results** array. For each phrase, include:
- **id**: the phrase identifier from input.
- **original_phrase**: the phrase text from input.
- **previous_frame**: the original MODIFIER_ROOT frame provided.
- **rationale**: a brief (1–2 sentences) explanation of how you generalized BOTH the modifier and the root, using story context.
- **frame_name**: the final, more general MODIFIER_ROOT frame name (exactly 2 tokens, UPPERCASE).

### Examples

**Example 1**

Story:
“David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.”

Phrases and previous frames:
[
  {{ "id":"p1","phrase":"David noticed weight gain", "previous_frame":"HEALTH_AWARENESS" }},
  {{ "id":"p2","phrase":"David examined his habits for a reason", "previous_frame":"HABIT_ANALYSIS" }},
  {{ "id":"p3","phrase":"David realized he ate too much fast food", "previous_frame":"DIET_REALIZATION" }},
  {{ "id":"p4","phrase":"David stopped going to burger places", "previous_frame":"HABIT_CESSATION" }},
  {{ "id":"p5","phrase":"David started a vegetarian diet", "previous_frame":"DIET_ADOPTION" }},
  {{ "id":"p6","phrase":"David felt better after a few weeks", "previous_frame":"HEALTH_IMPROVEMENT" }},
  {{ "id":"p7","phrase":"David had stopped eating unhealthy foods", "previous_frame":"DIET_CESSATION" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "David noticed weight gain",
      "previous_frame": "HEALTH_AWARENESS",
      "rationale": "Generalize the modifier from HEALTH to the broader PERSONAL domain. Generalize the root from AWARENESS to the broader cognitive state COGNITION while preserving that he notices a condition change.",
      "frame_name": "PERSONAL_COGNITION"
    }},
    {{
      "id": "p2",
      "original_phrase": "David examined his habits for a reason",
      "previous_frame": "HABIT_ANALYSIS",
      "rationale": "Lift HABIT to the broader category BEHAVIOR. Lift ANALYSIS to the broader evaluative process ASSESSMENT while keeping the idea of examining actions for explanation.",
      "frame_name": "BEHAVIOR_ASSESSMENT"
    }},
    {{
      "id": "p3",
      "original_phrase": "David realized he ate too much fast food",
      "previous_frame": "DIET_REALIZATION",
      "rationale": "Broaden DIET to BEHAVIOR to avoid food-specific detail. Broaden REALIZATION to COGNITION to keep the core meaning of gaining mental awareness of a cause-related behavior.",
      "frame_name": "BEHAVIOR_COGNITION"
    }},
    {{
      "id": "p4",
      "original_phrase": "David stopped going to burger places",
      "previous_frame": "HABIT_CESSATION",
      "rationale": "Generalize HABIT to BEHAVIOR as the parent category. Generalize CESSATION to DISENGAGEMENT as a broader form of stopping participation in an ongoing pattern.",
      "frame_name": "BEHAVIOR_DISENGAGEMENT"
    }},
    {{
      "id": "p5",
      "original_phrase": "David started a vegetarian diet",
      "previous_frame": "DIET_ADOPTION",
      "rationale": "Generalize DIET to BEHAVIOR to make it cross-domain. Generalize ADOPTION to ENGAGEMENT to capture a broader commitment to a new ongoing practice.",
      "frame_name": "BEHAVIOR_ENGAGEMENT"
    }},
    {{
      "id": "p6",
      "original_phrase": "David felt better after a few weeks",
      "previous_frame": "HEALTH_IMPROVEMENT",
      "rationale": "Broaden HEALTH to CONDITION to include any personal state without medical specificity. Broaden IMPROVEMENT to CHANGE to capture a general positive shift in state over time.",
      "frame_name": "CONDITION_CHANGE"
    }},
    {{
      "id": "p7",
      "original_phrase": "David had stopped eating unhealthy foods",
      "previous_frame": "DIET_CESSATION",
      "rationale": "Generalize DIET to BEHAVIOR to remove food-specific domain detail. Generalize CESSATION to DISENGAGEMENT to represent a broader stopping of an established practice.",
      "frame_name": "BEHAVIOR_DISENGAGEMENT"
    }}
  ]
}}
</JSON>

**Example 2**

Story:
“I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

Phrases and previous frames:
[
  {{ "id":"p1","phrase":"I bought a cheap jacket", "previous_frame":"CHEAP_PURCHASE" }},
  {{ "id":"p2","phrase":"Jacket fell apart the next day", "previous_frame":"PRODUCT_FAILURE" }},
  {{ "id":"p3","phrase":"I concluded more expensive clothes last longer", "previous_frame":"EXPERIENCE_REALIZATION" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "I bought a cheap jacket",
      "previous_frame": "CHEAP_PURCHASE",
      "rationale": "Generalize CHEAP to the broader cost dimension COST rather than a specific degree. Generalize PURCHASE to the broader acquisition concept ACQUISITION while keeping the meaning of obtaining an item via payment.",
      "frame_name": "COST_ACQUISITION"
    }},
    {{
      "id": "p2",
      "original_phrase": "Jacket fell apart the next day",
      "previous_frame": "PRODUCT_FAILURE",
      "rationale": "Generalize PRODUCT to the broader category OBJECT since the specific marketplace framing is not essential. Generalize FAILURE to the broader negative condition PROBLEM to capture any breakdown outcome.",
      "frame_name": "OBJECT_PROBLEM"
    }},
    {{
      "id": "p3",
      "original_phrase": "I concluded more expensive clothes last longer",
      "previous_frame": "EXPERIENCE_REALIZATION",
      "rationale": "Generalize EXPERIENCE to EVIDENCE as a broader source category for forming beliefs. Generalize REALIZATION to COGNITION to represent a general mental update drawn from what happened in the story.",
      "frame_name": "EVIDENCE_COGNITION"
    }}
  ]
}}
</JSON>

### Your Turn

#### Input Format
Story:
{story}

Phrases and previous frames:
{phrases}

#### Remember:
- Each **previous_frame** is **MODIFIER_ROOT** (two tokens).
- Produce a **more general MODIFIER_ROOT** for each phrase by generalizing BOTH the modifier and the root.
- Keep frames grounded and cross-domain.
- Output MUST be exactly one JSON object, wrapped in <JSON> ... </JSON> tags, and match the schema.

Return ONLY one JSON object. Do not output anything before or after it.
Provide output in the following format:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "...",
      "previous_frame": "...",
      "rationale": "...",
      "frame_name": "..."
    }},
    ...
  ]
}}
</JSON>

"""


prompt_abstraction_extraction22 = """

### Role Assignment
You are an **event-typing and evaluation assistant**.  
Your job is to read a short **Story** and a list of **Phrases**, then for **each phrase** assign:
1) an **Event Type** from **STATE**, **ACTION**, **OUTCOME**, and  
2) an **Evaluation** label that is **compatible with the chosen Event Type**.

### Task Definition
Apply these rules **independently per phrase** using the **whole story context**. Narrative order does **not** determine causality.

#### Step 1 — Decide ACTION vs non-ACTION
- If the phrase foregrounds a controllable **doing** or an **initiated change** by an agent → label **ACTION**.
  - Diagnostics: contains a verb someone can perform. Could be phrased as a command. The focus is on the act itself.
  - Not ACTION: non-agentive happenings. States or beliefs presented as results.

#### Step 2 — If not ACTION, decide STATE vs OUTCOME (order-agnostic)
- **STATE**: a condition that stands **on its own** in the story and **does not depend on any other explicitly stated event**. It remains fully interpretable if all other sentences were deleted.
- **OUTCOME**: a **resulting condition or belief** whose interpretation **requires** pointing to another **explicitly stated** event in the story world, **regardless of where that event appears**. You must be able to cite that causal event’s text from the story.

> Cues: Resulting beliefs like “realized” or “concluded” are **OUTCOME** **only when** they arise from other **explicit** events. A phrase can still be **STATE** if it functions as a standing status description without implying a cause that is explicitly written. If causality is only inferred from world knowledge and not written in the story, default to **STATE**. Lessons and generalized takeaways are **OUTCOME**. Their evaluation depends on the content and framing as specified below.

### Evaluation Mapping
Choose **exactly one** evaluation from the allowed set for the chosen type:

- **STATE →**
  - Positive: **EASE** — indicates comfort or stability or relief.
  - Negative: **STRUGGLE** — indicates difficulty or pain or burden.
  - Neutral: **NONE** — purely descriptive without a positive or negative tilt.

- **ACTION →**
  - Active (Positive): **EFFORT** — the act is goal directed and attempts to solve a problem or improve a situation.
  - Passive (Negative): **INDIFFERENCE** — the act neglects the problem or worsens it or ignores obvious risks.
  - Neutral: **NONE** — the act is routine or descriptive with no clear helpfulness or harm.
  - *Note:* Classify **the act itself**, **not** its downstream results.

- **OUTCOME →**
  - Positive: **GAIN** — the resulting state improves wellbeing or knowledge or resources or function.
  - Negative: **LOSS** — the resulting state reduces wellbeing or knowledge or resources or function.
  - Neutral: **NONE** — mixed or unclear impact.  
  - *Notes on beliefs and lessons:*  
    - If the belief or realization primarily **exposes harm or deficit** in the situation or self understanding, label **LOSS**. Example pattern: realizing one has been making a harmful mistake.  
    - If the belief or realization **equips corrective knowledge** or explicitly increases capability for better choices, label **GAIN**.  
    - If the takeaway is generic and not framed as helpful or harmful, label **NONE**.

### Rationale Style (Self-talk)
Write your rationale as **exactly six single-sentence lines** per phrase, using **periods only**, **no commas or semicolons**, and **no extra line breaks between titles**. Use these titles in this order. If the phrase is an **ACTION**, you may **skip the Deletion test and Explicit-cause test content** by stating they are skipped because the event is action, but you must still justify why it is an action by naming the controllable verb and agent.
- **Main idea:** This phrase is about ...
- **Doing:** Explain whether doing is present or absent and why by naming the controllable verb and whether an agent can initiate it then state **ACTION** or **non-ACTION**.
- **Deletion test:** Explain what the phrase still means if all other sentences are deleted and whether it remains fully interpretable on its own.
- **Explicit-cause test:** If proposing **OUTCOME**, identify the specific causal event from the story by quoting or clearly naming it and mention any temporal or causal cue such as because or after or therefore or realized that. If none exists say none.
- **Evaluation:** Justify the evaluation using the mapping tests for the chosen type and refer to wellbeing or knowledge or resources or function as applicable.
- **Final decision:** State the event type and the evaluation using the exact labels.

### Output Format
Return a single JSON object wrapped in **<JSON> ... </JSON>** tags with a top-level **results** array. For each phrase include:
- **id**: the phrase identifier from input.
- **original_phrase**: the exact phrase text from input.
- **rationale**: your self-talk text following the **Rationale Style (Self-talk)** section above.
- **event_type**: The type of the event, one of "ACTION", "STATE", "OUTCOME" 
- **evaluation**: The evaluation for each event. If it is STATE, then one of "EASE", "STRUGGLE", "NONE"; if it is an ACTION, then one of the "EFFORT", "INDIFFERENCE", "NONE"; if it is an OUTCOME, then one of the "GAIN", "LOSS", "NONE".
---

### Examples

**Example 1**

Story:  
“David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.”

Phrases:  
[
  {{ "id":"p1","text":"David noticed weight gain" }},
  {{ "id":"p2","text":"David examined his habits for a reason" }},
  {{ "id":"p3","text":"David Realized he ate too much fast food" }},
  {{ "id":"p4","text":"David Stopped going to burger places" }},
  {{ "id":"p5","text":"David Started a vegetarian diet" }},
  {{ "id":"p6","text":"David Felt better after a few weeks" }},
  {{ "id":"p7","text":"David had stopped eating unhealthy foods" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "David noticed weight gain",
      "rationale": "Main idea: This phrase is about recognizing a health condition. Doing: Doing is absent because notice reports awareness not a controllable initiated change so it is non action. Deletion test: The phrase remains a complete description of a condition if the story is deleted. Explicit-cause test: No explicit causal event is required to interpret this awareness. Evaluation: The condition signals difficulty with health and self image so it matches struggle. Final decision: STATE STRUGGLE.",
      "event_type": "STATE",
      "evaluation": "STRUGGLE"
    }},
    {{
      "id": "p2",
      "original_phrase": "David examined his habits for a reason",
      "rationale": "Main idea: This phrase is about an investigative act. Doing: Doing is present because examine is a controllable verb that an agent performs to initiate change so it is action. Deletion test: Skipped because the event is action. Explicit-cause test: Skipped because the event is action. Evaluation: The act targets a problem to gain understanding which fits effort. Final decision: ACTION EFFORT.",
      "event_type": "ACTION",
      "evaluation": "EFFORT"
    }},
    {{
      "id": "p3",
      "original_phrase": "David Realized he ate too much fast food",
      "rationale": "Main idea: This phrase is about a resulting belief about harmful behavior. Doing: Doing is absent because realize is not a controllable initiated change so it is non action. Deletion test: The phrase is interpretable but the status as a realization depends on prior analysis and weight gain. Explicit-cause test: The cause is the earlier habit examination and the noted weight gain which are explicit and the cue is realized that. Evaluation: This realization exposes a harmful mistake and reduces wellbeing appraisal so it matches loss. Final decision: OUTCOME LOSS.",
      "event_type": "OUTCOME",
      "evaluation": "LOSS"
    }},
    {{
      "id": "p4",
      "original_phrase": "David Stopped going to burger places",
      "rationale": "Main idea: This phrase is about ending a behavior. Doing: Doing is present because stop going is a controllable decision by an agent so it is action. Deletion test: Skipped because the event is action. Explicit-cause test: Skipped because the event is action. Evaluation: The act directly removes an unhealthy trigger which is corrective so it matches effort. Final decision: ACTION EFFORT.",
      "event_type": "ACTION",
      "evaluation": "EFFORT"
    }},
    {{
      "id": "p5",
      "original_phrase": "David Started a vegetarian diet",
      "rationale": "Main idea: This phrase is about initiating a practice. Doing: Doing is present because start a diet is a controllable adoption by an agent so it is action. Deletion test: Skipped because the event is action. Explicit-cause test: Skipped because the event is action. Evaluation: The act aims to improve health and is goal directed so it matches effort. Final decision: ACTION EFFORT.",
      "event_type": "ACTION",
      "evaluation": "EFFORT"
    }},
    {{
      "id": "p6",
      "original_phrase": "David Felt better after a few weeks",
      "rationale": "Main idea: This phrase is about an improved condition. Doing: Doing is absent because feel better is not a controllable initiated change so it is non action. Deletion test: The phrase is interpretable but its improvement status suggests earlier dietary changes. Explicit-cause test: The improvement depends on stopping burgers and starting a vegetarian diet which are explicit and the cue is after. Evaluation: Wellbeing increases which fits gain. Final decision: OUTCOME GAIN.",
      "event_type": "OUTCOME",
      "evaluation": "GAIN"
    }},
    {{
      "id": "p7",
      "original_phrase": "David had stopped eating unhealthy foods",
      "rationale": "Main idea: This phrase is about a standing status of abstaining. Doing: Doing is absent in this phrasing because it reports a condition rather than a current controllable act so it is non action. Deletion test: The phrase stands as a complete status if the story is deleted. Explicit-cause test: No explicit causal event is required to interpret the status. Evaluation: The status indicates relief and stability which fits ease. Final decision: STATE EASE.",
      "event_type": "STATE",
      "evaluation": "EASE"
    }}
  ]
}}
</JSON>

---

**Example 2**

Story: “I was really upset by my new jacket. I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

Phrases:  
[
  {{ "id":"p1","text":"upset by the new jacket" }},
  {{ "id":"p2","text":"I bought a cheap jacket" }},
  {{ "id":"p3","text":"Jacket fell apart the next day" }},
  {{ "id":"p4","text":"I concluded more expensive clothes last longer" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "upset by the new jacket",
      "rationale": "Main idea: This phrase is about an emotional condition that follows events. Doing: Doing is absent because being upset is not a controllable initiated change so it is non action. Deletion test: The phrase is interpretable but it points to something bad that happened to the jacket. Explicit-cause test: The feeling depends on buying a cheap jacket and the jacket failing which are explicit. Evaluation: Wellbeing is reduced which fits loss. Final decision: OUTCOME LOSS.",
      "event_type": "OUTCOME",
      "evaluation": "LOSS"
    }},
    {{
      "id": "p2",
      "original_phrase": "I bought a cheap jacket",
      "rationale": "Main idea: This phrase is about a purchase. Doing: Doing is present because buy is a controllable verb performed by the agent so it is action. Deletion test: Skipped because the event is action. Explicit-cause test: Skipped because the event is action. Evaluation: The act ignores quality and increases risk which is neglectful so it matches indifference. Final decision: ACTION INDIFFERENCE.",
      "event_type": "ACTION",
      "evaluation": "INDIFFERENCE"
    }},
    {{
      "id": "p3",
      "original_phrase": "Jacket fell apart the next day",
      "rationale": "Main idea: This phrase is about a broken condition of the jacket. Doing: Doing is absent because fall apart is not an agent controlled act so it is non action. Deletion test: The phrase is interpretable but the timing suggests a prior purchase event. Explicit-cause test: The failure follows the cheap purchase which is explicit and the cue is the next day. Evaluation: Function and money are lost which fits loss. Final decision: OUTCOME LOSS.",
      "event_type": "OUTCOME",
      "evaluation": "LOSS"
    }},
    {{
      "id": "p4",
      "original_phrase": "I concluded more expensive clothes last longer",
      "rationale": "Main idea: This phrase is about a lesson learned from experience. Doing: Doing is absent because conclude is not a controllable initiated change in the moment so it is non action. Deletion test: The phrase is interpretable but it clearly depends on what happened with the jacket. Explicit-cause test: The conclusion arises from buying the cheap jacket and it failing which are explicit. Evaluation: This is a generalized takeaway without explicit benefit or harm so it matches none. Final decision: OUTCOME NONE.",
      "event_type": "OUTCOME",
      "evaluation": "NONE"
    }}
  ]
}}
</JSON>

---

### Your Turn

#### Input Format
Story:
{story}

Phrases:
{phrases}

### Remember
- Causality is **order-agnostic**. Use the whole story world.  
- **Doing present → ACTION**. If not, choose **STATE** or **OUTCOME** by whether interpretation requires an **explicitly stated** cause.  
- Use the **Deletion Test** and **Explicit-Cause Test** in your rationale. If the cause is only inferred, default to **STATE**.  
- For **beliefs and lessons**, set **OUTCOME** and choose **LOSS** when the belief exposes harm or deficit, **GAIN** when it provides corrective knowledge, and **NONE** when neutrality is clear.  
- **Rationale** must follow the six titled single-sentence lines in order. Periods only. No commas. No semicolons.  
- Do not add extra keys or commentary. Keep outputs consistent and valid.

Output: A single JSON object exactly matching the schema described in Output Format.

Return ONLY one JSON object. Do not output anything before or after it.
Wrap the array inside <JSON> ... </JSON> tags.
Provide output in the following format:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": ...,
      "rationale": ...,
      "event_type": ...,
      "evaluation": ...
    }},
    ...
  ]
}}
</JSON>


"""


prompt_abstraction_extraction23 = """

### Role Assignment
You are an **event-typing and evaluation assistant**.  
Your job is to read a short **Story** and a list of **Phrases**, then for **each phrase** assign:
1) an **Event Type** from **STATE**, **ACTION**, **OUTCOME**, and  
2) an **Evaluation** label that is **compatible with the chosen Event Type**.

### Task Definition
Apply these rules **independently per phrase** using the **whole story context**. Narrative order does **not** determine causality. Always answer with **evidence-first** reasoning grounded in the story text.

#### Step 1 — Decide ACTION vs non-ACTION
- If the phrase foregrounds a controllable **doing** or an **initiated change** by an agent → label **ACTION**.
  - Diagnostics for **ACTION** must be explicitly checked:  
    - **Main verb controllability test**: name the main verb and confirm an agent can intentionally perform it and that it can be phrased as a command.  
    - **Agent presence test**: identify the agent if stated or clearly implied by the phrase.  
  - Not ACTION: non-agentive happenings. States or beliefs presented as results.

#### Step 2 — If not ACTION, decide STATE vs OUTCOME (order-agnostic)
- **STATE**: a condition that stands **on its own** in the story and **does not depend on any other explicitly stated event**. It remains fully interpretable if all other sentences were deleted. When unsure after tests, default to **STATE**.
- **OUTCOME**: a **resulting condition or belief** whose interpretation **requires** pointing to another **explicitly stated** event in the story world, **regardless of where that event appears**. You must be able to cite that causal event’s text from the story. **Cue + Link gate**: OUTCOME is permitted only if you provide both an overt cue token or temporal link and a specific cited event from the story.

> Cues: Resulting beliefs like “realized” or “concluded” are **OUTCOME** **only when** they arise from other **explicit** events. A phrase can still be **STATE** if it functions as a standing status description without implying a cause that is explicitly written. If causality is only inferred from world knowledge and not written in the story, default to **STATE**. Lessons and generalized takeaways are **OUTCOME**. Their evaluation depends on the content and framing as specified below.

### Evaluation Mapping
Choose **exactly one** evaluation from the allowed set for the chosen type:

- **STATE →**
  - Positive: **EASE** — indicates comfort or stability or relief.
  - Negative: **STRUGGLE** — indicates difficulty or pain or burden.
  - Neutral: **NONE** — purely descriptive without a positive or negative tilt.

- **ACTION →**
  - Active (Positive): **EFFORT** — the act is goal directed and attempts to solve a problem or improve a situation.
  - Passive (Negative): **INDIFFERENCE** — the act neglects the problem or worsens it or ignores obvious risks.
  - Neutral: **NONE** — the act is routine or descriptive with no clear helpfulness or harm.
  - *Note:* Classify **the act itself**, **not** its downstream results.

- **OUTCOME →**
  - Positive: **GAIN** — the resulting state improves wellbeing or knowledge or resources or function.
  - Negative: **LOSS** — the resulting state reduces wellbeing or knowledge or resources or function.
  - Neutral: **NONE** — mixed or unclear impact.  
  - *Notes on beliefs and lessons:*  
    - If the belief or realization primarily **exposes harm or deficit** in the situation or self understanding, label **LOSS**. Example pattern: realizing one has been making a harmful mistake.  
    - If the belief or realization **equips corrective knowledge** or explicitly increases capability for better choices, label **GAIN**.  
    - If the takeaway is generic and not framed as helpful or harmful, label **NONE**.

### Evidence and Discipline Requirements
- **Evidence-first span quoting**: Whenever you claim dependence or causality, cite an exact short quote from the story and include a sentence ID like **S1** or **S2** that you scanned.  
- **Token-budgeted scanning**: State which story sentence IDs you scanned for the decision.  
- **Explicit-cause gate**: OUTCOME requires a quoted cause span and a cue token such as because or therefore or after or realized that.  
- **Deletion test with paraphrase**: For non-ACTION, paraphrase the phrase as a standalone proposition to justify whether meaning survives without context.  
- **Consistency check**: State if any scanned sentence contradicts your decision. If contradiction is found, reconsider and use the conservative default.  
- **Uncertainty flag with conservative default**: If evidence is weak, state uncertainty and default to **STATE** when ACTION is ruled out.  
- **Lightweight NLI self-check**: For OUTCOME, assert whether the cited cause plus cue **supports** or **does not entail** the result. If not supported, do not use OUTCOME.  
- **Boundary checklist for STATE vs OUTCOME**: Emotion without explicit linked event → STATE. Generic status without cue → STATE. Temporal link without cited event → STATE. Only if cue plus cited event plus entailment hold → OUTCOME.

### Rationale Style (Self-talk)
Write your rationale as **exactly six single-sentence lines** per phrase, using **periods only**, **no commas or semicolons**, and **no extra line breaks between titles**. Use these titles in this order. If the phrase is an **ACTION**, you may **skip the Deletion test and Explicit-cause test content** by stating they are skipped because the event is action, but you must still justify why it is an action by naming the controllable verb and agent and showing it can be phrased as a command or initiated change. Each line must include a concrete justification or quote from the story as evidence when you claim dependence or causality and must list scanned sentence IDs.
- **Main idea:** State the core content and list the scanned sentence IDs like S1 S2 S3.  
- **Doing:** Decide ACTION or non action and justify using the verb controllability test and agent presence and command form like quote go or examine if applicable.  
- **Deletion test:** Paraphrase the phrase as a standalone proposition and argue whether meaning remains without context by pointing to lexical content that encodes status or malfunction or emotion.  
- **Explicit-cause test:** If proposing outcome cite the specific causal event by quoting or naming it with a sentence ID and name the cue token and state an entailment judgment supports or unknown or conflicts. If none say none and explain why inference alone is insufficient.  
- **Evaluation:** Justify the evaluation using the mapping and refer to wellbeing or knowledge or resources or function and note any contradiction check outcome none found or found.  
- **Final decision:** State the event type and the evaluation using exact labels and state uncertainty low or high and if high confirm conservative default applied.

### Output Format
Return a single JSON object wrapped in **<JSON> ... </JSON>** tags with a top-level **results** array. For each phrase include:
- **id**: the phrase identifier from input.
- **original_phrase**: the exact phrase text from input.
- **rationale**: your self-talk text following the **Rationale Style (Self-talk)** section above.
- **event_type**: The type of the event, one of "ACTION", "STATE", "OUTCOME" 
- **evaluation**: The evaluation for each event. If it is STATE, then one of "EASE", "STRUGGLE", "NONE"; if it is an ACTION, then one of the "EFFORT", "INDIFFERENCE", "NONE"; if it is an OUTCOME, then one of the "GAIN", "LOSS", "NONE".
---

### Examples

**Example 1**

Story:  
“David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.”

Phrases:  
[
  {{ "id":"p1","text":"David noticed weight gain" }},
  {{ "id":"p2","text":"David examined his habits for a reason" }},
  {{ "id":"p3","text":"David Realized he ate too much fast food" }},
  {{ "id":"p4","text":"David Stopped going to burger places" }},
  {{ "id":"p5","text":"David Started a vegetarian diet" }},
  {{ "id":"p6","text":"David Felt better after a few weeks" }},
  {{ "id":"p7","text":"David had stopped eating unhealthy foods" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "David noticed weight gain",
      "rationale": "Main idea: Recognizing a health condition and I scanned S1 S2. Doing: Non action because notice reports awareness and awareness is not an agent initiated change and it cannot be commanded as notice now. Deletion test: As a standalone proposition it means David has the condition of weight gain and this meaning is encoded by the noun phrase weight gain without needing a cause. Explicit-cause test: None because the phrase meaning is complete and no explicit event is required to interpret recognition. Evaluation: This condition imposes burden on health which aligns with struggle and no contradictions found. Final decision: STATE STRUGGLE and uncertainty low and conservative default not applied.",
      "event_type": "STATE",
      "evaluation": "STRUGGLE"
    }},
    {{
      "id": "p2",
      "original_phrase": "David examined his habits for a reason",
      "rationale": "Main idea: Investigative act and I scanned S2. Doing: Action because the main verb examine is agent controllable and can be phrased as a command examine your habits and the agent David is explicit. Deletion test: Skipped because event is action. Explicit-cause test: Skipped because event is action. Evaluation: The act seeks understanding to improve the situation which maps to effort and no contradictions found. Final decision: ACTION EFFORT and uncertainty low and conservative default not applied.",
      "event_type": "ACTION",
      "evaluation": "EFFORT"
    }},
    {{
      "id": "p3",
      "original_phrase": "David Realized he ate too much fast food",
      "rationale": "Main idea: Resulting belief about harmful behavior and I scanned S1 S2 S3. Doing: Non action because realize is a belief change not a controllable initiated deed and cannot be commanded as realize now. Deletion test: As a standalone proposition it communicates a recognition but realization status implies dependence on prior facts about eating and weight stated elsewhere. Explicit-cause test: Cause is habit examination in S2 and weight condition in S1 and the cue token is realized that and the entailment supports because S2 plus S1 explains the realization. Evaluation: The belief exposes a harmful dietary mistake which reduces wellbeing appraisal and therefore maps to loss and no contradictions found. Final decision: OUTCOME LOSS and uncertainty low and conservative default not applied.",
      "event_type": "OUTCOME",
      "evaluation": "LOSS"
    }},
    {{
      "id": "p4",
      "original_phrase": "David Stopped going to burger places",
      "rationale": "Main idea: Ending a behavior and I scanned S3 S4. Doing: Action because stop going is agent controllable and can be commanded as stop going to burger places and David is the agent. Deletion test: Skipped because event is action. Explicit-cause test: Skipped because event is action. Evaluation: The act removes an unhealthy trigger which is corrective so it maps to effort and no contradictions found. Final decision: ACTION EFFORT and uncertainty low and conservative default not applied.",
      "event_type": "ACTION",
      "evaluation": "EFFORT"
    }},
    {{
      "id": "p5",
      "original_phrase": "David Started a vegetarian diet",
      "rationale": "Main idea: Initiating a practice and I scanned S4. Doing: Action because start a diet is agent controllable and can be commanded as start a vegetarian diet and the agent David is explicit. Deletion test: Skipped because event is action. Explicit-cause test: Skipped because event is action. Evaluation: The act is goal directed toward better health which maps to effort and no contradictions found. Final decision: ACTION EFFORT and uncertainty low and conservative default not applied.",
      "event_type": "ACTION",
      "evaluation": "EFFORT"
    }},
    {{
      "id": "p6",
      "original_phrase": "David Felt better after a few weeks",
      "rationale": "Main idea: Improved condition over time and I scanned S4 S5. Doing: Non action because feel better is a state description and not agent initiated and cannot be commanded as feel better now. Deletion test: As a standalone proposition it encodes an improvement state but the phrase after a few weeks is a temporal cue that signals a prior change. Explicit-cause test: Causes are stopped going to burger places and started a vegetarian diet in S4 with the cue after and the entailment supports because these changes plausibly lead to improved wellbeing. Evaluation: Wellbeing increases which maps to gain and no contradictions found. Final decision: OUTCOME GAIN and uncertainty low and conservative default not applied.",
      "event_type": "OUTCOME",
      "evaluation": "GAIN"
    }},
    {{
      "id": "p7",
      "original_phrase": "David had stopped eating unhealthy foods",
      "rationale": "Main idea: Standing status of abstaining and I scanned S4. Doing: Non action because the phrasing reports a status rather than a current initiated deed and cannot be commanded in this perfect aspect. Deletion test: As a standalone proposition it communicates the status of not eating unhealthy foods which is interpretable without citing a cause. Explicit-cause test: None because interpretation does not require another explicit event and inference alone would be insufficient to force a cause. Evaluation: The status indicates relief and stability so it maps to ease and no contradictions found. Final decision: STATE EASE and uncertainty low and conservative default not applied.",
      "event_type": "STATE",
      "evaluation": "EASE"
    }}
  ]
}}
</JSON>

---

**Example 2**

Story: “I was really upset by my new jacket. I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

Phrases:  
[
  {{ "id":"p1","text":"upset by the new jacket" }},
  {{ "id":"p2","text":"I bought a cheap jacket" }},
  {{ "id":"p3","text":"Jacket fell apart the next day" }},
  {{ "id":"p4","text":"I concluded more expensive clothes last longer" }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "upset by the new jacket",
      "rationale": "Main idea: Emotional condition following events and I scanned S1 S2 S3. Doing: Non action because be upset is not an agent initiated deed and cannot be ordered as be upset now. Deletion test: As a standalone proposition it encodes an adverse emotional state but the reference to the new jacket hints at dependence on what happened to it. Explicit-cause test: Causes are bought a cheap jacket in S2 and it fell apart in S3 and the cue is by the new jacket and entailment supports because damage to the jacket explains being upset. Evaluation: Emotional wellbeing is reduced which maps to loss and no contradictions found. Final decision: OUTCOME LOSS and uncertainty low and conservative default not applied.",
      "event_type": "OUTCOME",
      "evaluation": "LOSS"
    }},
    {{
      "id": "p2",
      "original_phrase": "I bought a cheap jacket",
      "rationale": "Main idea: Purchase event and I scanned S2. Doing: Action because buy is agent controllable and can be commanded as buy a jacket and the agent I is explicit. Deletion test: Skipped because event is action. Explicit-cause test: Skipped because event is action. Evaluation: The act overlooks quality and increases risk which maps to indifference and no contradictions found. Final decision: ACTION INDIFFERENCE and uncertainty low and conservative default not applied.",
      "event_type": "ACTION",
      "evaluation": "INDIFFERENCE"
    }},
    {{
      "id": "p3",
      "original_phrase": "Jacket fell apart the next day",
      "rationale": "Main idea: Broken condition of the jacket and I scanned S2 S3. Doing: Non action because fall apart is not agent controlled and cannot be commanded. Deletion test: As a standalone proposition it encodes an equipment failure state and is interpretable but the temporal phrase the next day signals a prior event. Explicit-cause test: Cause is the purchase in S2 linked by the temporal cue the next day and entailment supports because a cheap low quality purchase plausibly precedes failure in this story. Evaluation: Function and money are reduced which maps to loss and no contradictions found. Final decision: OUTCOME LOSS and uncertainty low and conservative default not applied.",
      "event_type": "OUTCOME",
      "evaluation": "LOSS"
    }},
    {{
      "id": "p4",
      "original_phrase": "I concluded more expensive clothes last longer",
      "rationale": "Main idea: Lesson learned and I scanned S2 S3 S4. Doing: Non action because conclude is a belief change not a controllable deed and cannot be commanded as conclude now. Deletion test: As a standalone proposition it communicates a generalized rule but its status as a conclusion depends on the earlier purchase and failure. Explicit-cause test: Causes are I bought a cheap jacket in S2 and it fell apart in S3 and the cue is concluded and entailment supports because those events justify the rule. Evaluation: This is a generalized takeaway without explicit immediate benefit or harm so it maps to none and no contradictions found. Final decision: OUTCOME NONE and uncertainty low and conservative default not applied.",
      "event_type": "OUTCOME",
      "evaluation": "NONE"
    }}
  ]
}}
</JSON>

---

### Your Turn

#### Input Format
Story:
{story}

Phrases:
{phrases}

### Remember
- Causality is **order-agnostic**. Use the whole story world.  
- **Doing present → ACTION**. If not, choose **STATE** or **OUTCOME** by whether interpretation requires an **explicitly stated** cause.  
- Use the **Deletion Test** and **Explicit-Cause Test** in your rationale and provide concrete justification or short quotes with sentence IDs whenever you claim dependence or causality. If the cause is only inferred, default to **STATE**.  
- Apply the **Cue + Link gate** for OUTCOME and perform the **entailment self-check**.  
- Use the **Boundary checklist** and the **conservative default** when ambiguous.  
- **Rationale** must follow the six titled single-sentence lines in order. Periods only. No commas. No semicolons.  
- Do not add extra keys or commentary. Keep outputs consistent and valid.

Output: A single JSON object exactly matching the schema described in Output Format.

Return ONLY one JSON object. Do not output anything before or after it.
Wrap the array inside <JSON> ... </JSON> tags.
Provide output in the following format:
<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": ...,
      "rationale": ...,
      "event_type": ...,
      "evaluation": ...
    }},
    ...
  ]
}}
</JSON>


"""



prompt_abstraction_extraction24 = """
## Role Assignment
You are a **simple narrative timeline extractor**. Your task is to:
Assign each event ID a **position in story-time** and output per-event results.

---
## Task Definition
Given a short list of event phrases with IDs:
- **Goal — Story-time positions**: Determine the order in which events **actually happen in time**, not how they are narrated. 
- The first sentence may describe a later effect or reaction. 
- Infer order from cues such as before, after, once, used to, kept, then, however, stopped, noticed, decided, explicit time markers, and relative durations. 
- Prefer **causal and temporal logic** over narration order.

You will produce a **two-part output**:
1) **all_rationale**: a numbered, sentence-only rationale that assigns a **position** to every ID.
2) **results**: an array of per-event objects with fields **id**, **original_phrase**, **rationale**, and **position**.  
   **Important**: The **results array MUST be in the exact input ID order** (p1, then p2, then p3, …), regardless of their positions. Positions are extracted from **all_rationale**.

---
## Term Definitions
- **N**: the number of input phrases.
- **position**: the rank of an event in **actual story-time**. Position "1" is earliest. Positions increase by 1 with no gaps, and there are no ties.
- **all_rationale**: a compact list of N sentences that each state the reason and the assignment and end with **so position k is pX.**

---
## Rationale Style and Generation Procedure
Produce **all_rationale** as **exactly N sentences**, one per event, using **periods only**. **Do not use commas or semicolons** inside these sentences. (Other punctuation such as hyphens or parentheses is allowed if needed.)

Each sentence must strictly follow this template and order:
- **The first event in time is … which is pX because … so position 1 is pX.**
- **After this the next event is … which is pY because … so position 2 is pY.** Continue incrementing positions for all remaining events.
- **Finally the last event is … which is pZ because … so position N is pZ.**

Guidelines:
- Decide by **story-time**, not narration order.
- Reactions must not precede the states or events that trigger them.
- Evaluations must not precede the events they evaluate.
- Respect explicit time markers and durations.
- **Every input ID must appear exactly once in all_rationale.**

---
## Building the Results
After writing **all_rationale**:
1) Start listing the **phrases** in their **original input order** (p1, p2, p3, …).  
2) For each phrase:
   - Extract its **position** from **all_rationale** (the number at the end of the sentence that mentions its ID).  
   - Copy that exact rationale sentence into the **rationale** field of the result.  
   - Set **position** to that number as a **string** (e.g., `"1"`, `"2"`, `"3"`).  
   - Keep all key–value pairs in the result on separate lines.

---
## Output Format
Return a single JSON object wrapped in **<JSON> ... </JSON>** tags with two top-level keys: **all_rationale** and **results**.

### Keys Description
- **all_rationale**: a single string that contains exactly N sentences. Each sentence must describe the reasoning behind the event’s position in time and end with **so position k is pX.** This provides the global explanation of story-time order.  
- **results**: an array of N objects, listed in the **same order as the input IDs** (p1, p2, p3, …). Each object represents one phrase and includes the following fields:  
  - **id**: the phrase identifier (e.g., `"p1"`, `"p2"`).  
  - **original_phrase**: the exact phrase text from input.  
  - **rationale**: the specific sentence from **all_rationale** that mentions this phrase, showing why it received its time position.  
  - **position**: a string value (inside quotes) indicating the phrase’s story-time position (e.g., `"1"`, `"2"`, `"3"`).  

---
## Examples

**Example 1**
Story:
“I noticed I had put on weight. I examined my habits. I realized I was eating too much fast food. I stopped going to burger places. I started a vegetarian diet. After a few weeks I felt better.”

Phrases:
[
  {{ "id":"p1","text":"David noticed weight gain" }},
  {{ "id":"p2","text":"David examined his habits for a reason" }},
  {{ "id":"p3","text":"David Realized he ate too much fast food" }},
  {{ "id":"p4","text":"David Stopped going to burger places" }},
  {{ "id":"p5","text":"David Started a vegetarian diet" }},
  {{ "id":"p6","text":"David Felt better after a few weeks" }},
  {{ "id":"p7","text":"David had stopped eating unhealthy foods" }}
]

Output:
<JSON>
{{
  "all_rationale": "The first event in time is David noticed weight gain which is p1 because awareness of a present condition precedes analysis and action so position 1 is p1. After this the next event is David examined his habits which is p2 because investigation follows noticing so position 2 is p2. After this the next event is David realized he ate too much fast food which is p3 because realization follows analysis so position 3 is p3. After this the next event is David stopped going to burger places which is p4 because actions follow realization so position 4 is p4. After this the next event is David started a vegetarian diet which is p5 because adopting a new plan follows stopping so position 5 is p5. After this the next event is David had stopped eating unhealthy foods which is p7 because consolidation of change precedes delayed outcomes so position 6 is p7. Finally the last event is David felt better after a few weeks which is p6 because the time marker after a few weeks places the outcome last so position 7 is p6.",
  "results": [
    {{
      "id":"p1",
      "original_phrase":"David noticed weight gain",
      "rationale":"The first event in time is David noticed weight gain which is p1 because awareness of a present condition precedes analysis and action so position 1 is p1.",
      "position":"1"
    }},
    {{
      "id":"p2",
      "original_phrase":"David examined his habits for a reason",
      "rationale":"After this the next event is David examined his habits which is p2 because investigation follows noticing so position 2 is p2.",
      "position":"2"
    }},
    {{
      "id":"p3",
      "original_phrase":"David Realized he ate too much fast food",
      "rationale":"After this the next event is David realized he ate too much fast food which is p3 because realization follows analysis so position 3 is p3.",
      "position":"3"
    }},
    {{
      "id":"p4",
      "original_phrase":"David Stopped going to burger places",
      "rationale":"After this the next event is David stopped going to burger places which is p4 because actions follow realization so position 4 is p4.",
      "position":"4"
    }},
    {{
      "id":"p5",
      "original_phrase":"David Started a vegetarian diet",
      "rationale":"After this the next event is David started a vegetarian diet which is p5 because adopting a new plan follows stopping so position 5 is p5.",
      "position":"5"
    }},
    {{
      "id":"p6",
      "original_phrase":"David Felt better after a few weeks",
      "rationale":"Finally the last event is David felt better after a few weeks which is p6 because the time marker after a few weeks places the outcome last so position 7 is p6.",
      "position":"7"
    }},
    {{
      "id":"p7",
      "original_phrase":"David had stopped eating unhealthy foods",
      "rationale":"After this the next event is David had stopped eating unhealthy foods which is p7 because consolidation of change precedes delayed outcomes so position 6 is p7.",
      "position":"6"
    }}
  ]
}}
</JSON>

---

**Example 2**
Story:
“I was really upset by my new jacket. I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

Phrases:
[
  {{ "id":"p1","text":"upset by the new jacket" }},
  {{ "id":"p2","text":"I bought a cheap jacket" }},
  {{ "id":"p3","text":"Jacket fell apart the next day" }},
  {{ "id":"p4","text":"I concluded more expensive clothes last longer" }}
]

Output:
<JSON>
{{
  "all_rationale": "The first event in time is I bought a cheap jacket which is p2 because a purchase must occur before any failure or reaction so position 1 is p2. After this the next event is Jacket fell apart the next day which is p3 because the next day places the failure after purchase so position 2 is p3. After this the next event is upset by the new jacket which is p1 because the emotional reaction follows the failure so position 3 is p1. Finally the last event is I concluded more expensive clothes last longer which is p4 because the general lesson follows the reaction so position 4 is p4.",
  "results": [
    {{
      "id":"p1",
      "original_phrase":"upset by the new jacket",
      "rationale":"After this the next event is upset by the new jacket which is p1 because the emotional reaction follows the failure so position 3 is p1.",
      "position":"3"
    }},
    {{
      "id":"p2",
      "original_phrase":"I bought a cheap jacket",
      "rationale":"The first event in time is I bought a cheap jacket which is p2 because a purchase must occur before any failure or reaction so position 1 is p2.",
      "position":"1"
    }},
    {{
      "id":"p3",
      "original_phrase":"Jacket fell apart the next day",
      "rationale":"After this the next event is Jacket fell apart the next day which is p3 because the next day places the failure after purchase so position 2 is p3.",
      "position":"2"
    }},
    {{
      "id":"p4",
      "original_phrase":"I concluded more expensive clothes last longer",
      "rationale":"Finally the last event is I concluded more expensive clothes last longer which is p4 because the general lesson follows the reaction so position 4 is p4.",
      "position":"4"
    }}
  ]
}}
</JSON>

---

### Your Turn

#### Input Format
Story:
{story}

Phrases:
{phrases}



#### Remember
- Decide by **story-time**, not narration order.
- In **all_rationale**, write exactly N sentences. Each must end with **so position k is pX.** and use **periods only**. **No commas or semicolons.**
- Keep **results** in **input ID order** (p1, p2, …).
- Extract each event’s position from **all_rationale**.
- **Every phrase must appear exactly once in all_rationale.**
- The **position** value must be inside quotes, e.g. `"position":"3"`.

Output: A single JSON object exactly matching the schema described in Output Format.

Return ONLY one JSON object. Do not output anything before or after it.
Wrap the JSON object inside <JSON> ... </JSON> tags.
Provide output in the following format:

<JSON>
{{
  "all_rationale": "...",
  "results": [
    {{
      "id":"p1",
      "original_phrase":"...",
      "rationale":"...",
      "position":"..."
    }},
    ...
  ]
}}
</JSON>


"""

# prompt_abstraction_extraction25 = """
# ### Role Assignment
# You are an **event-typing and evaluation assistant**.  
# Your job is to read a short **Story** and a list of **Phrases given in temporal order from earliest to latest**, then for **each phrase** assign:
# 1) an **Event Type** from **STATE**, **ACTION**, **OUTCOME**, and  
# 2) an **Evaluation** label that is **compatible with the chosen Event Type**.

# ### Temporal Setting
# - **All phrases are already ordered in time** from the earliest event to the latest event.  
# - Use this order only as a **candidate-cause filter**: when checking dependence, a phrase may depend **only on earlier phrases**.  
# - **Do not assume that “after” means “because.”** Temporal sequence narrows candidates but does not by itself establish causality.

# ### Task Definition
# Apply these rules **independently per phrase** using the **whole story context**.  
# Narrative order does **not** determine causality, but temporal ordering of phrases helps restrict candidates.  
# Always answer with **evidence-first** reasoning grounded in the story text.

# #### Step 1 — Decide ACTION vs non-ACTION
# - If the phrase foregrounds a controllable **doing** or an **initiated change** by an agent → label **ACTION**.
#   - Diagnostics for **ACTION** must be explicitly checked:
#     - **Main verb controllability test**: name the main verb and confirm an agent can intentionally perform it and that it can be phrased as a command.
#     - **Agent presence test**: identify the agent if stated or clearly implied by the phrase.
#   - Treat **initiation and cessation verbs** as actions even in perfect aspect: e.g., “started…”, “stopped…”, “had stopped…”, “began…”, “quit…”. These encode **agent-initiated change**, so they pass the controllability test and should not be mislabeled as STATE.
#   - Not ACTION: non-agentive happenings. States, statuses, or beliefs presented as results.

# #### Step 2 — If not ACTION, decide STATE vs OUTCOME (order-agnostic but candidate-limited by time)
# - **STATE**: a condition that stands **on its own** in the story and **does not depend on any earlier explicitly stated event** to be interpretable. It remains fully interpretable if all other sentences were deleted.
# - **OUTCOME**: a **resulting condition or belief** whose interpretation **requires** pointing to at least one **earlier** **explicitly stated** event in the story world. You must be able to **name** that earlier event in your rationale and explain why the current phrase depends on it.  
# - **When unsure after tests, default to STATE.** Do not promote to OUTCOME using world knowledge alone.

# > Notes on beliefs and lessons:  
# > - Verbs that encode acquired beliefs are **OUTCOME** **only if** the belief **depends on** a specific earlier event you can name.  
# > - Emotions without a named prior event are **STATE**; with a clear prior event they become **OUTCOME**.  
# > - Temporal markers narrow order but do **not** by themselves force OUTCOME.

# ### Evaluation Mapping
# Choose **exactly one** evaluation from the allowed set for the chosen type:

# - **STATE →**
#   - Positive: **EASE** — indicates comfort or stability or relief.
#   - Negative: **STRUGGLE** — indicates difficulty or pain or burden.
#   - Neutral: **NONE** — purely descriptive without a positive or negative tilt.

# - **ACTION →**
#   - Active (Positive): **EFFORT** — the act is goal directed and attempts to solve a problem or improve a situation.
#   - Passive (Negative): **INDIFFERENCE** — the act neglects the problem or worsens it or ignores obvious risks.
#   - Neutral: **NONE** — the act is routine or descriptive with no clear helpfulness or harm.
#   - *Note:* Classify **the act itself**, **not** its downstream results.

# - **OUTCOME →**
#   - Positive: **GAIN** — the resulting state improves wellbeing or knowledge or resources or function.
#   - Negative: **LOSS** — the resulting state reduces wellbeing or knowledge or resources or function.
#   - Neutral: **NONE** — mixed or unclear impact.  
#   - *Notes on beliefs and lessons:*  
#     - If the belief or realization primarily **exposes harm or deficit** in the situation or self understanding, label **LOSS**.  
#     - If the belief or realization **equips corrective knowledge** or explicitly increases capability for better choices, label **GAIN**.  
#     - If the takeaway is generic and not framed as helpful or harmful, label **NONE**.

# ### Evidence and Discipline Requirements
# Use the **rationale format** and keep decisions auditable and grounded.

# #### Rationale Format (exactly four segments per phrase)
# Write a single-line rationale per segment, separated by periods, using the exact titles below and **no extra punctuation like semicolons**.

# - **Position and previous summary:** State “Position P{{n}}”. Then write: “Summary P1–P{{n-1}}: {{≤25 words}}”. The summary must be **extractive and compact**, drawing strictly from the story phrasing and earlier phrases, not invented inferences. Use only:
#   - **Quoted spans from previous events**.
#   - **Chain compression**: a → b → c.
#   - **Milestone cue quotes**.
#   The summary must **not** use ellipses or placeholders and must contain the full content within the word cap.

# - **Action Decision:** Decide ACTION or non-action and justify with the controllability test, the agent presence test, and a possible command form.

# - **State vs Outcome Decision:**  
#   - If ACTION: say “It is an action so this step is not applicable.”  
#   - If not ACTION: first **review the summary** and explain clearly **why** the new event is **dependent** on earlier events **or** **independent** of them; explicitly point to the relevant parts of the summary in your reason; then state the final label.  
#     - Dependence form: “This event is about {{brief description of current event}}. The summary shows {{named piece(s) from the summary}} which this event presupposes or results from. Because this linkage is required for interpretation, label **OUTCOME**.”  
#     - Independence form: “This event is about {{brief description of current event}}. The summary elements are not required to interpret this as a standalone condition. Therefore label **STATE**.”

# - **Evaluation:** Provide **reason-first evaluation** that:  
#   1) States the **apparent valence** of the current event in plain terms.  
#   2) **References the summary** to compare earlier status with the current event and explains how the new event **extends the timeline**.  
#   3) Names the **impact dimension** (wellbeing or knowledge or resources or function) and the **direction** of change.  
#   4) Ends with the label.  
#   **Hedging words** like “might” or “potentially” are not allowed unless the story is explicitly mixed; choose a firm polarity or NONE when truly unclear.  
#   - Form: “This event appears {{positive|negative|neutral}} given the story. From the summary we see {{prior state or process}} and this event adds {{what it adds}}. This affects {{dimension}} and it {{increases|decreases|does not clearly change}}. Therefore **{{EASE|STRUGGLE|NONE|EFFORT|INDIFFERENCE|GAIN|LOSS}}**.”

# ### Output Format
# Return a single JSON object wrapped in **<JSON> ... </JSON>** tags with a top-level **results** array. For each phrase include:
# - **id**: the phrase identifier from input.
# - **original_phrase**: the exact phrase text from input.
# - **rationale**: a single string containing the four segments in this order and wording:
#   - `Position and previous summary: ... . Action Decision: ... . State vs Outcome Decision: ... . Evaluation: ... .`
# - **event_type**: The type of the event, one of "ACTION", "STATE", "OUTCOME".
# - **evaluation**: The evaluation for each event. If it is STATE, then one of "EASE", "STRUGGLE", "NONE"; if it is an ACTION, then one of the "EFFORT", "INDIFFERENCE", "NONE"; if it is an OUTCOME, then one of the "GAIN", "LOSS", "NONE".

# ---

# ### Examples

# **Example 1**

# Story:  
# “David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.”

# Phrases:  
# [
#   {{ "id":"p1","text":"David noticed weight gain" }},
#   {{ "id":"p2","text":"David examined his habits for a reason" }},
#   {{ "id":"p3","text":"David Realized he ate too much fast food" }},
#   {{ "id":"p4","text":"David Stopped going to burger places" }},
#   {{ "id":"p5","text":"David Started a vegetarian diet" }},
#   {{ "id":"p7","text":"David had stopped eating unhealthy foods" }},
#   {{ "id":"p6","text":"David Felt better after a few weeks" }}
# ]

# Output:
# <JSON>
# {{
#   "results": [
#     {{
#       "id": "p1",
#       "original_phrase": "David noticed weight gain",
#       "rationale": "Position and previous summary: Position P1. Summary P1–P0: none. Action Decision: Non-action because the main verb notice is not controllable on command and awareness cannot be ordered. State vs Outcome Decision: This event is about recognizing weight gain and there are no earlier events so the recognition stands on its own without required dependence; therefore label STATE. Evaluation: This recognition signals a burdensome health status relative to no prior context and adds an initial problem to the timeline; this affects wellbeing and it decreases; therefore STRUGGLE.",
#       "event_type": "STATE",
#       "evaluation": "STRUGGLE"
#     }},
#     {{
#       "id": "p2",
#       "original_phrase": "David examined his habits for a reason",
#       "rationale": "Position and previous summary: Position P2. Summary P1–P1: noticed weight gain. Action Decision: ACTION because examine is controllable and can be commanded as examine your habits with David as agent. State vs Outcome Decision: It is an action so this step is not applicable. Evaluation: This act targets problem-solving after noticing weight gain and advances the timeline from recognition to investigation; this affects knowledge and it increases; therefore EFFORT.",
#       "event_type": "ACTION",
#       "evaluation": "EFFORT"
#     }},
#     {{
#       "id": "p3",
#       "original_phrase": "David Realized he ate too much fast food",
#       "rationale": "Position and previous summary: Position P3. Summary P1–P2: noticed weight gain → examined his habits for a reason. Action Decision: Non-action because realize reports adoption of a belief not directly controllable on command. State vs Outcome Decision: This event is about recognizing excessive fast food intake and the summary shows prior noticing and examining which this belief presupposes to count as a result; because this linkage is required for interpretation label OUTCOME. Evaluation: This realization exposes a harmful mistake in diet and extends the timeline by yielding a concrete diagnosis after investigation; this affects knowledge and it increases while revealing deficit; therefore LOSS.",
#       "event_type": "OUTCOME",
#       "evaluation": "LOSS"
#     }},
#     {{
#       "id": "p4",
#       "original_phrase": "David Stopped going to burger places",
#       "rationale": "Position and previous summary: Position P4. Summary P1–P3: noticed weight gain → examined habits → realized too much fast food. Action Decision: ACTION because stop going is controllable and can be commanded as stop going to burger places with David as agent. State vs Outcome Decision: It is an action so this step is not applicable. Evaluation: This step is a corrective behavioral shift following diagnosis and it moves the timeline into intervention; this affects wellbeing and expected risk and it increases protective behavior; therefore EFFORT.",
#       "event_type": "ACTION",
#       "evaluation": "EFFORT"
#     }},
#     {{
#       "id": "p5",
#       "original_phrase": "David Started a vegetarian diet",
#       "rationale": "Position and previous summary: Position P5. Summary P1–P4: noticed weight gain → examined habits → realized too much fast food → stopped going to burger places. Action Decision: ACTION because start is controllable and can be commanded as start a vegetarian diet with David as agent. State vs Outcome Decision: It is an action so this step is not applicable. Evaluation: This begins a healthier regimen that deepens the intervention phase and extends the timeline toward sustained change; this affects wellbeing and it increases; therefore EFFORT.",
#       "event_type": "ACTION",
#       "evaluation": "EFFORT"
#     }},
#     {{
#       "id": "p7",
#       "original_phrase": "David had stopped eating unhealthy foods",
#       "rationale": "Position and previous summary: Position P6. Summary P1–P5: noticed weight gain → examined habits → realized too much fast food → stopped going to burger places → started a vegetarian diet. Action Decision: ACTION because stop eating is controllable and can be commanded as stop eating unhealthy foods with David as implied agent. State vs Outcome Decision: It is an action so this step is not applicable. Evaluation: This maintains abstinence as an ongoing practice and advances the timeline into maintenance; this affects wellbeing and it increases protective consistency; therefore EFFORT.",
#       "event_type": "ACTION",
#       "evaluation": "EFFORT"
#     }},
#     {{
#       "id": "p6",
#       "original_phrase": "David Felt better after a few weeks",
#       "rationale": "Position and previous summary: Position P7. Summary P1–P6: noticed weight gain → examined habits → realized too much fast food → stopped going to burger places → started a vegetarian diet → had stopped eating unhealthy foods. Action Decision: Non-action because feel better is a state description and cannot be commanded. State vs Outcome Decision: This event is about feeling better after some time and the summary shows problem recognition followed by dietary changes that this improvement presupposes as its basis; because these earlier changes are required to interpret the improvement as a result label OUTCOME. Evaluation: This improvement is clearly positive relative to the earlier problem and adds a recovery milestone after sustained change; this affects wellbeing and it increases; therefore GAIN.",
#       "event_type": "OUTCOME",
#       "evaluation": "GAIN"
#     }}
#   ]
# }}
# </JSON>

# ---

# **Example 2**

# Story:  
# “I was really upset by my new jacket. I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

# Phrases (already in temporal order):  
# [
#   {{ "id":"p1","text":"I bought a cheap jacket" }},
#   {{ "id":"p2","text":"Jacket fell apart the next day" }},
#   {{ "id":"p3","text":"upset by the new jacket" }},
#   {{ "id":"p4","text":"I concluded more expensive clothes last longer" }}
# ]

# Output:
# <JSON>
# {{
#   "results": [
#     {{
#       "id": "p1",
#       "original_phrase": "I bought a cheap jacket",
#       "rationale": "Position and previous summary: Position P1. Summary P1–P0: none. Action Decision: ACTION because buy is controllable and can be commanded as buy a jacket with the narrator as agent. State vs Outcome Decision: It is an action so this step is not applicable. Evaluation: This purchase chooses very low cost despite risk and begins the timeline with a questionable choice; this affects resources and expected durability and it decreases prudent value; therefore INDIFFERENCE.",
#       "event_type": "ACTION",
#       "evaluation": "INDIFFERENCE"
#     }},
#     {{
#       "id": "p2",
#       "original_phrase": "Jacket fell apart the next day",
#       "rationale": "Position and previous summary: Position P2. Summary P1–P1: bought a cheap jacket. Action Decision: Non-action because fall apart is a non-agentive happening not commandable. State vs Outcome Decision: This event is about the jacket failing and the summary shows a jacket was purchased which this failure presupposes to be meaningful; because that earlier purchase is required to interpret the loss label OUTCOME. Evaluation: The failure removes function and wastes the prior spend and advances the timeline from purchase to breakdown; this affects resources and function and both decrease; therefore LOSS.",
#       "event_type": "OUTCOME",
#       "evaluation": "LOSS"
#     }},
#     {{
#       "id": "p3",
#       "original_phrase": "upset by the new jacket",
#       "rationale": "Position and previous summary: Position P3. Summary P1–P2: bought a cheap jacket → jacket fell apart the next day. Action Decision: Non-action because being upset is an emotional state and not controllable on command. State vs Outcome Decision: This event is about feeling upset related to the new jacket and the summary shows the failure which this reaction presupposes to count as a result; because that linkage is required label OUTCOME. Evaluation: The reaction reflects reduced emotional wellbeing following the failure and extends the timeline into emotional impact; this affects wellbeing and it decreases; therefore LOSS.",
#       "event_type": "OUTCOME",
#       "evaluation": "LOSS"
#     }},
#     {{
#       "id": "p4",
#       "original_phrase": "I concluded more expensive clothes last longer",
#       "rationale": "Position and previous summary: Position P4. Summary P1–P3: bought a cheap jacket → jacket fell apart → upset by the new jacket. Action Decision: Non-action because conclude reports adoption of a belief not commandable. State vs Outcome Decision: This event is about forming a general rule and the summary shows a cheap purchase and a failure which this belief presupposes as its evidential basis; because those are required to interpret the conclusion as a result label OUTCOME. Evaluation: The belief provides corrective guidance after a loss and moves the timeline from harm to lesson; this affects knowledge and it increases; therefore GAIN.",
#       "event_type": "OUTCOME",
#       "evaluation": "GAIN"
#     }}
#   ]
# }}
# </JSON>

# ---

# ### Your Turn

# #### Input Format
# Story:
# {story}

# Phrases (already in temporal order):
# {phrases}

# ### Remember
# - Causality is **order-agnostic** but **time-order filters candidates** to **earlier phrases only**.  
# - **Doing present → ACTION**. If not, choose **STATE** or **OUTCOME** by whether interpretation **requires** a **named earlier event** referenced from the summary.  
# - Use the **four-part Rationale** and provide concrete justification when claiming dependence; **name earlier events via the summary**, not by IDs alone.  
# - The **Position and previous summary** must be **extractive and compact**, must not use ellipses or placeholders, and must stay within the word cap while drawing strictly from prior story phrasing and phrases.  
# - **Evaluation must be reason-first**: state valence, reference the summary to compare earlier and current status, name the impact dimension and direction, and only then give the label; avoid hedging unless the story is explicitly mixed.  
# - **Emotions and beliefs** become **OUTCOME** only when they **depend** on a specific earlier event you can name from the summary; otherwise they are **STATE**.  
# - **Initiation and cessation verbs** including perfect aspects are **ACTION** when an agent is present or implied.  
# - **Temporal markers** alone do not force OUTCOME; they only restrict candidate causes.  
# - Apply the **conservative default**: if ACTION is ruled out and dependence is not required, choose **STATE**.  

# Output: A single JSON object exactly matching the schema described in Output Format.

# Return ONLY one JSON object. Do not output anything before or after it.
# Wrap the JSON object inside <JSON> ... </JSON> tags.
# Provide output in the following format:

# <JSON>
# {{
#   "results": [
#     {{
#       "id":"p1",
#       "original_phrase":"...",
#       "rationale":"...",
#       "event_type":"...",
#       "evaluation":"..."
#     }},
#     ...
#   ]
# }}
# </JSON>



# """

# prompt_abstraction_extraction25 = """

# ### Role Assignment
# You are an **event-typing assistant**.  
# Your task is to read a short **Story** and a list of **Phrases given in temporal order from earliest to latest**, then determine for **each phrase** whether it is a **STATE**, an **ACTION**, or an **OUTCOME**.

# ---

# ### Task Definition
# You will produce a **two-part output**:
# 1) **all_rationale** — a single string containing **exactly N sentences** that sequentially analyze the phrases in their given order and assign a label to each.  
# 2) **results** — an array of per-phrase objects with fields **id**, **original_phrase**, **rationale**, and **event_type** in the **original input ID order** (p1 then p2 then p3 and so on).

# Work from the **main person’s perspective** and reason **step by step** across the whole story.

# ---

# ### Perspective Rule
# - **Infer the main person** from the story and phrases. Prefer first person I if present else a recurring named or pronominal subject else the most central entity across phrases. Keep this choice **consistent** across all phrases.
# - **ACTION is reserved for doings by the main person**. If someone else acts that phrase is **non ACTION** and must be typed as **STATE** or **OUTCOME** from the main person’s perspective.

# ---

# ### Core Definitions
# - **ACTION**: a **new doing or initiated change by the main person** that is intentionally controllable and can be phrased as a command to them. Initiation and cessation verbs count as ACTION when controlled by the main person.
# - **STATE**: a **new situation or a continuation or description of the current situation** for the main person that is **interpretable on its own** without requiring an earlier explicit event.
# - **OUTCOME**: a **lesson or belief or new situation that happens because of earlier event or events**. Interpretation **requires** naming at least one **earlier explicit** phrase that it depends on.

# **Conservative default:** If a phrase is not an ACTION and its interpretation does **not** require an earlier event choose **STATE**.  
# **Order constraint:** A phrase may **depend only** on **earlier** phrases. Do **not** assume after means because and when you choose **OUTCOME** you must **name** the specific earlier phrase or phrases.

# ---

# ### Mandatory Two Step Decision
# For **every** phrase follow this strict order within the one sentence:

# **Step A — Action check first**
# - State explicitly whether the phrase is an **ACTION** by the main person or **not an action**.  
# - Use controllability and agent tests. If it is an ACTION end the reasoning and give the label.

# **Step B — Only if not an action run dependence tests**
# - **Deletion Test:** If all earlier phrases were removed would this phrase still be fully interpretable in the same way. If no then it is OUTCOME and you must name the earlier phrase or phrases that are required.  
# - **Minimal cause set:** For OUTCOME list the **fewest** earlier phrases that jointly support the result and explain why each is needed.  
# - **Counterfactual flip:** Explicitly state whether this event would still hold in the same way if the named earlier events had not occurred or had occurred differently and if not then label OUTCOME.  
# - **Milestone dependency:** Phrases that encode milestones or statuses that presuppose an initiator event are OUTCOME when that initiator appears earlier.  
# - If none of these force dependence and the phrase stands alone then label STATE.

# Your one sentence must reflect Step A and, when applicable, Step B.

# ---

# ### Rationale Style and Generation Procedure
# Produce **all_rationale** as **exactly N sentences** one per input phrase using **periods only**. **Do not use commas or semicolons** inside these sentences. No ellipses.

# Each sentence must be **reason first then conclusion** and must end with **so label TYPE for pX.** Use these exact openers and structure:

# - **For the first phrase:**  
#   **The first phrase is {{quote the phrase text minimally}} which is about {{what the phrase describes}} so {{it is an action by the main person because {{brief controllability and agent reason}} or it is not an action because {{brief reason}}}} and {{if not an action then state the Deletion Test result and the Minimal cause set if any and the Counterfactual flip in one compact claim or state that it stands alone}} so label {{STATE or ACTION or OUTCOME}} for pX.**

# - **For each subsequent phrase:**  
#   **After {{list all previous IDs as p1 and p2 and p3 up to p{{X-1}}}} the next phrase is {{quote the phrase text minimally}} which is about {{what the phrase describes}} so {{it is an action by the main person because {{brief controllability and agent reason}} or it is not an action because {{brief reason}}}} and {{if not an action then apply the Deletion Test and name the Minimal cause set and perform the Counterfactual flip or state that it stands alone}} so label {{STATE or ACTION or OUTCOME}} for pX.**

# In the single sentence for each phrase you must explicitly state:
# 1) **What this phrase is about** in extractive wording.  
# 2) **Step A result**: action vs not action with a short justification.  
# 3) **Step B details** when non action: Deletion Test outcome and Minimal cause set and Counterfactual flip or explicit independence.  
# 4) **Your final label** in **uppercase** from {{STATE ACTION OUTCOME}} with the closing words **so label TYPE for pX.**

# Keep language **extractive and compact**. Draw strictly from the story phrasing and earlier phrases. Do **not** invent facts.

# ---

# ### Building the Results
# After writing **all_rationale**:
# 1) Iterate the phrases in the **original input ID order**.  
# 2) For each phrase:
#    - Set **rationale** to the **exact sentence** from **all_rationale** that analyzes that phrase.  
#    - Set **event_type** to the final TYPE named in that sentence.  
#    - Keep all key–value pairs on separate lines.

# ---

# ### Output Format
# Return a single JSON object wrapped in **<JSON> ... </JSON>** tags with two top level keys **all_rationale** and **results**.

# #### Keys Description
# - **all_rationale**: a single string with **exactly N sentences** each following the format above and each ending with **so label TYPE for pX.**  
# - **results**: an array of N objects in **input ID order**. Each object has:
#   - **id**: the phrase ID like "p1".  
#   - **original_phrase**: the exact phrase text.  
#   - **rationale**: the sentence from **all_rationale** for this phrase.  
#   - **event_type**: one of "STATE" "ACTION" "OUTCOME".

# ---

# ### Examples

# **Example 1**

# Story:
# “I noticed I had put on weight. I examined my habits. I realized I was eating too much fast food. I stopped going to burger places. I started a vegetarian diet. After a few weeks I felt better.”

# Phrases:
# [
#   {{ "id":"p1","text":"David noticed weight gain" }},
#   {{ "id":"p2","text":"David examined his habits for a reason" }},
#   {{ "id":"p3","text":"David Realized he ate too much fast food" }},
#   {{ "id":"p4","text":"David Stopped going to burger places" }},
#   {{ "id":"p5","text":"David Started a vegetarian diet" }},
#   {{ "id":"p6","text":"David had stopped eating unhealthy foods" }},
#   {{ "id":"p7","text":"David Felt better after a few weeks" }}
# ]

# Output:
# <JSON>
# {{
#   "all_rationale": "The first phrase is David noticed weight gain which is about recognizing a new condition so it is not an action because noticing is awareness not a controllable doing and with no earlier phrases the Deletion Test shows it stands alone as a status so label STATE for p1. After p1 the next phrase is David examined his habits for a reason which is about investigating the problem so it is an action by the main person because examine can be commanded and David is the agent so label ACTION for p2. After p1 and p2 the next phrase is David Realized he ate too much fast food which is about adopting a belief about diet so it is not an action because realize is not commandable and the Deletion Test fails without David noticed weight gain and David examined his habits and the Counterfactual flip shows if those earlier events were absent or different this belief would not arise the same way so label OUTCOME for p3. After p1 and p2 and p3 the next phrase is David Stopped going to burger places which is about choosing cessation so it is an action by the main person because stop going is controllable and David is the agent so label ACTION for p4. After p1 and p2 and p3 and p4 the next phrase is David Started a vegetarian diet which is about initiating a regimen so it is an action by the main person because start a diet is controllable and David is the agent so label ACTION for p5. After p1 and p2 and p3 and p4 and p5 the next phrase is David had stopped eating unhealthy foods which is about maintained abstinence so it is an action by the main person because it encodes a deliberate cessation under his control so label ACTION for p6. After p1 and p2 and p3 and p4 and p5 and p6 the next phrase is David Felt better after a few weeks which is about improved feeling over time so it is not an action because feeling is not commandable and the Deletion Test fails without David Stopped going to burger places and David Started a vegetarian diet and David had stopped eating unhealthy foods and the Counterfactual flip shows if those earlier changes were absent or different the improvement would not hold the same way so label OUTCOME for p7.",
#   "results": [
#     {{
#       "id":"p1",
#       "original_phrase":"David noticed weight gain",
#       "rationale":"The first phrase is David noticed weight gain which is about recognizing a new condition so it is not an action because noticing is awareness not a controllable doing and with no earlier phrases the Deletion Test shows it stands alone as a status so label STATE for p1.",
#       "event_type":"STATE"
#     }},
#     {{
#       "id":"p2",
#       "original_phrase":"David examined his habits for a reason",
#       "rationale":"After p1 the next phrase is David examined his habits for a reason which is about investigating the problem so it is an action by the main person because examine can be commanded and David is the agent so label ACTION for p2.",
#       "event_type":"ACTION"
#     }},
#     {{
#       "id":"p3",
#       "original_phrase":"David Realized he ate too much fast food",
#       "rationale":"After p1 and p2 the next phrase is David Realized he ate too much fast food which is about adopting a belief about diet so it is not an action because realize is not commandable and the Deletion Test fails without David noticed weight gain and David examined his habits and the Counterfactual flip shows if those earlier events were absent or different this belief would not arise the same way so label OUTCOME for p3.",
#       "event_type":"OUTCOME"
#     }},
#     {{
#       "id":"p4",
#       "original_phrase":"David Stopped going to burger places",
#       "rationale":"After p1 and p2 and p3 the next phrase is David Stopped going to burger places which is about choosing cessation so it is an action by the main person because stop going is controllable and David is the agent so label ACTION for p4.",
#       "event_type":"ACTION"
#     }},
#     {{
#       "id":"p5",
#       "original_phrase":"David Started a vegetarian diet",
#       "rationale":"After p1 and p2 and p3 and p4 the next phrase is David Started a vegetarian diet which is about initiating a regimen so it is an action by the main person because start a diet is controllable and David is the agent so label ACTION for p5.",
#       "event_type":"ACTION"
#     }},
#     {{
#       "id":"p6",
#       "original_phrase":"David had stopped eating unhealthy foods",
#       "rationale":"After p1 and p2 and p3 and p4 and p5 the next phrase is David had stopped eating unhealthy foods which is about maintained abstinence so it is an action by the main person because it encodes a deliberate cessation under his control so label ACTION for p6.",
#       "event_type":"ACTION"
#     }},
#     {{
#       "id":"p7",
#       "original_phrase":"David Felt better after a few weeks",
#       "rationale":"After p1 and p2 and p3 and p4 and p5 and p6 the next phrase is David Felt better after a few weeks which is about improved feeling over time so it is not an action because feeling is not commandable and the Deletion Test fails without David Stopped going to burger places and David Started a vegetarian diet and David had stopped eating unhealthy foods and the Counterfactual flip shows if those earlier changes were absent or different the improvement would not hold the same way so label OUTCOME for p7.",
#       "event_type":"OUTCOME"
#     }}
#   ]
# }}
# </JSON>

# ---

# **Example 2**

# Story:
# “I was really upset by my new jacket. I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

# Phrases:
# [
#   {{ "id":"p1","text":"I bought a cheap jacket" }},
#   {{ "id":"p2","text":"Jacket fell apart the next day" }},
#   {{ "id":"p3","text":"upset by the new jacket" }},
#   {{ "id":"p4","text":"I concluded more expensive clothes last longer" }}
# ]

# Output:
# <JSON>
# {{
#   "all_rationale": "The first phrase is I bought a cheap jacket which is about making a purchase so it is an action by the main person because buy can be commanded and I am the agent so label ACTION for p1. After p1 the next phrase is Jacket fell apart the next day which is about the item failing so it is not an action because the jacket fails without the main person controlling it and the Deletion Test fails without I bought a cheap jacket and the Counterfactual flip shows if the jacket had not been bought this failure would not be stated this way so label OUTCOME for p2. After p1 and p2 the next phrase is upset by the new jacket which is about an emotional reaction so it is not an action because being upset is not commandable and the Deletion Test fails without Jacket fell apart the next day and the Counterfactual flip shows if the jacket had not failed the upset would not hold the same way so label OUTCOME for p3. After p1 and p2 and p3 the next phrase is I concluded more expensive clothes last longer which is about adopting a belief so it is not an action because conclude is not commandable and the Deletion Test fails without I bought a cheap jacket and Jacket fell apart the next day and the Counterfactual flip shows if the jacket had been expensive or had lasted the belief would not arise the same way so label OUTCOME for p4.",
#   "results": [
#     {{
#       "id":"p1",
#       "original_phrase":"I bought a cheap jacket",
#       "rationale":"The first phrase is I bought a cheap jacket which is about making a purchase so it is an action by the main person because buy can be commanded and I am the agent so label ACTION for p1.",
#       "event_type":"ACTION"
#     }},
#     {{
#       "id":"p2",
#       "original_phrase":"Jacket fell apart the next day",
#       "rationale":"After p1 the next phrase is Jacket fell apart the next day which is about the item failing so it is not an action because the jacket fails without the main person controlling it and the Deletion Test fails without I bought a cheap jacket and the Counterfactual flip shows if the jacket had not been bought this failure would not be stated this way so label OUTCOME for p2.",
#       "event_type":"OUTCOME"
#     }},
#     {{
#       "id":"p3",
#       "original_phrase":"upset by the new jacket",
#       "rationale":"After p1 and p2 the next phrase is upset by the new jacket which is about an emotional reaction so it is not an action because being upset is not commandable and the Deletion Test fails without Jacket fell apart the next day and the Counterfactual flip shows if the jacket had not failed the upset would not hold the same way so label OUTCOME for p3.",
#       "event_type":"OUTCOME"
#     }},
#     {{
#       "id":"p4",
#       "original_phrase":"I concluded more expensive clothes last longer",
#       "rationale":"After p1 and p2 and p3 the next phrase is I concluded more expensive clothes last longer which is about adopting a belief so it is not an action because conclude is not commandable and the Deletion Test fails without I bought a cheap jacket and Jacket fell apart the next day and the Counterfactual flip shows if the jacket had been expensive or had lasted the belief would not arise the same way so label OUTCOME for p4.",
#       "event_type":"OUTCOME"
#     }}
#   ]
# }}
# </JSON>

# ---

# ### Your Turn

# #### Input Format
# Story:
# {story}

# Phrases:
# {phrases}

# #### Remember
# - Work from the **main person’s perspective** and keep it consistent.  
# - **ACTION only if** the main person performs a **new doing or initiated change**.  
# - Always do **Step A** first in the sentence and only if not an action run **Step B** with the Deletion Test and Minimal cause set and Counterfactual flip and Milestone dependency.  
# - Use **periods only** in **all_rationale**. **No commas or semicolons**. **No ellipses**.  
# - In each subsequent sentence list **all** earlier IDs exactly as p1 and p2 and p3 style with the word **and** between them and no commas.  
# - The **results** array must follow the **input ID order**.  
# - Do not include any evaluation or sentiment labels.


# Output: A single JSON object exactly matching the schema described in Output Format.

# Return ONLY one JSON object. Do not output anything before or after it.
# Wrap the JSON object inside <JSON> ... </JSON> tags.
# Provide output in the following format:

# <JSON>
# {{
#   "results": [
#     {{
#       "id":"p1",
#       "original_phrase":"...",
#       "rationale":"...",
#       "event_type":"..."
#     }},
#     ...
#   ]
# }}
# </JSON>


# """

prompt_abstraction_extraction25 = """

### Role Assignment
You are an **event-typing assistant**.  
Your task is to read a short **Story** and a list of **Phrases given in temporal order from earliest to latest**, then determine for **each phrase** whether it is a **STATE**, an **ACTION**, or an **OUTCOME**.

---

### Task Definition
You will produce a **two-part output**:
1) **all_rationale** — a single string containing **exactly N sentences** that sequentially analyze the phrases in their given order and assign a label to each.  
2) **results** — an array of per-phrase objects with fields **id**, **original_phrase**, **rationale**, and **event_type** in the **original input ID order** (p1 then p2 then p3 and so on).

Work from the **main person’s perspective** and reason **step by step** across the whole story.

---

### Perspective Rule
- **Infer the main person** from the story and phrases. Prefer first person I if present else a recurring named or pronominal subject else the most central entity across phrases. Keep this choice **consistent** across all phrases.
- **ACTION is reserved for doings by the main person**. If someone else acts that phrase is **non ACTION** and must be typed as **STATE** or **OUTCOME** from the main person’s perspective.

---

### Core Definitions
- **ACTION**: a **new doing or initiated change by the main person** that is intentionally controllable and can be phrased as a command to them. Initiation and cessation verbs count as ACTION when controlled by the main person.
- **STATE**: a **new situation or a continuation or description of the current situation** for the main person that is **interpretable on its own** without requiring an earlier explicit event.
- **OUTCOME**: a **lesson or belief or new situation that happens because of earlier event or events**. Interpretation **requires** naming at least one **earlier explicit** phrase that it depends on.

**Conservative default:** If a phrase is not an ACTION and its interpretation does **not** require an earlier event choose **STATE**.  
**Order constraint:** A phrase may **depend only** on **earlier** phrases. Do **not** assume after means because and when you choose **OUTCOME** you must **name** the specific earlier phrase or phrases.

---

### Mandatory Two Step Decision
For **every** phrase follow this strict order within the one sentence:

**Step A — Action check first**
- State explicitly whether the phrase is an **ACTION** by the main person or **not an action**.  
- Use controllability and agent tests. If it is an ACTION end the reasoning and give the label.

**Step B — Only if not an action run dependence tests**
Run all tests and reflect them in the sentence when the phrase is not an action:

- **Deletion Test:** If all earlier phrases were removed would this phrase still be fully interpretable in the same way. If no then it is OUTCOME and you must name the earlier phrase or phrases that are required.  
- **Minimal cause set:** For OUTCOME list the **fewest** earlier phrases that jointly support the result and explain why each is needed.  
- **Counterfactual flip:** Explicitly state whether this event would still hold in the same way if the named earlier events had not occurred or had occurred differently and if not then label OUTCOME.  
- **Milestone dependency:** Phrases that encode milestones or statuses that presuppose an initiator event are OUTCOME when that initiator appears earlier.  
- **Opposite possibility test:** If under the same earlier context it is reasonable that both this event and its clear opposite could occur then the earlier context does not by itself determine this event and dependence is not forced so prefer STATE unless another required cause is named.

Your one sentence must reflect Step A and, when applicable, Step B.

---

### Rationale Style and Generation Procedure
Produce **all_rationale** as **exactly N sentences** one per input phrase using **periods only**. **Do not use commas or semicolons** inside these sentences. No ellipses.

**Name the main person at the start of the first sentence** before analyzing p1 using short wording like main person is I or main person is David or main person is Lily then proceed with the rest of the first sentence as usual.

Each sentence must be **reason first then conclusion** and must end with **so label TYPE for pX.** Use these exact openers and structure:

- **For the first phrase:**  
  **The first phrase is {{quote the phrase text minimally}} and main person is {{name or pronoun}} which is about {{what the phrase describes}} so {{it is an action by the main person because {{brief controllability and agent reason}} or it is not an action because {{brief reason}}}} and {{if not an action then state the Deletion Test result and the Minimal cause set if any and the Counterfactual flip and the Opposite possibility test or state that it stands alone}} so label {{STATE or ACTION or OUTCOME}} for pX.**

- **For each subsequent phrase:**  
  **After {{list all previous IDs as p1 and p2 and p3 up to p{{X-1}}}} the next phrase is {{quote the phrase text minimally}} which is about {{what the phrase describes}} so {{it is an action by the main person because {{brief controllability and agent reason}} or it is not an action because {{brief reason}}}} and {{if not an action then apply the Deletion Test and name the Minimal cause set and perform the Counterfactual flip and run the Opposite possibility test or state that it stands alone}} so label {{STATE or ACTION or OUTCOME}} for pX.**

In the single sentence for each phrase you must explicitly state:
1) **What this phrase is about** in extractive wording.  
2) **Step A result**: action vs not action with a short justification.  
3) **Step B details** when non action: Deletion Test outcome and Minimal cause set and Counterfactual flip and Opposite possibility test or explicit independence.  
4) **Your final label** in **uppercase** from {{STATE ACTION OUTCOME}} with the closing words **so label TYPE for pX.**

Keep language **extractive and compact**. Draw strictly from the story phrasing and earlier phrases. Do **not** invent facts.

---

### Building the Results
After writing **all_rationale**:
1) Iterate the phrases in the **original input ID order**.  
2) For each phrase:
   - Set **rationale** to the **exact sentence** from **all_rationale** that analyzes that phrase.  
   - Set **event_type** to the final TYPE named in that sentence.  
   - Keep all key–value pairs on separate lines.

---

### Output Format
Return a single JSON object wrapped in **<JSON> ... </JSON>** tags with two top level keys **all_rationale** and **results**.

#### Keys Description
- **all_rationale**: a single string with **exactly N sentences** each following the format above and each ending with **so label TYPE for pX.**  
- **results**: an array of N objects in **input ID order**. Each object has:
  - **id**: the phrase ID like "p1".  
  - **original_phrase**: the exact phrase text.  
  - **rationale**: the sentence from **all_rationale** for this phrase.  
  - **event_type**: one of "STATE" "ACTION" "OUTCOME".

---

### Examples

**Example 1**

Story:
“I noticed I had put on weight. I examined my habits. I realized I was eating too much fast food. I stopped going to burger places. I started a vegetarian diet. After a few weeks I felt better.”

Phrases:
[
  {{ "id":"p1","text":"David noticed weight gain" }},
  {{ "id":"p2","text":"David examined his habits for a reason" }},
  {{ "id":"p3","text":"David Realized he ate too much fast food" }},
  {{ "id":"p4","text":"David Stopped going to burger places" }},
  {{ "id":"p5","text":"David Started a vegetarian diet" }},
  {{ "id":"p6","text":"David had stopped eating unhealthy foods" }},
  {{ "id":"p7","text":"David Felt better after a few weeks" }}
]

Output:
<JSON>
{{
  "all_rationale": "The first phrase is David noticed weight gain and main person is David which is about recognizing a new condition so it is not an action because noticing is awareness not a controllable doing and with no earlier phrases the Deletion Test shows it stands alone as a status and the Opposite possibility test is not needed so label STATE for p1. After p1 the next phrase is David examined his habits for a reason which is about investigating the problem so it is an action by the main person because examine can be commanded and David is the agent so label ACTION for p2. After p1 and p2 the next phrase is David Realized he ate too much fast food which is about adopting a belief about diet so it is not an action because realize is not commandable and the Deletion Test fails without David noticed weight gain and David examined his habits and the Minimal cause set is those two and the Counterfactual flip shows if those earlier events were absent or different this belief would not arise the same way and the Opposite possibility test shows the belief would not hold if habits were not examined so label OUTCOME for p3. After p1 and p2 and p3 the next phrase is David Stopped going to burger places which is about choosing cessation so it is an action by the main person because stop going is controllable and David is the agent so label ACTION for p4. After p1 and p2 and p3 and p4 the next phrase is David Started a vegetarian diet which is about initiating a regimen so it is an action by the main person because start a diet is controllable and David is the agent so label ACTION for p5. After p1 and p2 and p3 and p4 and p5 the next phrase is David had stopped eating unhealthy foods which is about maintained abstinence so it is an action by the main person because it encodes a deliberate cessation under his control so label ACTION for p6. After p1 and p2 and p3 and p4 and p5 and p6 the next phrase is David Felt better after a few weeks which is about improved feeling over time so it is not an action because feeling is not commandable and the Deletion Test fails without David Stopped going to burger places and David Started a vegetarian diet and David had stopped eating unhealthy foods and the Minimal cause set is these dietary changes and the Counterfactual flip shows if those changes were absent or different the improvement would not hold and the Opposite possibility test shows improvement would not arise under unchanged unhealthy eating so label OUTCOME for p7.",
  "results": [
    {{
      "id":"p1",
      "original_phrase":"David noticed weight gain",
      "rationale":"The first phrase is David noticed weight gain and main person is David which is about recognizing a new condition so it is not an action because noticing is awareness not a controllable doing and with no earlier phrases the Deletion Test shows it stands alone as a status and the Opposite possibility test is not needed so label STATE for p1.",
      "event_type":"STATE"
    }},
    {{
      "id":"p2",
      "original_phrase":"David examined his habits for a reason",
      "rationale":"After p1 the next phrase is David examined his habits for a reason which is about investigating the problem so it is an action by the main person because examine can be commanded and David is the agent so label ACTION for p2.",
      "event_type":"ACTION"
    }},
    {{
      "id":"p3",
      "original_phrase":"David Realized he ate too much fast food",
      "rationale":"After p1 and p2 the next phrase is David Realized he ate too much fast food which is about adopting a belief about diet so it is not an action because realize is not commandable and the Deletion Test fails without David noticed weight gain and David examined his habits and the Minimal cause set is those two and the Counterfactual flip shows if those earlier events were absent or different this belief would not arise the same way and the Opposite possibility test shows the belief would not hold if habits were not examined so label OUTCOME for p3.",
      "event_type":"OUTCOME"
    }},
    {{
      "id":"p4",
      "original_phrase":"David Stopped going to burger places",
      "rationale":"After p1 and p2 and p3 the next phrase is David Stopped going to burger places which is about choosing cessation so it is an action by the main person because stop going is controllable and David is the agent so label ACTION for p4.",
      "event_type":"ACTION"
    }},
    {{
      "id":"p5",
      "original_phrase":"David Started a vegetarian diet",
      "rationale":"After p1 and p2 and p3 and p4 the next phrase is David Started a vegetarian diet which is about initiating a regimen so it is an action by the main person because start a diet is controllable and David is the agent so label ACTION for p5.",
      "event_type":"ACTION"
    }},
    {{
      "id":"p6",
      "original_phrase":"David had stopped eating unhealthy foods",
      "rationale":"After p1 and p2 and p3 and p4 and p5 the next phrase is David had stopped eating unhealthy foods which is about maintained abstinence so it is an action by the main person because it encodes a deliberate cessation under his control so label ACTION for p6.",
      "event_type":"ACTION"
    }},
    {{
      "id":"p7",
      "original_phrase":"David Felt better after a few weeks",
      "rationale":"After p1 and p2 and p3 and p4 and p5 and p6 the next phrase is David Felt better after a few weeks which is about improved feeling over time so it is not an action because feeling is not commandable and the Deletion Test fails without David Stopped going to burger places and David Started a vegetarian diet and David had stopped eating unhealthy foods and the Minimal cause set is these dietary changes and the Counterfactual flip shows if those changes were absent or different the improvement would not hold and the Opposite possibility test shows improvement would not arise under unchanged unhealthy eating so label OUTCOME for p7.",
      "event_type":"OUTCOME"
    }}
  ]
}}
</JSON>

---

**Example 2**

Story:
“I was really upset by my new jacket. I bought a cheap jacket for only a dollar. The temperature dropped sharply that night. The jacket fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

Phrases:
[
  {{ "id":"p1","text":"I bought a cheap jacket" }},
  {{ "id":"p2","text":"The temperature dropped sharply that night" }},
  {{ "id":"p3","text":"Jacket fell apart the next day" }},
  {{ "id":"p4","text":"upset by the new jacket" }},
  {{ "id":"p5","text":"I concluded more expensive clothes last longer" }}
]

Output:
<JSON>
{{
  "all_rationale": "The first phrase is I bought a cheap jacket and main person is I which is about making a purchase so it is an action by the main person because buy can be commanded and I am the agent so label ACTION for p1. After p1 the next phrase is The temperature dropped sharply that night which is about a weather condition so it is not an action because weather is not controlled by the main person and the Deletion Test shows it is interpretable without p1 and the Opposite possibility test shows after buying a jacket the night could be warm or cold so dependence is not forced so label STATE for p2. After p1 and p2 the next phrase is Jacket fell apart the next day which is about the item failing so it is not an action because the jacket fails without main person control and the Deletion Test fails without I bought a cheap jacket and the Minimal cause set is that purchase and the Counterfactual flip shows if the purchase had not happened this failure would not be stated and the Opposite possibility test allows that jackets can last but here the stated failure still depends on having the jacket so label OUTCOME for p3. After p1 and p2 and p3 the next phrase is upset by the new jacket which is about an emotional reaction so it is not an action because being upset is not commandable and the Deletion Test fails without Jacket fell apart the next day and the Minimal cause set is that failure and the Counterfactual flip shows if the jacket had not failed the upset would not hold and the Opposite possibility test shows without the failure both upset and not upset are possible but the story ties upset to the failure so label OUTCOME for p4. After p1 and p2 and p3 and p4 the next phrase is I concluded more expensive clothes last longer which is about adopting a belief so it is not an action because conclude is not commandable and the Deletion Test fails without I bought a cheap jacket and Jacket fell apart the next day and the Minimal cause set is those two and the Counterfactual flip shows if the jacket had been expensive or had lasted the belief would not arise the same way and the Opposite possibility test shows that under a non failing purchase both the belief and its opposite are possible so the story requires the failure so label OUTCOME for p5.",
  "results": [
    {{
      "id":"p1",
      "original_phrase":"I bought a cheap jacket",
      "rationale":"The first phrase is I bought a cheap jacket and main person is I which is about making a purchase so it is an action by the main person because buy can be commanded and I am the agent so label ACTION for p1.",
      "event_type":"ACTION"
    }},
    {{
      "id":"p2",
      "original_phrase":"The temperature dropped sharply that night",
      "rationale":"After p1 the next phrase is The temperature dropped sharply that night which is about a weather condition so it is not an action because weather is not controlled by the main person and the Deletion Test shows it is interpretable without p1 and the Opposite possibility test shows after buying a jacket the night could be warm or cold so dependence is not forced so label STATE for p2.",
      "event_type":"STATE"
    }},
    {{
      "id":"p3",
      "original_phrase":"Jacket fell apart the next day",
      "rationale":"After p1 and p2 the next phrase is Jacket fell apart the next day which is about the item failing so it is not an action because the jacket fails without main person control and the Deletion Test fails without I bought a cheap jacket and the Minimal cause set is that purchase and the Counterfactual flip shows if the purchase had not happened this failure would not be stated and the Opposite possibility test allows that jackets can last but here the stated failure still depends on having the jacket so label OUTCOME for p3.",
      "event_type":"OUTCOME"
    }},
    {{
      "id":"p4",
      "original_phrase":"upset by the new jacket",
      "rationale":"After p1 and p2 and p3 the next phrase is upset by the new jacket which is about an emotional reaction so it is not an action because being upset is not commandable and the Deletion Test fails without Jacket fell apart the next day and the Minimal cause set is that failure and the Counterfactual flip shows if the jacket had not failed the upset would not hold and the Opposite possibility test shows without the failure both upset and not upset are possible but the story ties upset to the failure so label OUTCOME for p4.",
      "event_type":"OUTCOME"
    }},
    {{
      "id":"p5",
      "original_phrase":"I concluded more expensive clothes last longer",
      "rationale":"After p1 and p2 and p3 and p4 the next phrase is I concluded more expensive clothes last longer which is about adopting a belief so it is not an action because conclude is not commandable and the Deletion Test fails without I bought a cheap jacket and Jacket fell apart the next day and the Minimal cause set is those two and the Counterfactual flip shows if the jacket had been expensive or had lasted the belief would not arise the same way and the Opposite possibility test shows that under a non failing purchase both the belief and its opposite are possible so the story requires the failure so label OUTCOME for p5.",
      "event_type":"OUTCOME"
    }}
  ]
}}
</JSON>

---

### Your Turn

#### Input Format
Story:
{story}

Phrases:
{phrases}

#### Remember
- Identify and state the **main person** at the start of the first sentence in **all_rationale** and keep it consistent.  
- **ACTION only if** the main person performs a **new doing or initiated change**.  
- Always do **Step A** first in the sentence and only if not an action run **Step B** with the Deletion Test and Minimal cause set and Counterfactual flip and Milestone dependency and Opposite possibility test.  
- Use **periods only** in **all_rationale**. **No commas or semicolons**. **No ellipses**.  
- In each subsequent sentence list **all** earlier IDs exactly as p1 and p2 and p3 style with the word **and** between them and no commas.  
- The **results** array must follow the **input ID order**.  
- Do not include any evaluation or sentiment labels.

Output: A single JSON object exactly matching the schema described in Output Format.

Return ONLY one JSON object. Do not output anything before or after it.
Wrap the JSON object inside <JSON> ... </JSON> tags.
Provide output in the following format:

<JSON>
{{
  "results": [
    {{
      "id":"p1",
      "original_phrase":"...",
      "rationale":"...",
      "event_type":"..."
    }},
    ...
  ]
}}
</JSON>

"""

prompt_abstraction_extraction26 = """

## Role Assignment
You are a **narrative event evaluator**. 
Your task is to read a short story and a list of event phrases with IDs, understand the situation of the **main protagonist**, and assign each phrase exactly one evaluation label from a set of nine narrative categories.

---

## Term Definitions

### 1. Protagonist and Event Phrase
- **Protagonist**: The main person whose situation, actions, and outcomes matter most in the story. In a first-person story, this is usually “I”.
- **Event phrase**: A short text span that describes one situation, action, or result in the story. Each phrase has an ID like `"p1"`, `"p2"`, and so on.

---

### 2. Three base event types

1. **State**
   - A State describes how things *are* for someone at a given moment.
   - It answers questions like “How is the person?” or “What situation are they in?”.
   - Typical patterns:  
     - “be” + adjective or noun: *was upset, was comfortable, was angry*  
     - “have” + noun: *had too many problems, had everything he wanted*  
     - emotions or conditions: *felt hopeless*  
   - States can describe the protagonist or the environment.

2. **Action**
   - An Action describes *doing* something: physical, verbal, or mental activity.
   - It answers questions like “What did this person do?”.
   - Typical patterns: dynamic verbs such as *worked, texted, cried, asked, hosted, helped, decided, reflected, slept, sang*.
   - Actions always have a human agent: the protagonist or another person.

3. **Outcome**
   - An Outcome describes a later state that clearly results from earlier events in the same story.
   - It answers “What happened as a result?” for the protagonist or their situation.
   - Use story-time order and cues like *then, after that, the next day, so, therefore, as a result, it paid off*.
   - Typical verbs: *ended up, turned into, gained, lost, realized, learned, now knows*.

When you classify, first think in terms of State, Action, or Outcome, then choose one of the nine labels below.

---

### 3. Nine evaluation labels

Each label combines:
- a base type (State, Action, Outcome), and  
- a valence (positive, negative, neutral).

Always choose exactly one of these labels for each phrase:

#### A. State labels
1. **ease** (Positive State)
   - The protagonist is in a comfortable, safe, or beneficial situation.
   - Needs are met and there is no clear problem in focus.
   - Examples: feeling relaxed, secure, proud, satisfied.

2. **struggle** (Negative State)
   - The protagonist is in a difficult, painful, or problematic situation.
   - There is pressure, lack, danger, distress, or conflict.
   - Examples: feeling stressed, devastated, hopeless, overwhelmed, trapped.

3. **neutral_state** (Neutral State)
   - The phrase describes a situation without clear positive or negative value.
   - It may be ordinary, mixed, or underspecified.
   - Examples: being at a location, having a job, a neutral or descriptive environmental condition.

#### B. Action labels
4. **effort** (Positive Action by the protagonist)
   - The protagonist actively tries to improve or respond to a situation.
   - The focus is on constructive initiative or engagement, not on the final result.
   - Examples: asking for help, working hard, planning, reflecting seriously.

5. **indifference** (Negative Action or inaction by the protagonist)
   - The protagonist avoids acting, gives up, or behaves in a way that clearly ignores a problem they could address.
   - This includes explicit non-action in the face of a need.
   - Examples: doing nothing when help is needed, refusing to try.

6. **neutral_action** (Neutral Action)
   - Any action that is neither clear effort nor clear indifference from the protagonist.
   - Includes routine actions, descriptive actions, and actions by other people.
   - Examples: walking to a place, buying something without clear problem context, someone else talking.

#### C. Outcome labels
7. **gain** (Positive Outcome)
   - A later state where the protagonist gains something beneficial: resources, safety, status, understanding, or emotional improvement.
   - Examples: receiving a raise, inheriting money, forming a good relationship.

8. **loss** (Negative Outcome)
   - A later state where the protagonist loses something important: money, time, health, opportunity, respect, or emotional stability.
   - Examples: something breaking, being rejected, losing a job, missing a chance because of earlier actions.

9. **neutral_outcome** (Neutral or unclear Outcome)
   - A later state that results from earlier events but has mixed, unclear, or purely informational impact.
   - The story does not clearly present it as a gain or a loss for the protagonist.
   - General lessons and realizations belong here:
     - When a phrase mainly expresses learning or a conclusion (for example *realized, learned, concluded, now knows*), assign **neutral_outcome**.

---

## Task Definition

You receive:
- A **Story**: a short narrative text.
- A list of **Phrases** in the temporal order: JSON-like items of the form  
  `{{ "id":"p1","text":"..." }}, {{ "id":"p2","text":"..." }}, ...`.

Your task:

1. Read the story and phrases.
2. Identify the main protagonist.
3. Understand how each phrase relates to the protagonist and to other phrases.

4. For each phrase, always use previous events as context:
   - Before you classify phrase `pᵢ`, read all earlier phrases `p1` to `pᵢ₋₁`.
   - Ask two questions for `pᵢ`:  
     1) “Why is this phrase here in the story?”  
     2) “Is this phrase introducing something new, or is it mainly telling what happened *because of* earlier events?”
   - Use these earlier phrases to understand whether `pᵢ` continues an existing struggle or ease, or whether it is a new result of earlier events.
   - Use this context when choosing between **struggle, ease, neutral_state** and between **State** and **Outcome**.

5. For each phrase, apply a cause-or-new test:
   - First, check if `pᵢ` looks like a **result or payoff** of earlier events:
     - Does it resolve an earlier struggle?
     - Does it realize an earlier goal or desire?
     - Does it clearly describe “what happened because of” a previous action or situation?
   - If yes, treat `pᵢ` as an **Outcome** candidate first and choose `gain`, `loss`, or `neutral_outcome`.
   - If no, classify it as a **State** or **Action** based on its form.

6. For each phrase:
   - Decide if it is best treated as State, Action, or Outcome.
   - Use story-time logic and the order given to detect Outcomes:
     - Treat Outcomes as later states that clearly result from earlier phrases in the same list.
     - Use only information and ordering from the given story and phrases.

   - For Actions:
     - For the protagonist:
       - Use **effort** when the protagonist takes constructive steps.
       - Use **indifference** when the protagonist avoids reasonable action or gives up.
       - Use **neutral_action** for other actions of the protagonist that are not clearly effort or indifference.
     - For other people:
       - First check whether their action is itself a result of the protagonist’s earlier efforts or situation:
         - If the other person’s action clearly happens because of what the protagonist did or wanted, and it helps or harms the protagonist, treat it as an **Outcome** for the protagonist and label it `gain` or `loss`.
         - If the other person’s action is not clearly caused by or tied to the protagonist’s earlier efforts or goals, label it as **neutral_action**.
       - Express the positive or negative impact on the protagonist through Outcomes or States when appropriate.

   - For States:
     - Use the State labels for situations and conditions (emotional, physical, or contextual).
     - When a State is clearly part of an ongoing problem described in earlier phrases, label it as **struggle** rather than neutral_state.
     - When a State is clearly part of an ongoing benefit described in earlier phrases, label it as **ease** rather than neutral_state.

   - For Outcomes:
     - Use the Outcome labels for later states that clearly arise from earlier events in the story.
     - Use **gain** when the resulting state clearly improves the protagonist’s life.
     - Use **loss** when the resulting state clearly worsens the protagonist’s life or emotional stability.
     - Use **neutral_outcome** for general lessons or realizations, or for results whose value is not clearly good or bad.

7. After deciding the **type** (state/action/outcome), decide the **valence** (positive / negative / neutral) explicitly:
   - For valence reasoning, answer: “Is this good, bad, or neutral for the protagonist, given the story so far, and why?”

8. Then choose the final **evaluation** label by mapping **type + valence**:
   - If `type = state`:
     - positive valence → **ease**
     - negative valence → **struggle**
     - neutral valence → **neutral_state**
   - If `type = action`:
     - positive valence and constructive effort by the protagonist → **effort**
     - negative valence and avoidance/giving up by the protagonist → **indifference**
     - otherwise → **neutral_action**
   - If `type = outcome`:
     - positive valence → **gain**
     - negative valence → **loss**
     - neutral valence → **neutral_outcome**
   - Ensure the chosen **evaluation** is consistent with your type and valence reasoning.

9. Choose exactly one label from this list for each phrase:  
   `ease, struggle, neutral_state, effort, indifference, neutral_action, gain, loss, neutral_outcome`.

---

## Output Format

Always produce output with two parts in this order:

1. A **thinking** section:
   - Wrap it in `<thinking>` and `</thinking>` tags.
   - Follow this structure inside the thinking section:

     - First, summarize the story’s arc:
       - `protagonist: ...`
       - `story_arc_initial: ...`
       - `story_arc_key_changes: ...`
       - `story_arc_final_state: ...`

     - Then, for each phrase `pᵢ` in order (p1, p2, p3, ...), write one line in this format:

       `pᵢ: role=...; cause_or_new=...; reasoning_type=...; type=...; reasoning_valence=...; evaluation=...`

       where:
       - `role` is a short description of how this phrase functions in the story (for example: introduces setup, continues struggle, shows turning point, shows result/payoff).
       - `cause_or_new` explains if it is a new event or caused by earlier ones (for example: `new` or `caused_by=[p1,p2]`).
       - `reasoning_type` explains briefly how you used the story context and causality to decide whether this phrase is a state, action, or outcome.
       - `type` is one of `state`, `action`, or `outcome`.
       - `reasoning_valence` explains whether this phrase is positive, negative, or neutral for the protagonist and why.
       - `evaluation` is one of the nine labels: `ease, struggle, neutral_state, effort, indifference, neutral_action, gain, loss, neutral_outcome`, chosen consistently with `type` and `reasoning_valence`.

   - Identify the protagonist clearly.
   - Describe how the phrases relate to each other in terms of State, Action, and Outcome, and how causality flows through the story.
   - Explicitly use previous events as context when deciding the label for each new phrase.
   - Keep this section concise and focused.
   - The total length of the thinking section stays within 1500 characters.

2. A **JSON** section:
   - Wrap it in `<JSON>` and `</JSON>` tags.
   - Inside, return a single JSON object with a key `"results"`.
   - `"results"` is an array of objects, one per phrase, in the **same order as the input IDs** (`p1`, `p2`, `p3`, …).

Each result object has the following keys:
- `"id"`: the phrase ID, such as `"p1"`.
- `"original_phrase"`: the exact text of the phrase.
- `"rationale"`: a short, one-sentence explanation for the chosen label. The rationale can refer to your reasoning in the thinking section and should reflect how earlier events influenced your decision and whether the phrase is a cause, continuation, or result, and its valence.
- `"event_evalaution"`: the chosen label as a string, exactly one of  
  `"ease"`, `"struggle"`, `"neutral_state"`, `"effort"`, `"indifference"`, `"neutral_action"`, `"gain"`, `"loss"`, `"neutral_outcome"`.


---

## Example

Story:
“I was really upset by my new jacket. I bought a cheap jacket for only a dollar. The temperature dropped sharply that night. The jacket fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

Phrases:
[
  {{ "id":"p1","text":"I bought a cheap jacket" }},
  {{ "id":"p2","text":"The temperature dropped sharply that night" }},
  {{ "id":"p3","text":"Jacket fell apart the next day" }},
  {{ "id":"p4","text":"upset by the new jacket" }},
  {{ "id":"p5","text":"I concluded more expensive clothes last longer" }}
]

### Example Output

<thinking>
protagonist: The narrator “I”.
story_arc_initial: I start by having bought a very cheap jacket and then face a cold night.
story_arc_key_changes: Because the jacket is cheap and the temperature drops, the jacket fails the next day and I become emotionally upset about it.
story_arc_final_state: From this bad experience I extract a general lesson that buying more expensive clothes that last longer is better.

p1: role=introduces the practical setup of the story (the cheap jacket purchase); cause_or_new=new with no prior in-story cause; reasoning_type=This is the first concrete event and describes something I do so it is an action; type=action; reasoning_valence=The purchase itself is not clearly good or bad for me yet so it is neutral; evaluation=neutral_action.
p2: role=adds contextual conditions that make the later failure more likely; cause_or_new=new, not caused by p1 but following it in time; reasoning_type=This describes how the weather is and not something anyone does so it is a state; type=state; reasoning_valence=The drop in temperature is presented as a neutral environmental fact that only later leads to trouble so it is neutral; evaluation=neutral_state.
p3: role=key turning point where the concrete problem appears; cause_or_new=caused_by=[p1,p2]; reasoning_type=This occurs after the purchase and cold night and shows what happened as a result so it is an outcome; type=outcome; reasoning_valence=The jacket falling apart clearly harms me and wastes my money so it is negative; evaluation=loss.
p4: role=emotional reaction that shows the personal impact of the failure; cause_or_new=caused_by=[p3]; reasoning_type=This follows the failure and expresses the resulting emotional state so it is an outcome; type=outcome; reasoning_valence=Being upset is clearly negative for my well-being so it is negative; evaluation=loss.
p5: role=final reflective conclusion that wraps up the story; cause_or_new=caused_by=[p1,p2,p3,p4]; reasoning_type=This is a general belief formed after the prior events so it is an outcome; type=outcome; reasoning_valence=The lesson is useful information but is not clearly framed as happy or sad, just something I now know so it is neutral; evaluation=neutral_outcome.
</thinking>

<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "I bought a cheap jacket",
      "rationale": "This phrase introduces a new purchase action by the protagonist with no prior in-story cause and is not clearly good or bad yet so it is a neutral_action.",
      "event_evalaution": "neutral_action"
    }},
    {{
      "id": "p2",
      "original_phrase": "The temperature dropped sharply that night",
      "rationale": "This phrase introduces a new weather condition that sets context but is not a result of earlier events and is neutral for the protagonist so it is a neutral_state.",
      "event_evalaution": "neutral_state"
    }},
    {{
      "id": "p3",
      "original_phrase": "Jacket fell apart the next day",
      "rationale": "This phrase describes a jacket failure that happens after the cheap purchase and cold night and clearly harms the protagonist so it is a loss outcome.",
      "event_evalaution": "loss"
    }},
    {{
      "id": "p4",
      "original_phrase": "upset by the new jacket",
      "rationale": "This phrase describes the protagonist’s negative emotional reaction that results from the jacket failure so it is a loss outcome.",
      "event_evalaution": "loss"
    }},
    {{
      "id": "p5",
      "original_phrase": "I concluded more expensive clothes last longer",
      "rationale": "This phrase shows a general lesson the protagonist learns from all earlier events and is a neutral informational result so it is a neutral_outcome.",
      "event_evalaution": "neutral_outcome"
    }}
  ]
}}
</JSON>

---

### Your Turn

#### Input Format
Story:
{story}

Phrases:
{phrases}

#### Remember

1. Always identify the protagonist and evaluate events from their perspective.
2. First summarize the overall story arc in your thinking: initial situation, key actions or changes, and final payoff.
3. For each phrase, first decide if it is best seen as State, Action, or Outcome.
4. Before labeling phrase `pᵢ`, always read and use the earlier phrases `p1` to `pᵢ₋₁` as context.
5. For each phrase, ask “Why is this phrase here?” and “Is it new or mainly caused by earlier events?” and use this to decide if it is an Outcome.
6. Use story-time order and explicit cues to detect Outcomes as later states that clearly result from earlier phrases.
7. Use **ease, struggle, neutral_state** for States depending on positive, negative, or neutral impact on the protagonist or neutral description of conditions. When a State is clearly part of an ongoing problem use **struggle**; when clearly part of an ongoing benefit use **ease**.
8. Use **effort, indifference, neutral_action** for Actions; Actions are always done by people. Use effort and indifference only for protagonist actions and neutral_action for other actions or neutral actions unless those actions are clearly results tied to the protagonist’s goals, in which case treat them as Outcomes.
9. Explicitly reason about valence: state whether each phrase is positive, negative, or neutral for the protagonist and why.
10. Use **gain, loss, neutral_outcome** for Outcomes depending on beneficial, harmful, or neutral/mixed results. Use neutral_outcome for general lessons and realizations.
11. For every phrase, choose exactly one label from the nine and explain it with one short sentence in the rationale.

Output: Always output two parts in this order: first a concise `<thinking>` section using the specified structure, then a `<JSON>` section with a `"results"` array in the same ID order as the input.

All of your context must be placed inside the <thinking>...</thinking> and <JSON>...</JSON> tags. Do not generate anything outside of these tags.
Wrap the JSON object inside <JSON> ... </JSON> tags.
Provide output in the following format:

<thinking>
protagonist: ...
story_arc_initial: ...
story_arc_key_changes: ...
story_arc_final_state: ...

p1: role=...; cause_or_new=...; reasoning_type=...; type=...; reasoning_valence=...; evaluation=...
p2: role=...; cause_or_new=...; reasoning_type=...; type=...; reasoning_valence=...; evaluation=...
...
</thinking>

<JSON>
{{
  "results": [
    {{
      "id": "p1",
      "original_phrase": "...",
      "rationale": "...",
      "event_evalaution": "..."
    }},
    {{
      "id": "p2",
      "original_phrase": "...",
      "rationale": "...",
      "event_evalaution": "..."
    }}
  ]
}}
</JSON>


"""


# prompt_abstraction_extraction5 = """
# ### Role Assignment
# You are an assistant that maps narrative phrases to **FrameNet-style semantic frames** and fills their **frame-specific roles** (participants/props).
# A **semantic frame** is a script-like conceptual structure evoked by a **word/lexical unit** that presupposes a situation type and a set of **core and non-core roles** (e.g., KILLING with KILLER, VICTIM; INGESTION with INGESTOR, INGESTIBLES).
# Your job: for each input phrase, (a) identify the **most appropriate FrameNet-inspired frame name**, (b) list the **roles** that the phrase overtly fills (and any clearly licensed adjuncts like Time, Place, Manner), and (c) give a one-sentence **rationale** explaining the choice.

# ---

# ### Task Definition
# Input
# 1. A Story (free text).
# 2. A list of Phrases (each a concrete event, feeling, judgment, or action from the story).

# Output (per phrase)
# - id: copied exactly from input.
# - original_phrase: copied exactly from the phrase text.
# - frame_name: a concise FrameNet-style name (e.g., Perception_experience, Scrutiny, Coming_to_believe, Activity_stop, Activity_start, Health_status, Commerce_buy, Grasp, Killing).
# - frame_roles: an object mapping role names → fillers drawn from the phrase (e.g., {{ "Experiencer": "David", "Content": "weight gain" }}). Use standard role names when widely established (e.g., Experiencer, Stimulus/Content, Agent, Patient/Theme, Killer, Victim, Buyer, Goods, Price, Time, Place, Instrument). If multiple fillers occur for a role, return a list.
# - rationale: one short sentence justifying the frame and roles (point to the evoking word and how the phrase’s elements fill the frame’s roles).

# Frame selection & role filling guidelines
# - Pick the frame that the main evoking word in the phrase most plausibly triggers (e.g., notice → Perception_experience; realize → Coming_to_believe; stop/start → Activity_stop/Activity_start; kill → Killing; buy → Commerce_buy).
# - Prefer specific frames over generic ones when the evoking word strongly selects them (e.g., Killing over Cause_harm for kill).
# - Fill only roles that are overtly realized or are standard non-core adjuncts clearly expressed (e.g., Time, Place, Manner, Reason, Purpose).
# - If a role is not expressed, omit it (do not invent fillers).
# - When uncertain between two near frames, choose the one more standard in FrameNet for the evoking word and explain briefly in the rationale.

# ---

# ### Delexicalization Rules
# - Do not paraphrase the frame_name with story-specific words; frame names must be general and FrameNet-style.
# - Do keep surface words in role fillers (they anchor the roles to the original phrase).
# - Mention participants in roles (e.g., Experiencer, Agent, Patient). Do not merge multiple roles into one label.
# - Avoid redefining frames; use conventional role labels when widely used in FrameNet.

# ---

# ### Quality Checks *(silent; output only JSON array)*
# 1. Frame validity: The chosen frame is a plausible FrameNet-style match for the evoking word in the phrase.
# 2. Role fit: Each role label is appropriate for the frame and each filler comes from the phrase.
# 3. Coverage: All overtly expressed core roles are filled when present; adjuncts included only if explicit.
# 4. Parsimony: Do not add roles that are not expressed.
# 5. Rationale: Cites the evoking word and why the frame + roles fit the phrase’s structure.
# 6. Concision: frame_name is 1–3 words in FrameNet style; rationale is one sentence.

# ---

# ### Output Format
# Return a single JSON object with array results. Each element must include:
# - id
# - original_phrase
# - frame_name
# - frame_roles (filler or role : [fillers])
# - rationale

# Return ONLY one JSON object.
# Do not output anything before or after it.
# Wrap the array inside <JSON> ... </JSON> tags.

# ---

# ### Examples

# Example 1

# Story:
# “David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.”

# Phrases:
# [
#   {{ "id":"p1","text":"David noticed weight gain" }},
#   {{ "id":"p2","text":"David examined his habits for a reason" }},
#   {{ "id":"p3","text":"David Realized he ate too much fast food" }},
#   {{ "id":"p4","text":"David Stopped going to burger places" }},
#   {{ "id":"p5","text":"David Started a vegetarian diet" }},
#   {{ "id":"p6","text":"David Felt better after a few weeks" }},
#   {{ "id":"p7","text":"David had stopped eating unhealthy foods" }}
# ]

# Output:
# <JSON>
# {{
#   "results": [
#     {{
#       "id": "p1",
#       "original_phrase": "David noticed weight gain",
#       "frame_name": "Perception_experience",
#       "frame_roles": {{ "Experiencer": "David", "Content": "weight gain" }},
#       "rationale": "“noticed” evokes Perception_experience with an Experiencer who becomes aware of a Content."
#     }},
#     {{
#       "id": "p2",
#       "original_phrase": "David examined his habits for a reason",
#       "frame_name": "Scrutiny",
#       "frame_roles": {{ "Inspector": "David", "Phenomenon": "his habits", "Purpose": "a reason" }},
#       "rationale": "“examined” selects Scrutiny where an Inspector investigates a Phenomenon, optionally with a Purpose."
#     }},
#     {{
#       "id": "p3",
#       "original_phrase": "David Realized he ate too much fast food",
#       "frame_name": "Coming_to_believe",
#       "frame_roles": {{ "Cognizer": "David", "Proposition": "he ate too much fast food" }},
#       "rationale": "“realized” triggers Coming_to_believe with a Cognizer arriving at a Proposition."
#     }},
#     {{
#       "id": "p4",
#       "original_phrase": "David Stopped going to burger places",
#       "frame_name": "Activity_stop",
#       "frame_roles": {{ "Agent": "David", "Activity": "going to burger places" }},
#       "rationale": "“stopped” evokes Activity_stop where an Agent ceases an Activity."
#     }},
#     {{
#       "id": "p5",
#       "original_phrase": "David Started a vegetarian diet",
#       "frame_name": "Activity_start",
#       "frame_roles": {{ "Agent": "David", "Activity": "a vegetarian diet" }},
#       "rationale": "“started” evokes Activity_start with an Agent initiating an Activity."
#     }},
#     {{
#       "id": "p6",
#       "original_phrase": "David Felt better after a few weeks",
#       "frame_name": "Health_status",
#       "frame_roles": {{ "Patient": "David", "Attribute": "felt better", "Time": "after a few weeks" }},
#       "rationale": "A change in well-being fits Health_status with a Patient, an Attribute, and a Time adjunct."
#     }},
#     {{
#       "id": "p7",
#       "original_phrase": "David had stopped eating unhealthy foods",
#       "frame_name": "Activity_stop",
#       "frame_roles": {{ "Agent": "David", "Activity": "eating unhealthy foods", "Aspect": "completed" }},
#       "rationale": "Perfective “had stopped” indicates Activity_stop with a completed cessation of the Activity."
#     }}
#   ]
# }}
# </JSON>

# ---------

# Example 2

# Story:
# “Eric and his wife had a daughter named Meg. Eric and Meg were very sad when Eric's wife passed away. Eric met a woman and married her 5 years after his wife died. Meg is finally happy with her new stepmother as she is very kind to her.”

# Phrases:
# [
#   {{ "id":"p1","text":"Eric and his wife had Meg" }},
#   {{ "id":"p2","text":"Erics wife passed away" }},
#   {{ "id":"p3","text":"Eric and Meg were very sad" }},
#   {{ "id":"p4","text":"Eric met a woman" }},
#   {{ "id":"p5","text":"Eric married the woman five years later " }},
#   {{ "id":"p6","text":"Meg was happy with her stepmother" }},
#   {{ "id":"p7","text":"Megs stepmother is kind to her" }}
# ]

# Output:
# <JSON>
# {{
#   "results": [
#     {{
#       "id": "p1",
#       "original_phrase": "Eric and his wife had Meg",
#       "frame_name": "Birth",
#       "frame_roles": {{ "Parents": ["Eric", "his wife"], "Child": "Meg" }},
#       "rationale": "Having a child evokes the Birth frame with Parents and Child roles."
#     }},
#     {{
#       "id": "p2",
#       "original_phrase": "Erics wife passed away",
#       "frame_name": "Death",
#       "frame_roles": {{ "Deceased": "Eric's wife" }},
#       "rationale": "“passed away” evokes Death with the Deceased role filled."
#     }},
#     {{
#       "id": "p3",
#       "original_phrase": "Eric and Meg were very sad",
#       "frame_name": "Experiencer_focus",
#       "frame_roles": {{ "Experiencer": ["Eric", "Meg"], "Emotion": "sadness" }},
#       "rationale": "An emotional state without explicit stimulus fits Experiencer_focus with Experiencers and an Emotion."
#     }},
#     {{
#       "id": "p4",
#       "original_phrase": "Eric met a woman",
#       "frame_name": "Meet_with",
#       "frame_roles": {{ "Participant_1": "Eric", "Participant_2": "a woman" }},
#       "rationale": "“met” evokes Meet_with with two participants encountering each other."
#     }},
#     {{
#       "id": "p5",
#       "original_phrase": "Eric married the woman five years later ",
#       "frame_name": "Marriage",
#       "frame_roles": {{ "Spouses": ["Eric", "the woman"], "Time": "five years later" }},
#       "rationale": "“married” selects Marriage with Spouses and a Time adjunct."
#     }},
#     {{
#       "id": "p6",
#       "original_phrase": "Meg was happy with her stepmother",
#       "frame_name": "Experiencer_focus",
#       "frame_roles": {{ "Experiencer": "Meg", "Emotion": "happiness", "Stimulus": "her stepmother" }},
#       "rationale": "A positive emotional state toward someone fits Experiencer_focus with Stimulus expressed."
#     }},
#     {{
#       "id": "p7",
#       "original_phrase": "Megs stepmother is kind to her",
#       "frame_name": "Kindness",
#       "frame_roles": {{ "Agent": "Meg's stepmother", "Recipient": "her" }},
#       "rationale": "The copular adjective 'kind … to' profiles a benevolent disposition; 'kind' evokes the Kindness frame with an Agent showing kindness toward a Recipient."
#     }}
#   ]
# }}
# </JSON>

# ---------

# Example 3

# Story:
# “There was a bug on the wall by the bed. Kate grabbed a shoe and killed it.”

# Phrases:
# [
#   {{ "id":"p1","text":"Bug was on the wall by the bed" }},
#   {{ "id":"p2","text":"Kate grabbed a shoe" }},
#   {{ "id":"p3","text":"Kate killed the bug" }}
# ]

# Output:
# <JSON>
# {{
#   "results": [
#     {{
#       "id": "p1",
#       "original_phrase": "Bug was on the wall by the bed",
#       "frame_name": "Spatial_location",
#       "frame_roles": {{ "Figure": "Bug", "Ground": "the wall", "Locative_relation": "by the bed" }},
#       "rationale": "A located entity relative to a reference object fits Spatial_location with Figure and Ground."
#     }},
#     {{
#       "id": "p2",
#       "original_phrase": "Kate grabbed a shoe",
#       "frame_name": "Grasp",
#       "frame_roles": {{ "Agent": "Kate", "Item": "a shoe" }},
#       "rationale": "“grabbed” evokes Grasp where an Agent takes hold of an Item."
#     }},
#     {{
#       "id": "p3",
#       "original_phrase": "Kate killed the bug",
#       "frame_name": "Killing",
#       "frame_roles": {{ "Killer": "Kate", "Victim": "the bug" }},
#       "rationale": "“killed” evokes Killing with Killer and Victim; the prior shoe could serve as Instrument but is not stated here."
#     }}
#   ]
# }}
# </JSON>

# ---------

# Example 4

# Story:
# “I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

# Phrases:
# [
#   {{ "id":"p1","text":"I bought a cheap jacket" }},
#   {{ "id":"p2","text":"Jacket fell apart the next day" }},
#   {{ "id":"p3","text":"I concluded more expensive clothes last longer" }}
# ]

# Output:
# <JSON>
# {{
#   "results": [
#     {{
#       "id": "p1",
#       "original_phrase": "I bought a cheap jacket",
#       "frame_name": "Commerce_buy",
#       "frame_roles": {{ "Buyer": "I", "Goods": "a cheap jacket" }},
#       "rationale": "“bought” evokes Commerce_buy with Buyer and Goods; price is implied but not explicitly quantified here."
#     }},
#     {{
#       "id": "p2",
#       "original_phrase": "Jacket fell apart the next day",
#       "frame_name": "Breaking_apart",
#       "frame_roles": {{ "Whole": "Jacket", "Time": "the next day" }},
#       "rationale": "A single item disintegrating fits Breaking_apart with Whole and a Time adjunct."
#     }},
#     {{
#       "id": "p3",
#       "original_phrase": "I concluded more expensive clothes last longer",
#       "frame_name": "Coming_to_believe",
#       "frame_roles": {{ "Cognizer": "I", "Proposition": "more expensive clothes last longer" }},
#       "rationale": "“concluded/now know” licenses Coming_to_believe with a Cognizer and a Proposition."
#     }}
#   ]
# }}
# </JSON>

# ---

# ### Your Turn

# #### Input Format
# Story:
# {story}

# Phrases:
# {phrases}

# ---------

# #### Output Format
# #### Remember:
# - Read the Story and Phrases; work per phrase.
# - Choose the FrameNet-style frame evoked by the main lexical unit; prefer specific, standard frames.
# - Fill only roles overtly expressed in the phrase (plus clear adjuncts like Time/Place/Manner/Purpose/Reason).
# - Keep frame_name generic (no story-specific words); role fillers must come from the phrase.
# - Preserve id and original_phrase exactly as given.
# - Rationale must cite the evoking word and why the roles fit; avoid tautologies.
# - Apply all Quality Checks and keep outputs concise and consistent.


# Return ONLY one JSON object. Do not output anything before or after it.
# Wrap the array inside <JSON> ... </JSON> tags.
# Provide output in the following format:
# <JSON>
# {{
#   "results": [
#     {{
#       "id": "<copy from input>",
#       "original_phrase": "<copy from input>",
#       "frame_name": "<FrameNet-style name>",
#       "frame_roles": {{ "<RoleName>": "<filler or [fillers]>", "..." : "..." }},
#       "rationale": <one sentence explaining the mapping>
#     }},
#     ...
#   ]
# }}
# </JSON>

# """


# prompt_abstraction_extraction6 = """

# ### Role Assignment
# You are an assistant that extracts **cognitive frames** (prototype-like knowledge structures) from a story and its event phrases, then **groups events into frames that correspond to distinct script steps**, and **orders the frames as a script**.  
# A **cognitive frame** is an open-ended, encyclopedic structure: when one element is activated, related elements become available. For narrative analysis, treat cognitive frames as **mid-level “steps”** in a script (e.g., SELF_DIAGNOSIS, DIET_CHANGE, HEALTH_IMPROVEMENT). **Do not merge across different steps.** Merge only events that are **the same step** (same goal, mechanism, and domain **and** same narrative phase).

# ---

# ### Task Definition
# **Input**
# 1. A *Story* (free text).
# 2. A list of *Phrases* (each a concrete event, feeling, judgment, or action).

# **Output**
# Return **one** JSON object with:
# - **cognitive_frames**: an array of frame objects with:
#   - **frame_id**: unique ID like `"cf1"`, `"cf2"`, …
#   - **name**: concise, prototype-style **UPPER_SNAKE_CASE** (e.g., `SELF_DIAGNOSIS`, `DIET_CHANGE`, `HEALTH_IMPROVEMENT`).
#   - **description**: one-sentence definition of the frame’s gist.
#   - **supporting_events**: list of event IDs (e.g., `["p4","p5"]`) that instantiate **this same step**.
#   - **slots**: object with key conceptual roles (e.g., `Agent`, `Problem`, `Cause_identified`, `Target_behavior`, `Replacement_behavior`, `Goal`, `Outcome`, `Time`, `Place`, `Mechanism`, `Reason`). Values are strings or arrays of strings drawn from the phrases.
#   - **inherits_from** *(optional)*: array of broader frames/schemas (e.g., `["HEALTH_MANAGEMENT"]`).
#   - **script_relations** *(optional)*: `{{ "preceded_by": ["cfX"], "followed_by": ["cfY"] }}`.
#   - **confidence**: number in `[0,1]` for this frame’s validity in context.
#   - **notes** *(optional)*: brief justification (e.g., why events were merged, or why a step boundary was set).
# - **event_to_cognitive_frame**: object mapping each event ID → list of frame_ids it belongs to.
# - **script_order**: array of frame_ids in narrative order (high-level script).
# - **unassigned_events**: array of event IDs not covered by any cognitive frame (empty if fully covered).

# **Method (three-phase, with step integrity)**
# 1) **Seed labels** per event (mid-level candidates).  
# 2) **Segment into steps**: identify **step boundaries** (goal shift, status/role change, major state transition, explicit time jump, new relationship, or causal closure).  
# 3) **Within-step merge only**: merge candidates **inside the same step** if they share **goal + mechanism + domain**; otherwise keep separate frames.  
# 4) **Script**: order frames by narrative progression; set `script_relations` where obvious.

# ---

# ### Delexicalization Rules
# - **Frame names**: general, prototype-like, **no proper names** or story-specific terms; use domain-neutral wording.
# - **Slots**: may contain story surface strings (to show evidence), but be concise.
# - **No cross-step merging**: if events belong to different steps (e.g., forming an initial family vs. remarriage years later), **keep separate frames** even if conceptually related.
# - **No invention**: Populate only slots **licensed by the phrases** (if unknown, omit).

# ---

# ### Quality Checks *(silent; output only JSON)*
# 1. **Step integrity**: Events from distinct narrative steps **must not** be merged into one frame.  
# 2. **Merging discipline (within-step)**: Merge events only if **goal + mechanism + domain** align **and** they belong to the **same step**.  
# 3. **Coverage**: Every event ID appears in `supporting_events` (via some frame) and in `event_to_cognitive_frame`, or else in `unassigned_events`.  
# 4. **Script coherence**: `script_order` aligns with `script_relations`.  
# 5. **Slot fidelity**: Slot values are from the phrases (verbatim or lightly normalized).  
# 6. **Parsimony with steps respected**: Minimal number of frames that still preserves **step-by-step** narrative structure.  
# 7. **Confidence**: Calibrated `[0,1]` and reflects ambiguity (lower if boundary/merge is borderline).

# ---

# ### Output Format
# **Return ONLY one JSON object. Do not output anything before or after it.**  
# Wrap the entire object inside `<JSON> ... </JSON>` tags.

# **Top-level schema**
# - `cognitive_frames`: [ {{ frame_id, name, description, supporting_events, slots, inherits_from?, script_relations?, confidence, notes? }}, … ]
# - `event_to_cognitive_frame`: {{ "<event_id>": ["<cf_id>", …], … }}
# - `script_order`: ["<cf_id>", …]
# - `unassigned_events`: ["<event_id>", …]

# ---

# ### Examples

# **Example 1**

# Story:
# “David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.”

# Phrases:
# [
#   {{ "id":"p1","text":"David noticed weight gain" }},
#   {{ "id":"p2","text":"David examined his habits for a reason" }},
#   {{ "id":"p3","text":"David Realized he ate too much fast food" }},
#   {{ "id":"p4","text":"David Stopped going to burger places" }},
#   {{ "id":"p5","text":"David Started a vegetarian diet" }},
#   {{ "id":"p6","text":"David Felt better after a few weeks" }},
#   {{ "id":"p7","text":"David had stopped eating unhealthy foods" }}
# ]

# Output:
# <JSON>
# {{
#   "cognitive_frames": [
#     {{
#       "frame_id": "cf1",
#       "name": "SELF_DIAGNOSIS",
#       "description": "Identifying a cause of a personal problem through reflection.",
#       "supporting_events": ["p1", "p2", "p3"],
#       "slots": {{
#         "Agent": ["David"],
#         "Problem": ["weight gain"],
#         "Cause_identified": ["eating too much fast food"]
#       }},
#       "inherits_from": ["CAUSAL_REASONING"],
#       "script_relations": {{ "followed_by": ["cf2"] }},
#       "confidence": 0.82
#     }},
#     {{
#       "frame_id": "cf2",
#       "name": "DIET_CHANGE",
#       "description": "Shifting habitual intake patterns to improve health.",
#       "supporting_events": ["p4", "p5", "p7"],
#       "slots": {{
#         "Agent": ["David"],
#         "Target_behavior": ["going to burger places", "eating unhealthy foods"],
#         "Replacement_behavior": ["a vegetarian diet"],
#         "Reason": ["health concern / weight gain"]
#       }},
#       "inherits_from": ["HEALTH_MANAGEMENT"],
#       "script_relations": {{ "preceded_by": ["cf1"], "followed_by": ["cf3"] }},
#       "confidence": 0.86,
#       "notes": "p4, p5, p7 are the same step (behavioral diet change); merged within-step only."
#     }},
#     {{
#       "frame_id": "cf3",
#       "name": "HEALTH_IMPROVEMENT",
#       "description": "Perceived positive change in well-being after intervention.",
#       "supporting_events": ["p6"],
#       "slots": {{ "Agent": ["David"], "Outcome": ["felt better"], "Time": ["after a few weeks"] }},
#       "inherits_from": ["HEALTH_STATUS"],
#       "script_relations": {{ "preceded_by": ["cf2"] }},
#       "confidence": 0.78
#     }}
#   ],
#   "event_to_cognitive_frame": {{
#     "p1": ["cf1"], "p2": ["cf1"], "p3": ["cf1"],
#     "p4": ["cf2"], "p5": ["cf2"], "p6": ["cf3"], "p7": ["cf2"]
#   }},
#   "script_order": ["cf1", "cf2", "cf3"],
#   "unassigned_events": []
# }}
# </JSON>

# ---------

# **Example 2**

# Story:
# “Eric and his wife had a daughter named Meg. Eric and Meg were very sad when Eric's wife passed away. Eric met a woman and married her 5 years after his wife died. Meg is finally happy with her new stepmother as she is very kind to her.”

# Phrases:
# [
#   {{ "id":"p1","text":"Eric and his wife had Meg" }},
#   {{ "id":"p2","text":"Erics wife passed away" }},
#   {{ "id":"p3","text":"Eric and Meg were very sad" }},
#   {{ "id":"p4","text":"Eric met a woman" }},
#   {{ "id":"p5","text":"Eric married the woman five years later " }},
#   {{ "id":"p6","text":"Meg was happy with her stepmother" }},
#   {{ "id":"p7","text":"Megs stepmother is kind to her" }}
# ]

# Output:
# <JSON>
# {{
#   "cognitive_frames": [
#     {{
#       "frame_id": "cf1",
#       "name": "INITIAL_FAMILY_FORMATION",
#       "description": "Establishing the original family unit.",
#       "supporting_events": ["p1"],
#       "slots": {{ "Event": ["birth of child"] }},
#       "inherits_from": ["FAMILY_STRUCTURE"],
#       "script_relations": {{ "followed_by": ["cf2"] }},
#       "confidence": 0.84
#     }},
#     {{
#       "frame_id": "cf2",
#       "name": "LOSS_EVENT",
#       "description": "Death of a close family member.",
#       "supporting_events": ["p2"],
#       "slots": {{ "Deceased": ["Eric's wife"] }},
#       "inherits_from": ["LIFE_TRANSITIONS"],
#       "script_relations": {{ "preceded_by": ["cf1"], "followed_by": ["cf3"] }},
#       "confidence": 0.86
#     }},
#     {{
#       "frame_id": "cf3",
#       "name": "GRIEF_RESPONSE",
#       "description": "Emotional reaction to bereavement.",
#       "supporting_events": ["p3"],
#       "slots": {{ "Experiencers": ["Eric", "Meg"], "Emotion": ["sadness"] }},
#       "inherits_from": ["BEREAVEMENT_AND_ADJUSTMENT"],
#       "script_relations": {{ "preceded_by": ["cf2"], "followed_by": ["cf4"] }},
#       "confidence": 0.8
#     }},
#     {{
#       "frame_id": "cf4",
#       "name": "NEW_PARTNER_ENCOUNTER",
#       "description": "Initial meeting that may lead to a new relationship.",
#       "supporting_events": ["p4"],
#       "slots": {{ "Participants": ["Eric", "a woman"] }},
#       "inherits_from": ["RELATIONSHIP_FORMATION"],
#       "script_relations": {{ "preceded_by": ["cf3"], "followed_by": ["cf5"] }},
#       "confidence": 0.78
#     }},
#     {{
#       "frame_id": "cf5",
#       "name": "REMARRIAGE",
#       "description": "Forming a new marital bond after prior loss.",
#       "supporting_events": ["p5"],
#       "slots": {{ "Spouses": ["Eric", "the woman"], "Time": ["five years later"] }},
#       "inherits_from": ["FAMILY_RECONFIGURATION"],
#       "script_relations": {{ "preceded_by": ["cf4"], "followed_by": ["cf6"] }},
#       "confidence": 0.83
#     }},
#     {{
#       "frame_id": "cf6",
#       "name": "STEPFAMILY_ADJUSTMENT",
#       "description": "Positive adaptation to a new stepfamily relationship.",
#       "supporting_events": ["p6", "p7"],
#       "slots": {{ "Child": ["Meg"], "Affect": ["happiness"], "Support_factor": ["kind stepmother"] }},
#       "inherits_from": ["FAMILY_ADAPTATION"],
#       "script_relations": {{ "preceded_by": ["cf5"] }},
#       "confidence": 0.8,
#       "notes": "p6 and p7 are the same adjustment step (well-being + supportive behavior)."
#     }}
#   ],
#   "event_to_cognitive_frame": {{
#     "p1": ["cf1"],
#     "p2": ["cf2"],
#     "p3": ["cf3"],
#     "p4": ["cf4"],
#     "p5": ["cf5"],
#     "p6": ["cf6"],
#     "p7": ["cf6"]
#   }},
#   "script_order": ["cf1", "cf2", "cf3", "cf4", "cf5", "cf6"],
#   "unassigned_events": []
# }}
# </JSON>

# ---------

# **Example 3**

# Story:
# “There was a bug on the wall by the bed. Kate grabbed a shoe and killed it.”

# Phrases:
# [
#   {{ "id":"p1","text":"Bug was on the wall by the bed" }},
#   {{ "id":"p2","text":"Kate grabbed a shoe" }},
#   {{ "id":"p3","text":"Kate killed the bug" }}
# ]

# Output:
# <JSON>
# {{
#   "cognitive_frames": [
#     {{
#       "frame_id": "cf1",
#       "name": "PEST_SIGHTING",
#       "description": "Noticing an unwanted organism in a personal space.",
#       "supporting_events": ["p1"],
#       "slots": {{ "Problem": ["bug on the wall by the bed"] }},
#       "inherits_from": ["HOUSEHOLD_CONTEXT"],
#       "script_relations": {{ "followed_by": ["cf2"] }},
#       "confidence": 0.83
#     }},
#     {{
#       "frame_id": "cf2",
#       "name": "IMPROMPTU_TOOL_USE",
#       "description": "Selecting an everyday object to accomplish a task.",
#       "supporting_events": ["p2"],
#       "slots": {{ "Agent": ["Kate"], "Instrument": ["a shoe"] }},
#       "inherits_from": ["PROBLEM_SOLVING"],
#       "script_relations": {{ "preceded_by": ["cf1"], "followed_by": ["cf3"] }},
#       "confidence": 0.77
#     }},
#     {{
#       "frame_id": "cf3",
#       "name": "NUISANCE_RESOLUTION",
#       "description": "Eliminating the unwanted presence.",
#       "supporting_events": ["p3"],
#       "slots": {{ "Agent": ["Kate"], "Resolution": ["killed the bug"] }},
#       "inherits_from": ["HOUSEHOLD_MANAGEMENT"],
#       "script_relations": {{ "preceded_by": ["cf2"] }},
#       "confidence": 0.84
#     }}
#   ],
#   "event_to_cognitive_frame": {{
#     "p1": ["cf1"],
#     "p2": ["cf2"],
#     "p3": ["cf3"]
#   }},
#   "script_order": ["cf1", "cf2", "cf3"],
#   "unassigned_events": []
# }}
# </JSON>

# ---------

# **Example 4**

# Story:
# “I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

# Phrases:
# [
#   {{ "id":"p1","text":"I bought a cheap jacket" }},
#   {{ "id":"p2","text":"Jacket fell apart the next day" }},
#   {{ "id":"p3","text":"I concluded more expensive clothes last longer" }}
# ]

# Output:
# <JSON>
# {{
#   "cognitive_frames": [
#     {{
#       "frame_id": "cf1",
#       "name": "LOW_COST_PURCHASE",
#       "description": "Choosing an item primarily for minimal price.",
#       "supporting_events": ["p1"],
#       "slots": {{ "Decision": ["bought a cheap jacket"] }},
#       "inherits_from": ["CONSUMER_DECISION_MAKING"],
#       "script_relations": {{ "followed_by": ["cf2"] }},
#       "confidence": 0.82
#     }},
#     {{
#       "frame_id": "cf2",
#       "name": "PRODUCT_FAILURE_FEEDBACK",
#       "description": "Experiencing rapid breakdown that signals low durability.",
#       "supporting_events": ["p2"],
#       "slots": {{ "Outcome": ["fell apart the next day"], "Time": ["the next day"] }},
#       "inherits_from": ["POST_PURCHASE_EXPERIENCE"],
#       "script_relations": {{ "preceded_by": ["cf1"], "followed_by": ["cf3"] }},
#       "confidence": 0.84
#     }},
#     {{
#       "frame_id": "cf3",
#       "name": "HEURISTIC_UPDATE",
#       "description": "Adopting a general rule to guide future choices.",
#       "supporting_events": ["p3"],
#       "slots": {{ "Generalization": ["more expensive clothes last longer"] }},
#       "inherits_from": ["CONSUMER_LEARNING"],
#       "script_relations": {{ "preceded_by": ["cf2"] }},
#       "confidence": 0.83
#     }}
#   ],
#   "event_to_cognitive_frame": {{
#     "p1": ["cf1"],
#     "p2": ["cf2"],
#     "p3": ["cf3"]
#   }},
#   "script_order": ["cf1", "cf2", "cf3"],
#   "unassigned_events": []
# }}
# </JSON>

# ---

# ### Your Turn

# #### Input Format
# Story:
# {story}

# Phrases:
# {phrases}

# ---------

# #### Output Format
# **Return ONLY one JSON object. Do not output anything before or after it.**  
# Wrap the entire object inside `<JSON> ... </JSON>` tags.  
# Schema:
# - `cognitive_frames`: [ {{ frame_id, name, description, supporting_events, slots, inherits_from?, script_relations?, confidence, notes? }}, … ]
# - `event_to_cognitive_frame`: {{ "<event_id>": ["<cf_id>", …], … }}
# - `script_order`: ["<cf_id>", …]
# - `unassigned_events`: ["<event_id>", …]

# #### Remember:
# - **Step integrity first**: identify step boundaries (goal shift, status/role change, state transition, explicit time jump, new relationship, or causal closure).  
# - **Within-step merge only**: merge events **only** if they are the **same step** **and** share **goal + mechanism + domain**.  
# - **Name frames** in **UPPER_SNAKE_CASE**, domain-neutral, prototype-like.  
# - **Assign events** so every event ID appears in `event_to_cognitive_frame` or `unassigned_events`.  
# - **Fill slots** using information **expressed** in the phrases (verbatim or lightly normalized).  
# - **Order frames** into a script; keep `script_relations` consistent with `script_order`.  
# - **Prefer parsimony** while preserving **step-by-step** structure.  
# - **Report confidence** `[0,1]`; add brief notes for non-trivial merges or boundary choices.

# """