prompt_group_abstraction = """
### Role Assignment
You are an analytical assistant that generalizes grouped narrative phrases into higher-level conceptual “kernel names.”
You read a short **Story** and an accompanying list of grouped **Phrases**, where each group shares a narrative role (TP1–TP5).
For each group you output one concise, abstract kernel name capturing the group’s core idea, considering its function in the story.

---------

### Task Definition
Given:
1. A *Story* describing a situation.
2. A list of *Groups*, each with a **role_code** and a set of member *Phrases* (each phrase is a concrete element, event, feeling, judgment, or action).

Produce for **each group** exactly **one** **kernel name** that:
- Expresses the central concept of the **group as a whole** in a **more general / abstract** manner than the member phrases.
- You must use the story content as primary evidence.
- Reflects the group’s **role** in the overall story (e.g., background, introduction/problem detection, action/decision, challenge, conclusion/lesson) and the **relations** among its member phrases.
- Uses a concise **noun or noun phrase** (prefer 1–5 words), neutral in tone unless sentiment is essential.
- **Does not** introduce new specific details absent from the story.
- **Single kernel only**: Output one consistent kernel (no multiple kernels). Using “and/or” is allowed only when forming a **single coherent concept**, not to join disparate kernels. If member phrases diverge, base the kernel on the **most important** elements (dominant theme) and explain the linkage in the rationale.

Also provide a brief **rationale** (1–2 sentences) explaining how the member phrases and their role/relations justify the chosen kernel. The rationale must state the reasoning (features/role/relations), not a tautology.

---------

### Role Codes (for guidance)
- **TP1**: background/context
- **TP2**: introduction or problem detection (main event emerges)
- **TP3**: action/strategy/decision regarding the main event
- **TP4**: challenge/obstacle/complication regarding the main event
- **TP5**: conclusion/final state/learned lesson

Use the story content as primary evidence. Treat the role code as a helpful hint. If content and role appear misaligned, still produce the best kernel from content and set `role_consistency` accordingly.

---------

### Term Definitions
- **Phrase:** A specific textual fragment describing an event, state, perception, emotion, evaluation, or decision.
- **Group:** A set of phrases clustered by narrative role (at most one group per TP present in the input).
- **Kernel Name:** A concise, more abstract concept label summarizing a group’s essential meaning (e.g., “health-oriented behavior change”).
- **Abstraction / More General:** Remove incidental specifics (time, place, proper nouns) to reveal a broader category or concept.
- **Role / Relations:** The functional contribution of the group within the story and how its member phrases connect.

---------

### Output Explanation
Return a **single JSON object** with an array `results`. Each element corresponds to one input **group** and contains:
- `role_code`: the group role code copied exactly from the input (e.g., "TP2").
- `kernel_name`: your generalized concept (string; one coherent kernel only).
- `rationale`: 1–2 sentences explaining how the member phrases and their relations support the kernel (state the reason; avoid tautology).

**Ordering:** Preserve the input group order.

---------

### Examples

**Example 1**

Story:
“David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better.”

Groups:
[
  {{
    "role_code": "TP2",
    "phrases": [
      {{ "id":"p1","text":"David noticed weight gain" }}
    ]
  }},
  {{
    "role_code": "TP3",
    "phrases": [
      {{ "id":"p2","text":"Examined his habits for a reason" }},
      {{ "id":"p3","text":"Realized he ate too much fast food" }},
      {{ "id":"p4","text":"Stopped going to burger places" }},
      {{ "id":"p5","text":"Started a vegetarian diet" }}
    ]
  }},
  {{
    "role_code": "TP5",
    "phrases": [
      {{ "id":"p6","text":"Felt better after a few weeks" }}
    ]
  }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "role_code": "TP2",
      "kernel_name": "weight gain awareness",
      "rationale": "Recognition of a problematic health change initiates the subsequent problem-solving sequence."
    }},
    {{
      "role_code": "TP3",
      "kernel_name": "health-oriented behavior change",
      "rationale": "A chain of self-assessment, cause identification, trigger avoidance, and adopting a new diet forms a coherent change strategy."
    }},
    {{
      "role_code": "TP5",
      "kernel_name": "improved well-being",
      "rationale": "A positive outcome follows the behavioral changes, indicating likely benefits from the prior actions."
    }}
  ]
}}
</JSON>

---------

**Example 2**

Story:
“Eric and his wife had a daughter named Meg. Eric and Meg were very sad when Eric's wife passed away. Eric met a woman and married her 5 years after his wife died. Meg is finally happy with her new stepmother.”

Groups:
[
  {{
    "role_code": "TP1",
    "phrases": [
      {{ "id":"p1","text":"Eric and his wife had Meg" }}
    ]
  }},
  {{
    "role_code": "TP2",
    "phrases": [
      {{ "id":"p2","text":"Erics wife passed away" }},
      {{ "id":"p3","text":"Eric and Meg were very sad" }}
    ]
  }},
  {{
    "role_code": "TP3",
    "phrases": [
      {{ "id":"p4","text":"Eric met a woman" }},
      {{ "id":"p5","text":"Five years later Eric married the woman" }}
    ]
  }},
  {{
    "role_code": "TP5",
    "phrases": [
      {{ "id":"p6","text":"Meg was happy with her stepmother" }}
    ]
  }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "role_code": "TP1",
      "kernel_name": "family formation",
      "rationale": "The birth establishes the family context within which later events occur."
    }},
    {{
      "role_code": "TP2",
      "kernel_name": "spousal bereavement and grief",
      "rationale": "A death event and the ensuing sadness function together as the initiating loss that shapes subsequent choices."
    }},
    {{
      "role_code": "TP3",
      "kernel_name": "remarriage after bereavement",
      "rationale": "Post-loss relationship development progresses from meeting to forming a new marital bond."
    }},
    {{
      "role_code": "TP5",
      "kernel_name": "positive stepfamily adjustment",
      "rationale": "The child's happiness indicates successful adaptation to the new family structure.",
    }}
  ]
}}
</JSON>

---------

**Example 3**

Story:
“There was a bug on the wall by the bed. Kate grabbed a shoe and killed it.”

Groups:
[
  {{
    "role_code": "TP2",
    "phrases": [
      {{ "id":"p1","text":"Bug was on the wall by the bed" }}
    ]
  }},
  {{
    "role_code": "TP3",
    "phrases": [
      {{ "id":"p2","text":"Kate grabbed a shoe" }},
      {{ "id":"p3","text":"Kate killed the bug" }}
    ]
  }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "role_code": "TP2",
      "kernel_name": "household pest presence",
      "rationale": "An insect in a living space creates a nuisance that prompts action."
    }},
    {{
      "role_code": "TP3",
      "kernel_name": "improvised pest control",
      "rationale": "Selecting a handy object and eliminating the bug constitute a single, practical removal strategy."
    }}
  ]
}}
</JSON>

---------

**Example 4**

Story:
“I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

Groups:
[
  {{
    "role_code": "TP2",
    "phrases": [
      {{ "id":"p1","text":"Bought a cheap jacket" }}
    ]
  }},
  {{
    "role_code": "TP4",
    "phrases": [
      {{ "id":"p2","text":"Jacket fell apart the next day" }}
    ]
  }},
  {{
    "role_code": "TP5",
    "phrases": [
      {{ "id":"p3","text":"Concluded more expensive clothes last longer" }}
    ]
  }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "role_code": "TP2",
      "kernel_name": "low-cost purchase decision",
      "rationale": "The buyer opts for a minimal-price item, setting up a quality tradeoff."
    }},
    {{
      "role_code": "TP4",
      "kernel_name": "premature product failure",
      "rationale": "Rapid breakdown serves as the complication that motivates a revised purchasing rule."
    }},
    {{
      "role_code": "TP5",
      "kernel_name": "quality-over-cost heuristic",
      "rationale": "The story culminates in a generalized rule favoring durability over low price."
    }}
  ]
}}
</JSON>

---------

### Your Turn

#### Input Format
Story:
{story}

Groups:
{groups}


#### Output Format
Remember:
- For each **group**, output exactly **one** coherent `kernel_name` and a reasoning `rationale`.
- Preserve `role_code` exactly as given.
- Use concise noun/noun-phrase (1–5 words), neutral tone, no invented specifics.
- Do **not** output multiple kernels; do **not** join unrelated kernels with “and/or”.

Output: A single JSON object matching the schema below. Return ONLY one JSON object. Wrap it inside <JSON> ... </JSON> tags.

<JSON>
{{
  "results": [
    {{
      "role_code": "TP2",
      "kernel_name": "...",
      "rationale": "..."
    }}
  ]
}}
</JSON>
"""




