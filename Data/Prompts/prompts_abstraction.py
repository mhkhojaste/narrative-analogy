prompt_timeline_extraction = """
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


prompt_conceptual_abstraction_level0 = """
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


prompt_conceptual_abstraction_level1 = """"
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


prompt_evaluative_abstraction = """

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


prompt_arc_abstraction = """
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



prompt_stage_abstraction = """

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