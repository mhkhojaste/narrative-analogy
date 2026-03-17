prompt_stage_extraction = """
### Role Assignment
You are an annotator who *clusters* story events into *narrative roles* for short, non-dramatic “micro-stories.” 

---------

### Task Definition
Given:
1. A *Story* describing a situation.
2. A list of *events* already extracted from that story (each with a stable ID and text).

Assign each *event* to exactly one of *five buckets*:
- The assignment must be based on the *ROLE* of that event, **not** chronology.
- Use the five buckets TP1–TP5 (defined below), which capture roles commonly seen in short stories.
- Return a JSON as the output.

Also provide a brief **rationale** (1–2 sentences) explaining **why** you made the assignment. The rationale must state the reasoning (features of the event and/or its role/relations) and must not be a tautology.

Do not invent new IDs or split items.

---------

### Term Definitions

- **TP1:** 
  - Setup / Background 
  - It is optional.
  - Pre-event context: setting, cast, history. Removing TP1 should not prevent understanding the main situation.
  - Cues: “had,” “used to,” “grew up,” “years ago,” “in [place],” “background.”
- **TP2:** 
  — Main Event / Situation 
  - It is REQUIRED
  - What the story is about: the problem/situation/opportunity being addressed (not its resolution).
  - Cues: “noticed,” “there was,” “is/was [problem],” “conflict,” “scheduled,” “found [issue].”
- **TP3:** 
  — Response / Actions / Decisions
  - It is optional.
  - What the protagonist does about TP2: decisions, investigations, behavioral changes, attempts.
  - Cues: “decided,” “examined/investigated,” “started,” “stopped,” “tried,” “implemented,” “realized” (when it follows investigation).
- **TP4:** 
  — Challenges / Complications 
  - It is optional.
  - Obstacles, failures, adverse events that hinder progress on TP2. Everything about TP2 that is not an action by the protagonist.
  - Cues: “but,” “however,” “failed,” “broke,” “blocked,” “fell apart,” “crashed,” “wasn’t able to,” “delay.”
- **TP5:**
  — Outcome / Resolution 
  - It is optional
  - The result, lesson, or final state/conclusion of the story (NOT an action step).
  - It Cannot be an action or a decision. Just a state or learned lesson.
  - Cues: “finally,” “as a result,” “therefore,” “concluded/learned,” “felt better,” “was happy,” “resulted in.”

### TIE-BREAKERS
1) TP5 (Outcome) is ONLY a lesson/conclusion/final state. Pure actions and decisions never go to TP5.
2) TP1 (Background) vs. TP2 (Situation): If removing the event still leaves the main situation understandable → TP1; otherwise → TP2.
3) Mixed attempt+failure in one event: prefer TP4 if a failure/obstacle is explicitly stated; otherwise TP3.
4) Actions and challenges may interleave; label strictly by ROLE, not by when they occur.
5) Do not invent or split events. Each input ID must appear in EXACTLY ONE bucket.
6) It is possible for some buckets to be empty, except for TP2. At least one event must be labeled TP2.
7) If an item is a phrase/fragment, interpret the implied event for labeling, but keep the `original_event` text unchanged.

### Output Explanation 
Return a JSON object with an array `results`. Each element corresponds to one input event and contains:
- `id`: the event identifier copied exactly from the input (e.g., "p1", "p2", ...).
- `original_event`: the exact input event text (byte-for-byte, including case and punctuation).
- `role`: one of the five buckets (TP1–TP5).
- `rationale`: one or two sentences explaining the choice based on features/role/relations (no tautologies).

Order the results in the same order as the input events. Use the same `id` values as provided.

**Formatting requirements (match Example 1 precisely):**
- Print ONLY the required JSON with `"results"`.
- Wrap the whole JSON in `<JSON>` ... `</JSON>`.
- In the array, each result object must be printed with **one key per line** and with the same indentation/leading spaces shown in Example 1 (i.e., leading spaces before each key, as in the first object of the first story).

---------

### Examples
**Example 1**

Story:
David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better.

Events:
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
      "id":"p1",
      "original_event":"David noticed weight gain",
      "role":"TP2",
      "rationale":"This introduces the main situation that motivates the story; removing it would make the story’s problem unclear." 
    }},
    {{ 
      "id":"p2",
      "original_event":"Examined his habits for a reason",
      "role":"TP3",
      "rationale":"An investigative action in response to the situation introduced in TP2." 
    }},
    {{ 
      "id":"p3",
      "original_event":"Realized he ate too much fast food",
      "role":"TP3",
      "rationale":"A realization produced by investigation; functions as part of the response to TP2." 
    }},
    {{ 
      "id":"p4",
      "original_event":"Stopped going to burger places",
      "role":"TP3",
      "rationale":"A behavioral change directly addressing the situation." 
    }},
    {{ 
      "id":"p5",
      "original_event":"Started a vegetarian diet",
      "role":"TP3",
      "rationale":"A decisive plan implementation that continues the response to the problem." 
    }},
    {{ 
      "id":"p6",
      "original_event":"Felt better after a few weeks",
      "role":"TP5",
      "rationale":"Final state/outcome that results from the preceding actions; not itself an action." 
    }}
  ]
}}
</JSON>

**Example 2**
Story:
Eric and his wife had a daughter named Meg. Eric and Meg were very sad when Eric's wife passed away. Eric met a woman and married her 5 years after his wife died. Meg is finally happy with her new stepmother.

Events:
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
      "id":"p1",
      "original_event":"Eric and his wife had Meg",
      "role":"TP1",
      "rationale":"Background family context; removing it still leaves the central situation understandable." 
    }},
    {{ 
      "id":"p2",
      "original_event":"Erics wife passed away",
      "role":"TP2",
      "rationale":"Introduces the central situation of loss that the story addresses." 
    }},
    {{ 
      "id":"p3",
      "original_event":"Eric and Meg were very sad",
      "role":"TP2",
      "rationale":"Further describes the ongoing situation and its emotional state." 
    }},
    {{ 
      "id":"p4",
      "original_event":"Eric met a woman",
      "role":"TP3",
      "rationale":"Action taken in response to the situation created by the loss." 
    }},
    {{ 
      "id":"p5",
      "original_event":"Five years later Eric married the woman",
      "role":"TP3",
      "rationale":"A commitment/action that progresses the response." 
    }},
    {{ 
      "id":"p6",
      "original_event":"Meg was happy with her stepmother",
      "role":"TP5",
      "rationale":"Final positive state—the outcome of prior actions in response to the situation." 
    }}
  ]
}}
</JSON>

**Example 3**
Story:
There was a bug on the wall by the bed. Kate grabbed a shoe and killed it.

Events:
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
      "id":"p1",
      "original_event":"Bug was on the wall by the bed",
      "role":"TP2",
      "rationale":"States the situation/problem that triggers the story." 
    }},
    {{ 
      "id":"p2",
      "original_event":"Kate grabbed a shoe",
      "role":"TP3",
      "rationale":"An action taken to address the situation introduced in TP2." 
    }},
    {{ 
      "id":"p3",
      "original_event":"Kate killed the bug",
      "role":"TP3",
      "rationale":"An action culminating the response; not a lesson/decision, so it remains an action (not TP5)." 
    }}
  ]
}}
</JSON>

**Example 4**
Story:
I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.

Events:
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
      "id":"p1",
      "original_event":"Bought a cheap jacket",
      "role":"TP2",
      "rationale":"Introduces the main situation that the story revolves around." 
    }},
    {{ 
      "id":"p2",
      "original_event":"Jacket fell apart the next day",
      "role":"TP4",
      "rationale":"A complication/failure within that situation that hinders progress." 
    }},
    {{ 
      "id":"p3",
      "original_event":"Concluded more expensive clothes last longer",
      "role":"TP5",
      "rationale":"Lesson/conclusion drawn from the events; a final state, not an action." 
    }}
  ]
}}
</JSON>

---------

#### Remember:
- Read the Story and events. For each event, output a cluster name and rationale following the given rules.
- The rationale must state the reason (features/role/relations that justify the kernel), not a tautology.
- TP1: Just some background knowledge. Optional.
- TP2: What the story is about. Required. At least one event.
- TP3: Any action/decision about TP2. Optional.
- TP4: Any challenge or problem about TP2. Optional.
- TP5: Just the final state or lesson learned. Not an action or decision. Optional.
- **Always use the same `id` and `original_event` as in the input.** Copy `original_event` exactly from the input `text` (preserve case and punctuation). Use the same `id` value.
- You are not allowed to change events or their ids. Use exactly what are given in the input. 

---------

### Your Turn

#### Input Format
Story:
{story}

Events:
{phrases}

---------

#### Output Format

Output: A single JSON object exactly matching the schema described in Output Explanation.

Return ONLY one JSON object. Do not output anything before or after it.
Wrap the object inside <JSON> ... </JSON> tags.
Provide output in the following format:

<JSON>
{{
  "results": [
    {{ 
      "id":"p1",
      "original_event":...,
      "role":...,
      "rationale":... 
    }},
    ...
  ]
}}
</JSON>

"""