prompt_group_abstraction2 = """

### Role Assignment
You are an analytical assistant that generalizes grouped narrative phrases into higher-level conceptual “kernel names.”
You read a short **Story** and an accompanying list of grouped **Phrases**, where each group shares a narrative role (TP1–TP5).
For each group you output one concise, abstract kernel name capturing the group’s core idea, considering its function in the story.

---------

### Task Definition
Given:
1. A *Story* describing a situation.
2. A list of *Groups*, each with a **role_code** and a set of member *Phrases* (each phrase is a concrete element, event, feeling, judgment, or action).

Produce for **each group** exactly **one** **kernel name** that:
- Expresses the central concept of the **group as a whole** in a **more general / abstract** manner than the member phrases.
- You must use the story content as primary evidence.
- Reflects the group’s **role** in the overall story (e.g., background, introduction/problem detection, challenge, action/decision, conclusion/lesson) and the **relations** among its member phrases.
- Uses a concise **noun or noun phrase** (prefer 1–5 words), neutral in tone unless sentiment is essential.
- **Does not** introduce new specific details absent from the story.
- **Single kernel only**: Output one consistent kernel (no multiple kernels). Using “and/or” is allowed only when forming a **single coherent concept**, not to join disparate kernels. If member phrases diverge, base the kernel on the **most important** elements (dominant theme) and explain the linkage in the rationale.

Also provide a brief **rationale** (1–2 sentences) explaining how the member phrases and their role/relations justify the chosen kernel. The rationale must state the reasoning (features/role/relations), not a tautology.

---------

### Role Codes (for guidance)
- **TP1**: background/context
- **TP2**: introduction or problem detection (main event emerges)
- **TP3**: challenge/obstacle/complication regarding the main event
- **TP4**: action/strategy/decision regarding the main event
- **TP5**: conclusion/final state/learned lesson

Use the story content as primary evidence. Treat the role code as a helpful hint. If content and role appear misaligned, still produce the best kernel from content and set `role_consistency` accordingly.

---------

### Term Definitions
- **Phrase:** A specific textual fragment describing an event, state, perception, emotion, evaluation, or decision.
- **Group:** A set of phrases clustered by narrative role (at most one group per TP present in the input).
- **Kernel Name:** A concise, more abstract concept label summarizing a group’s essential meaning (e.g., “health-oriented behavior change”).
- **Abstraction / More General:** Remove incidental specifics (time, place, proper nouns) to reveal a broader category or concept.
- **Role / Relations:** The functional contribution of the group within the story and how its member phrases connect.

---------

### Output Explanation
Return a **single JSON object** with an array `results`. Each element corresponds to one input **group** and contains:
- `role_code`: the group role code copied exactly from the input (e.g., "TP2").
- `kernel_name`: your generalized concept (string; one coherent kernel only).
- `rationale`: 1–2 sentences explaining how the member phrases and their relations support the kernel (state the reason; avoid tautology).

**Ordering:** Preserve the input group order.

---------

### Examples

**Example 1**

Story:
“David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.”

Groups:
[
  {{
    "role_code": "TP2",
    "phrases": [
      {{ "id":"p1","text":"David noticed weight gain" }}
    ]
  }},
  {{
    "role_code": "TP3",
    "phrases": [
      {{ "id":"p2","text":"David realized he ate too much fast food" }}
    ]
  }},
  {{
    "role_code": "TP4",
    "phrases": [
      {{ "id":"p3","text":"David examined his habits for a reason" }},
      {{ "id":"p4","text":"David stopped going to burger places" }},
      {{ "id":"p5","text":"David started a vegetarian diet" }}
    ]
  }},
  {{
    "role_code": "TP5",
    "phrases": [
      {{ "id":"p6","text":"David felt better after a few weeks" }},
      {{ "id":"p7","text":"David had stopped eating unhealthy foods" }}
    ]
  }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "role_code": "TP2",
      "kernel_name": "weight gain awareness",
      "rationale": "The recognition of increased weight establishes the central situation that motivates further interpretation and action."
    }},
    {{
      "role_code": "TP3",
      "kernel_name": "diet-related problem identification",
      "rationale": "Realizing the fast-food overconsumption specifies the underlying issue generating the central situation."
    }},
    {{
      "role_code": "TP4",
      "kernel_name": "health-oriented behavior change",
      "rationale": "The self-assessment and dietary changes function as coordinated responses intended to address the identified problem."
    }},
    {{
      "role_code": "TP5",
      "kernel_name": "improved well-being",
      "rationale": "Feeling better and referencing the cessation of unhealthy eating depict the final positive state and its justification."
    }}
  ]
}}
</JSON>

---------

**Example 2**

Story:
“Eric and his wife had a daughter named Meg. Eric and Meg were very sad when Eric's wife passed away. Eric met a woman and married her 5 years after his wife died. Meg is finally happy with her new stepmother as she is very kind to her.”

Groups:
[
  {{
    "role_code": "TP1",
    "phrases": [
      {{ "id":"p1","text":"Eric and his wife had Meg" }}
    ]
  }},
  {{
    "role_code": "TP2",
    "phrases": [
      {{ "id":"p2","text":"Eric’s wife passed away" }}
    ]
  }},
  {{
    "role_code": "TP3",
    "phrases": [
      {{ "id":"p3","text":"Eric and Meg were very sad" }}
    ]
  }},
  {{
    "role_code": "TP4",
    "phrases": [
      {{ "id":"p4","text":"Eric met a woman" }},
      {{ "id":"p5","text":"Eric married the woman five years later" }}
    ]
  }},
  {{
    "role_code": "TP5",
    "phrases": [
      {{ "id":"p6","text":"Meg was happy with her stepmother" }},
      {{ "id":"p7","text":"Meg’s stepmother is kind to her" }}
    ]
  }}
]


Output:
<JSON>
{{
  "results": [
    {{
      "role_code": "TP1",
      "kernel_name": "family background",
      "rationale": "Meg’s birth provides remote biographical context that precedes the central situation."
    }},
    {{
      "role_code": "TP2",
      "kernel_name": "spousal loss",
      "rationale": "The death of Eric’s wife establishes the main situation that shapes subsequent emotional and relational developments."
    }},
    {{
      "role_code": "TP3",
      "kernel_name": "bereavement distress",
      "rationale": "The shared sadness represents the immediate emotional problem arising from the central loss."
    }},
    {{
      "role_code": "TP4",
      "kernel_name": "post-loss relationship rebuilding",
      "rationale": "Meeting a new partner and eventually marrying her constitute actions responding to the emotional and familial disruption."
    }},
    {{
      "role_code": "TP5",
      "kernel_name": "positive stepfamily adjustment",
      "rationale": "Meg’s happiness and its explanation reflect the final improved state and its justification."
    }}
  ]
}}
</JSON>

---------

**Example 3**

Story:
“There was a bug on the wall by the bed. Kate grabbed a shoe and killed it.”

Groups:
[
  {{
    "role_code": "TP2",
    "phrases": [
      {{ "id":"p1","text":"Bug was on the wall by the bed" }}
    ]
  }},
  {{
    "role_code": "TP4",
    "phrases": [
      {{ "id":"p2","text":"Kate grabbed a shoe" }},
      {{ "id":"p3","text":"Kate killed the bug" }}
    ]
  }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "role_code": "TP2",
      "kernel_name": "household pest presence",
      "rationale": "The bug’s location establishes the central situation prompting intervention."
    }},
    {{
      "role_code": "TP4",
      "kernel_name": "direct pest removal",
      "rationale": "Grabbing a nearby tool and killing the bug function as coordinated actions addressing the situation."
    }}
  ]
}}
</JSON>

---------

**Example 4**

Story:
“I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

Groups:
[
  {{
    "role_code": "TP2",
    "phrases": [
      {{ "id":"p1","text":"Bought a cheap jacket" }}
    ]
  }},
  {{
    "role_code": "TP3",
    "phrases": [
      {{ "id":"p2","text":"Jacket fell apart the next day" }}
    ]
  }},
  {{
    "role_code": "TP5",
    "phrases": [
      {{ "id":"p3","text":"Concluded more expensive clothes last longer" }}
    ]
  }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "role_code": "TP2",
      "kernel_name": "low-cost purchase decision",
      "rationale": "The buyer opts for a minimal-price item, setting up a quality tradeoff."
    }},
    {{
      "role_code": "TP3",
      "kernel_name": "product failure",
      "rationale": "The rapid breakdown represents the adverse outcome arising from the initial purchase."
    }},
    {{
      "role_code": "TP5",
      "kernel_name": "durability-based buying lesson",
      "rationale": "The concluding insight summarizes the final evaluative stance supported by the earlier events."
    }}
  ]
}}
</JSON>

---------

### Your Turn

#### Input Format
Story:
{story}

Groups:
{groups}


#### Output Format
Remember:
- For each **group**, output exactly **one** coherent `kernel_name` and a reasoning `rationale`.
- Preserve `role_code` exactly as given.
- Use concise noun/noun-phrase (1–5 words), neutral tone, no invented specifics.
- Do **not** output multiple kernels; do **not** join unrelated kernels with “and/or”.

Output: A single JSON object matching the schema below. Return ONLY one JSON object. Wrap it inside <JSON> ... </JSON> tags.

<JSON>
{{
  "results": [
    {{
      "role_code": "TP2",
      "kernel_name": "...",
      "rationale": "..."
    }}
  ]
}}
</JSON>
"""


prompt_group_abstraction3 = """
### Role Assignment
You are an analytical assistant that generalizes grouped narrative phrases into higher-level conceptual “kernel names.”
You read a short **Story** and an accompanying list of grouped **Phrases**, where each group shares a narrative role (TP1–TP5).
For each group you output one concise, abstract kernel name capturing the group’s core idea, considering its function in the story.

---------

### Task Definition
Given:
1. A *Story* describing a situation.
2. A list of *Groups*, each with a **role_code** and a set of member *Phrases* (each phrase is a concrete element, event, feeling, judgment, or action).

Produce for **each group** exactly **one** **kernel name** that:
- Expresses the central concept of the **group as a whole** in a **more general / abstract** manner than the member phrases.
- Uses **all phrases in the group together** as evidence for a single unified concept (do not base the kernel on just one phrase unless the others are clearly minor variants).
- You must use the story content as primary evidence.
- Reflects the group’s **role** in the overall story (e.g., background, introduction/problem detection, challenge, action/decision, conclusion/lesson) and the **relations** among its member phrases.
- Uses a concise **[MODIFIER]_[ROOT]** form (defined below), with exactly **two tokens** in **UPPERCASE**, separated by a single underscore.
- **Does not** introduce new specific details absent from the story.
- **Single kernel only**: Output one consistent kernel (no multiple kernels). Using “and/or” is allowed only when forming a **single coherent concept**, not to join disparate kernels. If member phrases diverge, base the kernel on the **most important** elements (dominant theme) and explain the linkage in the rationale.

---------

### Kernel Name Structure: ROOT and MODIFIER

Each **kernel_name** must be of the form **[MODIFIER]_[ROOT]**, where:

#### ROOT
- **Purpose:** Name the core event/state/concept for the **entire group** in **one noun-like word**.
- **How to find it for a group:**
  1) Consider all phrases in the group together and identify the **shared semantic head** — what is mainly happening or what state mainly holds across the phrases.
  2) Convert that head to a **noun-like** form if needed (e.g., verb → nominalization) while preserving meaning at a slightly more abstract level.
- **Candidate evaluation (pros/cons to consider):**
  - **Pros:** carries clear signal from the story and the grouped phrases; is more general than any single phrase but still specific to this group’s meaning.
  - **Cons:** lacks story signal; is so generic it could apply to almost anything; simply repeats a surface verb without abstraction.
- **Not allowed (hard ban as ROOT):**
  - Words that are **overly general and story-agnostic**:  
    `EVENT, ACTION, ACTIVITY, SITUATION, OCCURRENCE, THING, ITEM, OBJECT, PROCESS, INFORMATION, KNOWLEDGE, STUFF`.
  - These fail to convey meaningful content about the group.

#### MODIFIER
- **Purpose:** Provide a minimal but informative **explanation or anchor** for the ROOT in **one word**.
- **How to choose it for a group:**
  - **Domain/category option:** Prefer a **domain-level or category-level** noun that clearly ties the ROOT to this story (e.g., HEALTH, FAMILY, DIET, RELATIONSHIP, PRODUCT, WORK), rather than a single-instance object or proper name.
  - **Quality option:** Alternatively, you may use a **single-word quality adjective** when the group mainly emphasizes **tempo, degree, polarity, or quality** (e.g., POSITIVE, NEGATIVE, CHEAP, RAPID).
  - **Focus choice:** Decide whether **domain** or **quality** better reflects the dominant focus of the grouped phrases and their narrative role.
  - **Non-redundancy:** The modifier must be **different from the ROOT** and must add **new information** rather than simply restating or paraphrasing it.
- **Candidate evaluation (pros/cons to consider):**
  - **Pros:** clearly anchors the ROOT to a meaningful domain or quality present in the grouped phrases; is minimal yet informative.
  - **Cons:** too generic or meta; redundant with the ROOT; overfitted to a one-off detail or name that does not generalize.
- **Not allowed (hard ban as MODIFIER):**
  - Generic or meta words that **do not add story signal**:  
    `GENERAL, QUALITY, THING, STUFF, EVENT, CONTEXT, TOPIC, AREA, DOMAIN, PEOPLE, PERSON, ENTITY, KNOWLEDGE, INFORMATION`.
  - Overly specific **proper names** or **single-instance items** when a broader domain or category is available (e.g., prefer CLOTHING over a specific brand name).
- **Formatting rule:**
  - Both ROOT and MODIFIER must be **UPPERCASE**, with no spaces, and combined as `MODIFIER_ROOT` with **exactly one underscore**.

---------

### Role Codes (for guidance)
- **TP1**: background/context
- **TP2**: introduction or problem detection (main event emerges)
- **TP3**: challenge/obstacle/complication regarding the main event
- **TP4**: action/strategy/decision regarding the main event
- **TP5**: conclusion/final state/learned lesson

Use the story content as primary evidence. Treat the role code as a helpful hint. If content and role appear misaligned, still produce the best kernel from content and set `role_consistency` accordingly.

---------

### Term Definitions
- **Phrase:** A specific textual fragment describing an event, state, perception, emotion, evaluation, or decision.
- **Group:** A set of phrases clustered by narrative role (at most one group per TP present in the input).
- **Kernel Name:** A concise, more abstract concept label summarizing a group’s essential meaning, expressed in a **[MODIFIER]_[ROOT]** frame (two UPPERCASE tokens separated by a single underscore).
- **Abstraction / More General:** Remove incidental specifics (time, place, proper nouns) to reveal a broader category or concept, while preserving the core event/state shared by the group’s phrases.
- **Role / Relations:** The functional contribution of the group within the story and how its member phrases connect (e.g., shared cause, shared consequence, shared topic).

---------

### Output Explanation
Return a **single JSON object** with an array `results`. Each element corresponds to one input **group** and contains:
- `role_code`: the group role code copied exactly from the input (e.g., "TP2").
- `kernel_name`: your generalized concept (string; one coherent kernel only) in **[MODIFIER]_[ROOT]** format, UPPERCASE, exactly two tokens.
- `rationale`: 1–2 sentences explaining how the member phrases and their role/relations justify the chosen kernel (state the reasoning (features/role/relations), not a tautology). You should reference both the abstract ROOT idea and how the MODIFIER anchors it to the story’s domain or quality.

**Ordering:** Preserve the input group order.

---------

### Examples

**Example 1**

Story:
“David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.”

Groups:
[
  {{
    "role_code": "TP2",
    "phrases": [
      {{ "id":"p1","text":"David noticed weight gain" }}
    ]
  }},
  {{
    "role_code": "TP3",
    "phrases": [
      {{ "id":"p2","text":"David realized he ate too much fast food" }}
    ]
  }},
  {{
    "role_code": "TP4",
    "phrases": [
      {{ "id":"p3","text":"David examined his habits for a reason" }},
      {{ "id":"p4","text":"David stopped going to burger places" }},
      {{ "id":"p5","text":"David started a vegetarian diet" }}
    ]
  }},
  {{
    "role_code": "TP5",
    "phrases": [
      {{ "id":"p6","text":"David felt better after a few weeks" }},
      {{ "id":"p7","text":"David had stopped eating unhealthy foods" }}
    ]
  }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "role_code": "TP2",
      "kernel_name": "HEALTH_AWARENESS",
      "rationale": "Noticing the weight gain marks a recognition of a change in physical condition, so AWARENESS captures the core event at an abstract level while HEALTH anchors it to the bodily domain signaled by the story."
    }},
    {{
      "role_code": "TP3",
      "kernel_name": "DIET_PROBLEM",
      "rationale": "Realizing he ate too much fast food identifies an underlying issue rather than just a behavior, so PROBLEM generalizes the difficulty while DIET specifies that the difficulty concerns eating habits."
    }},
    {{
      "role_code": "TP4",
      "kernel_name": "LIFESTYLE_CHANGE",
      "rationale": "Examining habits, stopping burger visits, and starting a vegetarian diet together describe a coordinated shift in ongoing patterns, so CHANGE captures the abstract transformation while LIFESTYLE ties it to daily behavioral routines."
    }},
    {{
      "role_code": "TP5",
      "kernel_name": "HEALTH_IMPROVEMENT",
      "rationale": "Feeling better and linking it to stopping unhealthy foods depict an enhanced state that follows earlier actions, so IMPROVEMENT expresses the general positive shift while HEALTH grounds it in physical well-being."
    }}
  ]
}}
</JSON>

---------

**Example 2**

Story:
“Eric and his wife had a daughter named Meg. Eric and Meg were very sad when Eric's wife passed away. Eric met a woman and married her 5 years after his wife died. Meg is finally happy with her new stepmother as she is very kind to her.”

Groups:
[
  {{
    "role_code": "TP1",
    "phrases": [
      {{ "id":"p1","text":"Eric and his wife had Meg" }}
    ]
  }},
  {{
    "role_code": "TP2",
    "phrases": [
      {{ "id":"p2","text":"Eric’s wife passed away" }}
    ]
  }},
  {{
    "role_code": "TP3",
    "phrases": [
      {{ "id":"p3","text":"Eric and Meg were very sad" }}
    ]
  }},
  {{
    "role_code": "TP4",
    "phrases": [
      {{ "id":"p4","text":"Eric met a woman" }},
      {{ "id":"p5","text":"Eric married the woman five years later" }}
    ]
  }},
  {{
    "role_code": "TP5",
    "phrases": [
      {{ "id":"p6","text":"Meg was happy with her stepmother" }},
      {{ "id":"p7","text":"Meg’s stepmother is kind to her" }}
    ]
  }}
]


Output:
<JSON>
{{
  "results": [
    {{
      "role_code": "TP1",
      "kernel_name": "FAMILY_FORMATION",
      "rationale": "The birth of Meg establishes how the family is constituted before later events, so FORMATION captures the general creation of the family unit while FAMILY identifies the relational domain involved."
    }},
    {{
      "role_code": "TP2",
      "kernel_name": "SPOUSAL_LOSS",
      "rationale": "The wife’s death is the central disruptive event that shapes subsequent emotions and actions, so LOSS abstracts the core experience while SPOUSAL specifies that it concerns the marital relationship."
    }},
    {{
      "role_code": "TP3",
      "kernel_name": "BEREAVEMENT_DISTRESS",
      "rationale": "Eric and Meg’s sadness reflects their emotional reaction to the death, so DISTRESS generalizes the negative state while BEREAVEMENT links it directly to grief over a death."
    }},
    {{
      "role_code": "TP4",
      "kernel_name": "RELATIONSHIP_REBUILDING",
      "rationale": "Meeting a new partner and eventually marrying her are steps in reconstructing family life after loss, so REBUILDING summarizes the restorative process while RELATIONSHIP indicates that it occurs in the intimate social domain."
    }},
    {{
      "role_code": "TP5",
      "kernel_name": "STEPFAMILY_ADJUSTMENT",
      "rationale": "Meg’s happiness with her kind stepmother shows a re-stabilized family configuration, so ADJUSTMENT captures the achieved new equilibrium while STEPFAMILY specifies that it concerns integration into a blended family."
    }}
  ]
}}
</JSON>

---------

**Example 3**

Story:
“There was a bug on the wall by the bed. Kate grabbed a shoe and killed it.”

Groups:
[
  {{
    "role_code": "TP2",
    "phrases": [
      {{ "id":"p1","text":"Bug was on the wall by the bed" }}
    ]
  }},
  {{
    "role_code": "TP4",
    "phrases": [
      {{ "id":"p2","text":"Kate grabbed a shoe" }},
      {{ "id":"p3","text":"Kate killed the bug" }}
    ]
  }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "role_code": "TP2",
      "kernel_name": "PEST_PRESENCE",
      "rationale": "The bug’s location near the bed sets up an unwanted creature being in the living space, so PRESENCE abstracts the state of being there while PEST identifies the nuisance-animal domain."
    }},
    {{
      "role_code": "TP4",
      "kernel_name": "PEST_REMOVAL",
      "rationale": "Grabbing a shoe and killing the bug are coordinated steps to eliminate the intruder, so REMOVAL expresses the core outcome while PEST connects it to getting rid of an unwanted insect."
    }}
  ]
}}
</JSON>

---------

**Example 4**

Story:
“I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.”

Groups:
[
  {{
    "role_code": "TP2",
    "phrases": [
      {{ "id":"p1","text":"Bought a cheap jacket" }}
    ]
  }},
  {{
    "role_code": "TP3",
    "phrases": [
      {{ "id":"p2","text":"Jacket fell apart the next day" }}
    ]
  }},
  {{
    "role_code": "TP5",
    "phrases": [
      {{ "id":"p3","text":"Concluded more expensive clothes last longer" }}
    ]
  }}
]

Output:
<JSON>
{{
  "results": [
    {{
      "role_code": "TP2",
      "kernel_name": "CHEAP_PURCHASE",
      "rationale": "Buying a very inexpensive jacket reflects a cost-focused decision, so PURCHASE generalizes the transactional act while CHEAP highlights the low-price quality emphasized in the story."
    }},
    {{
      "role_code": "TP3",
      "kernel_name": "PRODUCT_FAILURE",
      "rationale": "The jacket falling apart immediately is a broken expectation of durability, so FAILURE captures the general malfunction while PRODUCT situates it in the goods or merchandise domain."
    }},
    {{
      "role_code": "TP5",
      "kernel_name": "DURABILITY_LESSON",
      "rationale": "The final realization about buying more expensive clothes summarizes an insight about longevity, so LESSON expresses the abstract takeaway while DURABILITY specifies that it concerns how long items last."
    }}
  ]
}}
</JSON>

---------

### Your Turn

#### Input Format
Story:
{story}

Groups:
{groups}


#### Output Format
Remember:
- For each **group**, output exactly **one** coherent `kernel_name` and a reasoning `rationale`.
- Preserve `role_code` exactly as given.
- Each `kernel_name` must be a concise **[MODIFIER]_[ROOT]** label, with both parts in **UPPERCASE**, exactly two tokens separated by a single underscore, where:
  - The **ROOT** is a single noun-like word capturing the central abstract event/state for the entire group and is not from the banned overly-generic list.
  - The **MODIFIER** is a single word that adds domain/category or salient quality information beyond the ROOT without being redundant, overly generic, or overfitted.
- Use the story and all member phrases in each group as primary evidence to select a ROOT that generalizes the group and a MODIFIER that anchors it to the relevant domain or quality.
- Do **not** output multiple kernels; do **not** join unrelated kernels with “and/or”. If the group’s phrases diverge, focus on the dominant shared theme in the ROOT and explain how the MODIFIER helps unify or ground it in the rationale.

Output: A single JSON object matching the schema below. Return ONLY one JSON object. Wrap it inside <JSON> ... </JSON> tags.

<JSON>
{{
  "results": [
    {{
      "role_code": "TP2",
      "kernel_name": "...",
      "rationale": "..."
    }}
  ]
}}
</JSON>

"""