prompt_stage_extraction2 = """
### Role Assignment
You are an annotator who *clusters* story events into *narrative roles* for short, non-dramatic “micro-stories.”

---------

### Task Definition
Given:
1. A *Story* describing a situation.
2. A list of *events* already extracted from that story (each with a stable ID and text).

Assign each *event* to exactly one of *five buckets* (TP1–TP5), based on the *ROLE* the event plays in the story (not its surface wording or raw chronology).
Then return a single JSON with **two stages**:
- **Stage 1 (`tp_summaries`)**: one short line per TP describing what that bucket means *for this story*.
- **Stage 2 (`results`)**: per-event labels and rationales.

Provide a brief **rationale** (1–2 sentences) for each event explaining **why** you made the assignment. The rationale must state the reasoning (features of the event and/or its role/relations) and must not be a tautology.

Do not invent new IDs or split items.

---------

### Term Definitions (revised)

- **TP1 — Background (optional)**
  - Remote or biographical context that precedes the main scene/activity. Removing it still leaves TP2 understandable.
  - *Notes:* Using “was/were” alone does **not** imply TP1. TP1 is for background characteristics/history or context from a clearly earlier time.
  - *Cues:* “years ago,” “used to,” “back when,” “in [place] (history).”

- **TP2 — Central Activity / Situation (required)**
  - What the story is about *before* any problems/responses. May include same-scene introductory actions or states that establish the situation.
  - *Heuristics:* Prefer same-scene setup (e.g., “there was…”, “still [state]”, “woke up [state]”) as TP2 rather than TP1.

- **TP3 — Challenge / Problem (optional)**
  - Issues, mistakes, risks, obstacles, or adverse results *about TP2* (including recognition like “noticed/realized [problem]”).
  - *Heuristics:* Events that befall the protagonist (broke, crashed, failed) are TP3 unless clearly chosen actions.

- **TP4 — Response / Action / Decision (optional)**
  - What the protagonist (or an ally/agent) does or decides about TP2/TP3 (requests, rules, fixes, remedies, changes).
  - *Heuristics:* Any remedial/help-seeking step (called, asked, moved, hid, implemented) → TP4. If a response causes an adverse result, the adverse result itself is TP3.

- **TP5 — Outcome / Conclusion / Justification (optional)**
  - Final state, lesson, stance, or **justification**. **No new operative actions or decisions.**
  - **Retrospective actions in reason-clauses** (because/since/as/due to) may be TP5 **only if** they *justify* an outcome/response and **do not introduce the only mention** of that operative step.

---------

### Coverage & Self-Check  *(perform silently; output only the JSON)*
- **Build a Situation Frame (internal):** In one sentence, identify who is involved and what the central activity/state is. Use this to anchor TP2.
- **TP2 presence:** Ensure at least one TP2. If absent, promote the earliest same-scene situation/intro activity/current state to TP2.
- **Current state is not equal to background:** States at story time (e.g., “still [adj]”, “felt [adj]”, “woke up [state]”, “there was…”) are TP2, not TP1, unless they refer to remote history.
- **Intro activity preference:** Same-scene setup actions → TP2 rather than TP1.
- **Adverse results:** Events that befall the protagonist and causes problems → TP3.
- **Remedies & help:** Calls, asks, moves, hides, implements, decides/refuses/opts → TP4.
- **Catalysts vs. problems:** Neutral observations (watched, someone showed) stay in TP2 unless they explicitly introduce a discrepancy/ignorance (then TP3).
- **Justifications:** Reason-clauses (because/since/as/due to) → TP5 *if* they function as justifications/stances and are not the only mention of an operative step; otherwise TP4.
- **Necessity forms:** “had to [verb]”, “ended up [verb-ing]” are actions → TP4 (the harmful event that forced them is TP3).
- **Temporal gates:** TP1 is strictly before the first TP2; no TP2 after TP3/TP4 begins. TP3 and TP4 may interleave; label by role. TP5 conceptually follows problems/responses (it may appear earlier in text if it is a justification).
- **No actions in TP5:** Operative action/decision/speech verbs cannot be TP5 unless appearing only as a retrospective reason in a because/since/as/due to clause and not the sole mention of that step.
- **One bucket per ID:** Each input event appears in exactly one TP. Preserve IDs and copy `original_event` exactly.
- **Rationales:** Name the role relation (e.g., “recognizes problem…”, “remedial action addressing…”, “justifies outcome/decision…”). Avoid tautologies.

---------

### Output Explanation (Two-Stage JSON)
Return **one** JSON object with:
- `tp_summaries`: An object with keys "TP1"–"TP5", each a ≤12-word summary of that bucket **for this story**. Use "-" if unused.
- `results`: An array where each element corresponds to one input event and contains:
  - `id`: the event identifier copied exactly from the input (e.g., "p1", "p2", ...).
  - `original_event`: the exact input event text (byte-for-byte, including case and punctuation).
  - `role`: one of the five buckets (TP1–TP5).
  - `rationale`: one or two sentences explaining the choice based on features/role/relations (no tautologies).

**Order** the `results` in the same order as the input events. Use the same `id` values as provided.

**Formatting requirements:**
- Print ONLY the required JSON with `"tp_summaries"` and `"results"`.
- Wrap the whole JSON in `<JSON>` ... `</JSON>`.
- In the `results` array, each result object must be printed with **one key per line** and consistent indentation (see Examples).

---------

### Examples

**Example 1**

Story:
David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.

Events:
[
  {{ "id":"p1","text":"David noticed weight gain" }},
  {{ "id":"p2","text":"David examined his habits for a reason" }},
  {{ "id":"p3","text":"David realized he ate too much fast food" }},
  {{ "id":"p4","text":"David stopped going to burger places" }},
  {{ "id":"p5","text":"David started a vegetarian diet" }},
  {{ "id":"p6","text":"David felt better after a few weeks" }},
  {{ "id":"p7","text":"David had stopped eating unhealthy foods" }}
]

Output:
<JSON>
{{
  "tp_summaries": {{
    "TP1": "-",
    "TP2": "Current situation motivating a change",
    "TP3": "Specified problem and recognition",
    "TP4": "Remedial actions and behavior change",
    "TP5": "Outcome and justification"
  }},
  "results": [
    {{
      "id":"p1",
      "original_event":"David noticed weight gain",
      "role":"TP2",
      "rationale":"Frames the present situation that the story addresses; serves as the central anchor."
    }},
    {{
      "id":"p2",
      "original_event":"David examined his habits for a reason",
      "role":"TP4",
      "rationale":"Investigative action responding to the situation."
    }},
    {{
      "id":"p3",
      "original_event":"David realized he ate too much fast food",
      "role":"TP3",
      "rationale":"Recognition specifying the problem causing the situation."
    }},
    {{
      "id":"p4",
      "original_event":"David stopped going to burger places",
      "role":"TP4",
      "rationale":"Concrete remedial step addressing the problem."
    }},
    {{
      "id":"p5",
      "original_event":"David started a vegetarian diet",
      "role":"TP4",
      "rationale":"Further decision implementing a response."
    }},
    {{
      "id":"p6",
      "original_event":"David felt better after a few weeks",
      "role":"TP5",
      "rationale":"Final outcome state resulting from prior responses."
    }},
    {{
      "id":"p7",
      "original_event":"David had stopped eating unhealthy foods",
      "role":"TP5",
      "rationale":"Retrospective action cited as a reason (appears in a since-clause); functions as justification, not a new step."
    }}
  ]
}}
</JSON>

**Example 2**

Story:
Eric and his wife had a daughter named Meg. Eric and Meg were very sad when Eric's wife passed away. Eric met a woman and married her 5 years after his wife died. Meg is finally happy with her new stepmother as she is very kind to her.

Events:
[
  {{ "id":"p1","text":"Eric and his wife had Meg" }},
  {{ "id":"p2","text":"Erics wife passed away" }},
  {{ "id":"p3","text":"Eric and Meg were very sad" }},
  {{ "id":"p4","text":"Eric met a woman" }},
  {{ "id":"p5","text":"Eric married the woman five years later" }},
  {{ "id":"p6","text":"Meg was happy with her stepmother" }},
  {{ "id":"p7","text":"Megs stepmother is kind to her" }}
]

Output:
<JSON>
{{
  "tp_summaries": {{
    "TP1": "Family background",
    "TP2": "Loss as central situation",
    "TP3": "Ongoing difficulty after loss",
    "TP4": "Steps toward rebuilding family",
    "TP5": "Positive outcome and reason"
  }},
  "results": [
    {{
      "id":"p1",
      "original_event":"Eric and his wife had Meg",
      "role":"TP1",
      "rationale":"Background family fact preceding the central situation."
    }},
    {{
      "id":"p2",
      "original_event":"Erics wife passed away",
      "role":"TP2",
      "rationale":"Introduces the central situation the story addresses."
    }},
    {{
      "id":"p3",
      "original_event":"Eric and Meg were very sad",
      "role":"TP3",
      "rationale":"Problem state resulting from the central situation."
    }},
    {{
      "id":"p4",
      "original_event":"Eric met a woman",
      "role":"TP4",
      "rationale":"Action initiating a response to the situation."
    }},
    {{
      "id":"p5",
      "original_event":"Eric married the woman five years later",
      "role":"TP4",
      "rationale":"Further decision advancing the response."
    }},
    {{
      "id":"p6",
      "original_event":"Meg was happy with her stepmother",
      "role":"TP5",
      "rationale":"Final outcome state; not an action."
    }},
    {{
      "id":"p7",
      "original_event":"Megs stepmother is kind to her",
      "role":"TP5",
      "rationale":"Justification explaining the positive outcome."
    }}
  ]
}}
</JSON>

**Example 3**

Story:
There was a bug on the wall by the bed. Kate grabbed a shoe and killed it.

Events:
[
  {{ "id":"p1","text":"Bug was on the wall by the bed" }},
  {{ "id":"p2","text":"Kate grabbed a shoe" }},
  {{ "id":"p3","text":"Kate killed the bug" }}
]

Output:
<JSON>
{{
  "tp_summaries": {{
    "TP1": "-",
    "TP2": "Unwanted presence as situation",
    "TP3": "-",
    "TP4": "Actions to remove the problem",
    "TP5": "-"
  }},
  "results": [
    {{
      "id":"p1",
      "original_event":"Bug was on the wall by the bed",
      "role":"TP2",
      "rationale":"Central situation that motivates the response."
    }},
    {{
      "id":"p2",
      "original_event":"Kate grabbed a shoe",
      "role":"TP4",
      "rationale":"Concrete action aimed at addressing the situation."
    }},
    {{
      "id":"p3",
      "original_event":"Kate killed the bug",
      "role":"TP4",
      "rationale":"Culminating action resolving the situation; not a final-state description."
    }}
  ]
}}
</JSON>

**Example 4**

Story:
I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.

Events:
[
  {{ "id":"p1","text":"I bought a cheap jacket" }},
  {{ "id":"p2","text":"Jacket fell apart the next day" }},
  {{ "id":"p3","text":"I concluded more expensive clothes last longer" }}
]

Output:
<JSON>
{{
  "tp_summaries": {{
    "TP1": "-",
    "TP2": "Low-cost purchase as situation",
    "TP3": "Failure of the item",
    "TP4": "-",
    "TP5": "Lesson from the experience"
  }},
  "results": [
    {{
      "id":"p1",
      "original_event":"I bought a cheap jacket",
      "role":"TP2",
      "rationale":"Introduces the central activity that the story concerns."
    }},
    {{
      "id":"p2",
      "original_event":"Jacket fell apart the next day",
      "role":"TP3",
      "rationale":"Adverse result arising from the central activity."
    }},
    {{
      "id":"p3",
      "original_event":"I concluded more expensive clothes last longer",
      "role":"TP5",
      "rationale":"Explicit lesson; a final state of understanding rather than an action."
    }}
  ]
}}
</JSON>

---------

#### Remember
- Label by **role**, not by surface wording or raw chronology; use the Situation Frame to anchor TP2.
- **TP1**: remote/biographical background only (optional). This is either additional personal or location information, or it happened a very long time ago, before the main event of the story.
- **TP2**: central situation (required; may include same-scene introductory actions/states). The focus and the main event/situation of the story.
- **TP3**: problems/obstacles/adverse results (recognition included).
- **TP4**: responses/actions/decisions (by protagonist or allies) addressing TP2/TP3.
- **TP5**: outcomes/lessons/justifications; no new operative actions (retrospective reason-clauses allowed when not the only mention of that step).
- Ensure ≥1 TP2; do not invent or split events; preserve `id` and copy `original_event` exactly.
- Output exactly one JSON wrapped in `<JSON> ... </JSON>` with `tp_summaries` and `results`.
- In `results`, print one key per line with consistent indentation.

---------

### Your Turn

#### Input Format
Story:
{story}

Events:
{events}

---------

#### Output Format

Output: A single JSON object exactly matching the schema described in **Output Explanation**.

Return ONLY one JSON object. Do not output anything before or after it.
Wrap the object inside <JSON> ... </JSON> tags.

Provide output in the following format:

<JSON>
{{
  "tp_summaries": {{
    "TP1":"...",
    "TP2":"...",
    "TP3":"...",
    "TP4":"...",
    "TP5":"..."
  }},
  "results": [
    {{
      "id":"p1",
      "original_event":...,
      "role":...,
      "rationale":...
    }},
    ...
  ]
}}
</JSON>
"""