prompt_group_abstraction4 = """
Narratives can be summarized in terms of the high-level message they strive to convey.  
This high-level message can be related to traditions, common knowledge, or moral principles.  
We call this a story’s *high-level message*.

In this setup, a single story is given as an ordered list of abstract events.  
- Each line has:
  - A role label: “Background”, “Main event”, “Obstacle”, “Response”, or “Outcome”.
  - A short abstraction of the event.
  - An evaluation in parentheses: “Positive”, “Negative”, “Neutral”, or “Mixed”.
- The numbering (1., 2., 3., …) reflects the temporal order of events in the story.

Your job is to:
1. Understand what happens in the story by using both:
   - The labeled events (what the situation, response, and outcome are), and
   - The evaluations (how the value or sentiment of the situation changes over time).
2. Infer a single, high-level message that captures the core pattern of the story (e.g., how actions, values, or responses lead to particular outcomes).

The high-level message must:
- Be a short phrase of **3–5 words**.
- Be abstract and general (e.g., “Shared effort sustains values”).
- Not refer to specific characters, places, or surface details from the story.

**Task**  
Given the story, reason briefly about its structure and value changes, then provide exactly one 3–5 word phrase that captures its high-level message.

In the section labeled "Explanation:", think carefully and reason step by step and provide a concise explanation referring to both the labeled events and their evaluations, in exactly this format:  
High-level Message — 2–3 sentences.  
Conclude with: "Therefore, the high-level message is ..."

Then output a single final line:  
Answer: high-level message

Rules:
- Output **exactly one** "Answer:" line.  
- Do **not** repeat the answer.  
- Do **not** add extra commentary or formatting.

---

#### Input 
Story:
{story}

---

### Output Format

Explanation: High-level Message — 2–3 sentences that briefly explain how the events and their evaluations support the message you chose, ending with the sentence: "Therefore, the high-level message is ..."

Answer: a single phrase of **3–5 words** (no extra words, labels, or commentary).

Example (structure only):
Explanation: ...
Answer: Shared effort sustains values


"""