prompt_stage_extraction3 = """
### Role Assignment
You are an annotator who *clusters* story events into *narrative roles* for short, non-dramatic “micro-stories.”

---

### Task Definition
Given:
1. A *Story* describing a situation.
2. A list of *events* with stable IDs.

Assign each *event* to exactly one of five buckets (TP1–TP5), based on the *role* it plays (not raw chronology).
Return a single JSON with two parts:
- **`tp_summaries`**: one short line per TP (≤12 words). Use “-” if unused.
- **`results`**: per-event labels and rationales.

Each rationale must be 1–2 sentences, explaining the choice (no tautologies).

---

### Term Definitions

- **TP1 — Background**
  Remote/biographical context before main scene.
  *Guidelines:* “years ago,” “used to,” “back when,” distant history.

- **TP2 — Central Activity / Situation (required)**
  The main situation before any problems/responses. Same-scene intro states/actions.

- **TP3 — Challenge / Problem**
  Issues, mistakes, risks, or adverse results linked to TP2.

- **TP4 — Response / Action / Decision**
  What protagonist/others do or decide about TP2/TP3 (calls, fixes, requests…).

- **TP5 — Outcome / Conclusion / Justification**
  Final state, lesson, stance, or justification. No new operative actions.

---

### Self-Check Rules
- Ensure at least one TP2.
- Each event belongs to exactly one TP; preserve IDs and original text.
- Distinguish problems (TP3) vs responses (TP4).
- TP5 only for outcomes/justifications, not operative actions.
- Rationales must state role relations, not repeat labels.

---

### Output Format
Return **one JSON object** wrapped in `<JSON>...</JSON>` with:
- `tp_summaries`: keys TP1–TP5, each ≤12 words.
- `results`: array of objects with:
  - `id` (copied exactly)
  - `original_event` (copied exactly)
  - `role` (TP1–TP5)
  - `rationale` (1–2 sentences)

Keep results in the same order as input.

---------

### Examples

**Example 1**

Story:
David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.

Events:
[
  {{ "id":"p1","text":"David noticed weight gain" }},
  {{ "id":"p2","text":"David examined his habits for a reason" }},
  {{ "id":"p3","text":"David realized he ate too much fast food" }},
  {{ "id":"p4","text":"David stopped going to burger places" }},
  {{ "id":"p5","text":"David started a vegetarian diet" }},
  {{ "id":"p6","text":"David felt better after a few weeks" }},
  {{ "id":"p7","text":"David had stopped eating unhealthy foods" }}
]

Output:
<JSON>
{{
  "tp_summaries": {{
    "TP1": "-",
    "TP2": "Current situation motivating a change",
    "TP3": "Specified problem and recognition",
    "TP4": "Remedial actions and behavior change",
    "TP5": "Outcome and justification"
  }},
  "results": [
    {{
      "id":"p1",
      "original_event":"David noticed weight gain",
      "role":"TP2",
      "rationale":"Frames the present situation that the story addresses; serves as the central anchor."
    }},
    {{
      "id":"p2",
      "original_event":"David examined his habits for a reason",
      "role":"TP4",
      "rationale":"Investigative action responding to the situation."
    }},
    {{
      "id":"p3",
      "original_event":"David realized he ate too much fast food",
      "role":"TP3",
      "rationale":"Recognition specifying the problem causing the situation."
    }},
    {{
      "id":"p4",
      "original_event":"David stopped going to burger places",
      "role":"TP4",
      "rationale":"Concrete remedial step addressing the problem."
    }},
    {{
      "id":"p5",
      "original_event":"David started a vegetarian diet",
      "role":"TP4",
      "rationale":"Further decision implementing a response."
    }},
    {{
      "id":"p6",
      "original_event":"David felt better after a few weeks",
      "role":"TP5",
      "rationale":"Final outcome state resulting from prior responses."
    }},
    {{
      "id":"p7",
      "original_event":"David had stopped eating unhealthy foods",
      "role":"TP5",
      "rationale":"Retrospective action cited as a reason (appears in a since-clause); functions as justification, not a new step."
    }}
  ]
}}
</JSON>

**Example 2**

Story:
Eric and his wife had a daughter named Meg. Eric and Meg were very sad when Eric's wife passed away. Eric met a woman and married her 5 years after his wife died. Meg is finally happy with her new stepmother as she is very kind to her.

Events:
[
  {{ "id":"p1","text":"Eric and his wife had Meg" }},
  {{ "id":"p2","text":"Erics wife passed away" }},
  {{ "id":"p3","text":"Eric and Meg were very sad" }},
  {{ "id":"p4","text":"Eric met a woman" }},
  {{ "id":"p5","text":"Eric married the woman five years later" }},
  {{ "id":"p6","text":"Meg was happy with her stepmother" }},
  {{ "id":"p7","text":"Megs stepmother is kind to her" }}
]

Output:
<JSON>
{{
  "tp_summaries": {{
    "TP1": "Family background",
    "TP2": "Loss as central situation",
    "TP3": "Ongoing difficulty after loss",
    "TP4": "Steps toward rebuilding family",
    "TP5": "Positive outcome and reason"
  }},
  "results": [
    {{
      "id":"p1",
      "original_event":"Eric and his wife had Meg",
      "role":"TP1",
      "rationale":"Background family fact preceding the central situation."
    }},
    {{
      "id":"p2",
      "original_event":"Erics wife passed away",
      "role":"TP2",
      "rationale":"Introduces the central situation the story addresses."
    }},
    {{
      "id":"p3",
      "original_event":"Eric and Meg were very sad",
      "role":"TP3",
      "rationale":"Problem state resulting from the central situation."
    }},
    {{
      "id":"p4",
      "original_event":"Eric met a woman",
      "role":"TP4",
      "rationale":"Action initiating a response to the situation."
    }},
    {{
      "id":"p5",
      "original_event":"Eric married the woman five years later",
      "role":"TP4",
      "rationale":"Further decision advancing the response."
    }},
    {{
      "id":"p6",
      "original_event":"Meg was happy with her stepmother",
      "role":"TP5",
      "rationale":"Final outcome state; not an action."
    }},
    {{
      "id":"p7",
      "original_event":"Megs stepmother is kind to her",
      "role":"TP5",
      "rationale":"Justification explaining the positive outcome."
    }}
  ]
}}
</JSON>

**Example 3**

Story:
There was a bug on the wall by the bed. Kate grabbed a shoe and killed it.

Events:
[
  {{ "id":"p1","text":"Bug was on the wall by the bed" }},
  {{ "id":"p2","text":"Kate grabbed a shoe" }},
  {{ "id":"p3","text":"Kate killed the bug" }}
]

Output:
<JSON>
{{
  "tp_summaries": {{
    "TP1": "-",
    "TP2": "Unwanted presence as situation",
    "TP3": "-",
    "TP4": "Actions to remove the problem",
    "TP5": "-"
  }},
  "results": [
    {{
      "id":"p1",
      "original_event":"Bug was on the wall by the bed",
      "role":"TP2",
      "rationale":"Central situation that motivates the response."
    }},
    {{
      "id":"p2",
      "original_event":"Kate grabbed a shoe",
      "role":"TP4",
      "rationale":"Concrete action aimed at addressing the situation."
    }},
    {{
      "id":"p3",
      "original_event":"Kate killed the bug",
      "role":"TP4",
      "rationale":"Culminating action resolving the situation; not a final-state description."
    }}
  ]
}}
</JSON>

**Example 4**

Story:
I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.

Events:
[
  {{ "id":"p1","text":"I bought a cheap jacket" }},
  {{ "id":"p2","text":"Jacket fell apart the next day" }},
  {{ "id":"p3","text":"I concluded more expensive clothes last longer" }}
]

Output:
<JSON>
{{
  "tp_summaries": {{
    "TP1": "-",
    "TP2": "Low-cost purchase as situation",
    "TP3": "Failure of the item",
    "TP4": "-",
    "TP5": "Lesson from the experience"
  }},
  "results": [
    {{
      "id":"p1",
      "original_event":"I bought a cheap jacket",
      "role":"TP2",
      "rationale":"Introduces the central activity that the story concerns."
    }},
    {{
      "id":"p2",
      "original_event":"Jacket fell apart the next day",
      "role":"TP3",
      "rationale":"Adverse result arising from the central activity."
    }},
    {{
      "id":"p3",
      "original_event":"I concluded more expensive clothes last longer",
      "role":"TP5",
      "rationale":"Explicit lesson; a final state of understanding rather than an action."
    }}
  ]
}}
</JSON>

---------

#### Remember
- Label by **role**, not by surface wording or raw chronology; use the Situation Frame to anchor TP2.
- **TP1**: remote/biographical background only (optional). This is either additional personal or location information, or it happened a very long time ago, before the main event of the story.
- **TP2**: central situation (required; may include same-scene introductory actions/states). The focus and the main event/situation of the story.
- **TP3**: problems/obstacles/adverse results (recognition included).
- **TP4**: responses/actions/decisions (by protagonist or allies) addressing TP2/TP3.
- **TP5**: outcomes/lessons/justifications; no new operative actions (retrospective reason-clauses allowed when not the only mention of that step).
- Ensure ≥1 TP2; do not invent or split events; preserve `id` and copy `original_event` exactly.
- Output exactly one JSON wrapped in `<JSON> ... </JSON>` with `tp_summaries` and `results`.
- In `results`, print one key per line with consistent indentation.

---------

### Your Turn

#### Input Format
Story:
{story}

Events:
{phrases}

---------

#### Output Format

Output: A single JSON object exactly matching the schema described in **Output Explanation**.

Return ONLY one JSON object. Do not output anything before or after it.
Wrap the object inside <JSON> ... </JSON> tags.

Provide output in the following format:

<JSON>
{{
  "tp_summaries": {{
    "TP1":"...",
    "TP2":"...",
    "TP3":"...",
    "TP4":"...",
    "TP5":"..."
  }},
  "results": [
    {{
      "id":"p1",
      "original_event":...,
      "role":...,
      "rationale":...
    }},
    ...
  ]
}}
</JSON>
"""
