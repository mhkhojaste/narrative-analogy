prompt_event_phrase_extraction = """
## Role Assignment
You are an annotator who reads short stories and converts them into a **list of event phrases**.

--------

## Task Definition
For each provided story, extract every **distinct event** and express each as a **single, concise phrase** that follows the constraints below.

--------

## Term Definitions
- **event**: a specific **occurrence** involving **participants**
- **occurrence**: one discrete happening, action, state change, or decision at a point in the narrative
- **participant**: any person or entity involved (e.g., I, my neighbor, teacher)
- **decision or conclusion**: a mental event that affects the story and must be included
- **negation**: an explicit not phrase (e.g., did not, could not) rather than a contraction

--------

## Guidelines
- **one event per array element**; do **not** combine events
- **phrase form**, not a full sentence; no trailing punctuation
- **capitalization and allowed characters**: Start each phrase with an **uppercase** letter. **Capitalize proper nouns** (e.g., Lily, Jose, Mario). **Use letters and spaces only** (A–Z, a–z, space). **Do not** use digits, punctuation, or symbols.
- **negations**: State negations explicitly using **not**; avoid contractions
- **order**: Keep events in the story’s **original order**
- **include mental events**: Include **decisions and conclusions** that are explicitly stated or unmistakably implied
- **conciseness and atomicity**: Be concise and capture **only one event, occurrence, or decision** per phrase; aim for **3 to 8 words**; avoid using **and** to join actions
- **participant specificity**: Name participants when needed to make the line self-contained and unambiguous out of context
- **intention → reason → decision sequencing**:
  - When the story presents an **initial intention**, a **reason**, and a **final decision**, list them as **separate events in sequence**.
  - **Do not** invent intentions. Use words like **considered planned intended** only when the story states or clearly implies them.
  - Express the **reason** as a normal event phrase in plain language (e.g., **Mario had the money**, **Do not want to cause problems in marriage**). **Do not** add labels like **reason** or any punctuation.
  - Avoid listing **two opposite decisions** back to back. If the text says **instead of X Y**, record **Did not X** and also record **Y**; do **not** add **considered X** unless the text supports it.
- **spelling and names**: Correct obvious typos in common words; preserve names as written and use them consistently
- **uncertainty**: Keep uncertainty or evaluation only if it informs a later action or decision

--------

## Examples
### Example 1
Story:
David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better.

Output:
<JSON>
[
  "David noticed weight gain",
  "Examined his habits for a reason",
  "Realized he ate too much fast food",
  "Stopped going to burger places",
  "Started a vegetarian diet",
  "Felt better after a few weeks"
]
</JSON>

### Example 2
Story:
Eric and his wife had a daughter named Meg. Eric and Meg were very sad when Eric's wife passed away. Eric met a woman and married her 5 years after his wife died. Meg is finally happy with her new stepmother.

Output:
<JSON>
[
  "Eric and his wife had Meg",
  "Erics wife passed away",
  "Eric and Meg were very sad",
  "Eric met a woman",
  "Five years later Eric married the woman",
  "Meg was happy with her stepmother"
]
</JSON>

### Example 3
Story:
There was a bug on the wall by the bed. Kate grabbed a shoe and killed it.

Output:
<JSON>
[
  "Bug was on the wall by the bed",
  "Kate grabbed a shoe",
  "Kate killed the bug"
]
</JSON>

### Example 4
Story:
I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.

Output:
<JSON>
[
  "Bought a cheap jacket",
  "Jacket fell apart the next day",
  "Concluded more expensive clothes last longer"
]
</JSON>

--------

## Your Turn

### Input Format
Story:
{story}

### Output Format


### Remember
- Extract events that are specific **occurrences** or **decisions** in the story
- Keep phrases **concise** and express **only one event** per array element
- Preserve the **original narrative order**
- Use **uppercase** to start each phrase and **capitalize proper nouns**; use **letters and spaces only**
- Express **reasons** as normal phrases without labels; avoid **reason** or any punctuation
- Express **negations with not** and avoid contractions
- Do not invent or create events that are not explicitly mentioned in the story.

Provide output in the following format. Do **not** output anything before or after it:

<JSON>
[
  "Event phrase 1",
  "Event phrase 2",
  "...",
  "Event phrase n"
]
</JSON>
"""



prompt_event_phrase_extraction_2 = """
## Role Assignment
You are an annotator who reads short stories and converts them into a **list of event phrases**.

--------

## Task Definition
For each provided story, extract every **distinct event** and express each as a **single, concise phrase** that follows the constraints below.

--------

## Term Definitions
- **event**: An event is the smallest distinct piece of information in the text that represents an action, state, fact, or choice. An event can include
  1) **Action or state change**: something that happens or changes involving participants.
  2) **Observation or background fact**: descriptive details that situate or explain actions.
  3) **Intention or plan**: a stated goal, plan, or something meant to be done.
  4) **Reason or motive**: explanation of why someone acts, feels, or chooses.
  5) **Decision or conclusion**: a choice made, realization, or reflection.
- **negation**: an explicit not phrase (e.g., did not, could not) rather than a contraction

--------

## Guidelines
- **one event per array element**; do **not** combine events
- Extract **every event** and **piece of information**
  - When **combined**, the extracted events should **fully reconstruct the story**, with **no loss** of detail.
- **phrase form**, not a full sentence; no trailing punctuation
- **capitalization and allowed characters**: Start each phrase with an **uppercase** letter. **Capitalize proper nouns** (e.g., Lily, Jose, Mario). **Use letters and spaces only** (A–Z, a–z, space). **Do not** use digits, punctuation, or symbols.
- **negations**: State negations explicitly using **not**; avoid contractions
- **order**: Keep events in the story’s **original order**
- **include mental events**: Include **decisions and conclusions** that are explicitly stated or unmistakably implied
- **include background**: Include **all background facts**, whether they provide context, constraints, or reasons for actions, as well as descriptive details or scene-setting, even if they do not directly influence the events.
- **include dialogue**: Treat spoken facts, rules, and reasons as normal events.
- **include reasons and justifications**: When a directive, action, or decision includes **because / since / so / therefore / due to / as** or presents a justification, extract **each reason as its own event** placed immediately after the triggering action/decision.
- **conciseness and atomicity**: Be concise and capture **only one event per phrase
  - aim for **3 to 8 words**
  - avoid using **and** to join actions
- **participant specificity**: Name participants when possible at the start of each event
   - Make the line self-contained and unambiguous out of context
- **intention → reason → decision sequencing**:
  - When the story presents an **initial intention**, a **reason**, and a **final decision**, list them as **separate events in sequence**.
  - **Do not** invent intentions. Use words like **considered, planned,  intended** only when the story states or clearly implies them.
  - Express the **reason** as a normal event phrase in plain language.
  - **Do not** add labels like **reason** or any punctuation.
  - Avoid listing **two opposite decisions** back to back. If the text says **instead of X Y**, record **Did not X** and also record **Y**; do **not** add **considered X** unless the text supports it.
- **spelling and names**: Correct obvious typos in common words; preserve names as written and use them consistently


### Coverage and Self Check  *(perform silently; output only the JSON array)*
- **Sentence pass:** Ensure **each sentence** yields at least one event.
- **Clause pass:** For any sentence with multiple independent clauses or finite verbs, output a **separate event for each**.
- **Reason pass:** After any action/decision with an explicit justification (including in **dialogue**), output the **reason as its own event**.
- **Dialogue pass:** Convert spoken facts, rules, and reasons into event phrases.
- **Duplicate pass:** Remove **duplicate or paraphrased duplicates**. Output **habitual events once only**.
- **Final check:** Check that combining the extracted events reconstructs the complete story without any loss of information.


--------

## Examples
### Example 1
Story:
David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.

Output:
<JSON>
[
  "David noticed weight gain",
  "David Examined his habits for a reason",
  "David Realized he ate too much fast food",
  "David Stopped going to burger places",
  "David Started a vegetarian diet",
  "David Felt better after a few weeks",
  "David had stopped eating unhealthy foods"
]
</JSON>

### Example 2
Story:
Eric and his wife had a daughter named Meg. Eric and Meg were very sad when Eric's wife passed away. Eric met a woman and married her 5 years after his wife died. Meg is finally happy with her new stepmother as she is very kind to her.

Output:
<JSON>
[
  "Eric and his wife had Meg",
  "Erics wife passed away",
  "Eric and Meg were very sad",
  "Eric met a woman",
  "Eric married the woman five years later ",
  "Meg was happy with her stepmother",
  "Megs stepmother is kind to her"
]
</JSON>

### Example 3
Story:
There was a bug on the wall by the bed. Kate grabbed a shoe and killed it.

Output:
<JSON>
[
  "Bug was on the wall by the bed",
  "Kate grabbed a shoe",
  "Kate killed the bug"
]
</JSON>

### Example 4
Story:
I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.

Output:
<JSON>
[
  "I bought a cheap jacket",
  "Jacket fell apart the next day",
  "I concluded more expensive clothes last longer"
]
</JSON>

--------

## Your Turn

### Input Format
Story:
{story}

### Output Format


### Remember
- Extract every pieces of information that are **actions, observations/background, intentions, reasons, decisions, conclusions** as events.
- Express **reasons** as normal phrases without labels; avoid **reason** or any punctuation
- Keep phrases **concise** and express **only one event** per array element
- **Do not combine events**. Events should be atomic.
- Preserve the **original narrative order**
- Use **uppercase** to start each phrase and **capitalize proper nouns**; use **letters and spaces only**
- Start the phrase with the *participant's name* if possible
- Express **negations with not** and avoid contractions
- Do not invent or create events that are not explicitly mentioned in the story.

Provide output in the following format. Do **not** output anything before or after it:

<JSON>
[
  "Event phrase 1",
  "Event phrase 2",
  "...",
  "Event phrase n"
]
</JSON>
"""



prompt_event_phrase_extraction_3 = """
## Role Assignment
You are an annotator who reads short stories and converts them into a **list of event phrases**.

---

## Task Definition
For each story, extract every **distinct event** and express it as a **single, concise phrase** following the rules below.

---

## Term Definitions
- **event**: The smallest distinct piece of information that is an action, state, fact, intention, reason, or decision.
- **negation**: Explicit “not” forms (e.g., did not, could not), not contractions.

---

## Guidelines
- **One event per element**; do not combine.
- **Extract every event** so the list fully reconstructs the story.
- **Phrase form** only; no full sentences or punctuation.
- **Capitalization**: Start with uppercase, capitalize proper nouns. Only letters and spaces allowed.
- **Negations**: Use explicit “not.”
- **Order**: Preserve original story order.
- **Include mental events**: decisions, conclusions, intentions if stated/clearly implied.
- **Include background**: all contextual or descriptive facts.
- **Include dialogue**: Spoken facts, rules, and reasons as normal events.
- **Reasons/justifications**: Extract each reason as a separate event immediately after the triggering action.
- **Conciseness/atomicity**: 3–8 words, one event per phrase, avoid “and.”
- **Participant specificity**: Name participants when possible to keep phrases self-contained.
- **Sequencing**: Separate intention → reason → decision if text presents them.  
  - Record “Did not X” and “Y” for “instead of X Y.”  
  - Do not invent intentions.

---

## Coverage and Self-Check *(silent; output only JSON array)*
- Each sentence yields ≥1 event.  
- Separate events for multiple clauses/verbs.  
- Add reasons after actions/decisions with explicit justifications.  
- Convert dialogue facts/rules/reasons.  
- Remove duplicates; output habitual events once.  
- Final check: Combined events must reconstruct the full story.


--------

## Examples
### Example 1
Story:
David noticed he had put on a lot of weight recently. He examined his habits to try to figure out the reason. He realized he'd been eating too much fast food lately, so he stopped going to burger places and started a vegetarian diet. After a few weeks, he started to feel much better since he had stopped eating unhealthy foods.

Output:
<JSON>
[
  "David noticed weight gain",
  "David Examined his habits for a reason",
  "David Realized he ate too much fast food",
  "David Stopped going to burger places",
  "David Started a vegetarian diet",
  "David Felt better after a few weeks",
  "David had stopped eating unhealthy foods"
]
</JSON>

### Example 2
Story:
Eric and his wife had a daughter named Meg. Eric and Meg were very sad when Eric's wife passed away. Eric met a woman and married her 5 years after his wife died. Meg is finally happy with her new stepmother as she is very kind to her.

Output:
<JSON>
[
  "Eric and his wife had Meg",
  "Erics wife passed away",
  "Eric and Meg were very sad",
  "Eric met a woman",
  "Eric married the woman five years later ",
  "Meg was happy with her stepmother",
  "Megs stepmother is kind to her"
]
</JSON>

### Example 3
Story:
There was a bug on the wall by the bed. Kate grabbed a shoe and killed it.

Output:
<JSON>
[
  "Bug was on the wall by the bed",
  "Kate grabbed a shoe",
  "Kate killed the bug"
]
</JSON>

### Example 4
Story:
I bought a cheap jacket for only a dollar. It fell apart the next day. I now know it is best to buy more expensive clothes that last longer.

Output:
<JSON>
[
  "I bought a cheap jacket",
  "Jacket fell apart the next day",
  "I concluded more expensive clothes last longer"
]
</JSON>

--------

## Your Turn

### Input Format
Story:
{story}

### Output Format


### Remember
- Extract every pieces of information that are **actions, observations/background, intentions, reasons, decisions, conclusions** as events.
- Express **reasons** as normal phrases without labels; avoid **reason** or any punctuation
- Keep phrases **concise** and express **only one event** per array element
- **Do not combine events**. Events should be atomic.
- Preserve the **original narrative order**
- Use **uppercase** to start each phrase and **capitalize proper nouns**; use **letters and spaces only**
- Start the phrase with the *participant's name* if possible
- Express **negations with not** and avoid contractions
- Do not invent or create events that are not explicitly mentioned in the story.

Provide output in the following format. Do **not** output anything before or after it:

<JSON>
[
  "Event phrase 1",
  "Event phrase 2",
  "...",
  "Event phrase n"
]
</JSON>
"""

prompt_event_phrase_extraction_4 = """
### Role Assignment
You are a frame-extraction assistant. 
Your job is to read a numbered list of **Sentences** and assign concise semantic **Frames** that abstract the distinct events stated in those sentences. 
Each **Frame** must follow the schema **[MODIFIER]_[ROOT]**, capturing an event’s core meaning in the context implied by the sentence list.

### Task Definition
You must do this in two internal steps for each sentence:
1) **Understand the events in the sentence.**
2) **Assign exactly one Frame to each distinct event you understood.**

#### Event Understanding (internal only)
An **event** is:
- A distinct occurrence.
- The smallest distinct piece of information that is an **action**, **state**, **fact**, **intention**, **reason**, or **decision**.

How to understand events:
- A single sentence may contain **one or several** events.
- Treat events as **distinct** when they describe different actions or different states or different facts or an intention separate from an action or a reason separate from an action or a decision separate from a belief.
- You must use only what is stated in the sentences. Do not invent events that are not supported by the text.
- You must ensure every sentence is fully accounted for by one or more event frames. Do not skip meaningful events.

After understanding events, use the following specification to construct each **Frame**:

**ROOT**
- **Purpose:** Name the core event/state/concept in **one noun-like word**.
- **How to extract the candidate word:**
  1) Identify the **semantic head** of the event — what happened or what state holds.
  2) Convert it to a **noun-like** form if needed (e.g., verb → nominalization) while preserving meaning.
- **Not allowed (hard ban):**
  - Words that are **overly general and sentence-agnostic**: ACTION, EVENT, ACTIVITY, SITUATION, OCCURRENCE, THING, ITEM, OBJECT, PROCESS, INFORMATION, KNOWLEDGE, STUFF.  
  - *Why:* These carry no useful signal and fail to convey meaning.

**MODIFIER**
- **Purpose:** Provide an **explanation** for the ROOT in **one word**.
- **How to choose it:**
  - **Domain or category option:** Choose a **domain-level or category-level** noun that clearly ties the ROOT to these sentences while avoiding single-instance items or names.  
  - **Quality option:** You may instead use a **single-word quality adjective** when the event focuses on **tempo, degree, polarity, or quality** rather than domain.  
  - **Focus choice:** Decide whether **domain** or **quality** is more relevant by identifying the main focus of the event.
  - **Non-redundancy:** The modifier must be **completely different from the ROOT** and add **new information** rather than restating or paraphrasing the ROOT.
- **Not allowed (hard ban):**
  - Generic or meta modifiers that **do not add sentence signal**: GENERAL, QUALITY, THING, STUFF, EVENT, CONTEXT, TOPIC, AREA, DOMAIN, PEOPLE, PERSON, ENTITY, KNOWLEDGE, INFORMATION.  
  - Overly specific **proper names** or **single-instance items** when a domain or category (or a salient quality adjective) is available.  
  - *Why:* These either fail to anchor the ROOT to the sentences or overfit to a one-off instance.

**[MODIFIER]_[ROOT] frames**
- **Form:** `[MODIFIER]_[ROOT]`
- **Goal:** precisely capture each distinct event with a minimal but meaningful sentence signal.

**Rules**
- First, **understand the events** in each sentence. One sentence may yield multiple frames. You must not output the event phrases. You must output only frames.
- **Formatting:** both tokens **UPPERCASE**; exactly **two tokens** separated by a single underscore; total tokens = **2**.
- Avoid ultra-generic frames and avoid overfitted one-offs.

### Output Format
Return a single JSON value wrapped in **<JSON> ... </JSON>** tags.
- The JSON must be an **array of strings**.
- Each string must be one frame name in **[MODIFIER]_[ROOT]** form (UPPERCASE, exactly 2 tokens).
- The array order must follow the sentence order and the event order within each sentence.

### Examples

**Example 1**

Sentences:
1. David noticed he had put on a lot of weight recently.
2. He examined his habits to try to figure out the reason.
3. He realized he'd been eating too much fast food lately.
4. He stopped going to burger places and started a vegetarian diet.
5. After a few weeks he started to feel much better since he had stopped eating unhealthy foods.

Output:
<JSON>
[
  "HEALTH_AWARENESS",
  "HABIT_ANALYSIS",
  "DIET_REALIZATION",
  "HABIT_CESSATION",
  "DIET_ADOPTION",
  "HEALTH_IMPROVEMENT",
  "DIET_CESSATION"
]
</JSON>

**Example 2**

Sentences:
1. I bought a cheap jacket for only a dollar.
2. It fell apart the next day.
3. I now know it is best to buy more expensive clothes that last longer.

Output:
<JSON>
[
  "CHEAP_PURCHASE",
  "PRODUCT_FAILURE",
  "EXPERIENCE_REALIZATION"
]
</JSON>

### Your Turn

#### Input Format
Sentences:
{story}

#### Remember:
- You are given only **Sentences** as a numbered list.
- First **understand the distinct events** stated in each sentence. One sentence may contain **one or several** events.
- An event is the smallest distinct piece of information that is an action state fact intention reason or decision.
- Do not invent events. Use only what is supported by the sentences.
- Then assign **exactly one frame per distinct event** using **[MODIFIER]_[ROOT]**.
- Keep frames **exactly two tokens**, **UPPERCASE**, with **one underscore**: `MODIFIER_ROOT`.
- **Banned ROOTs:** EVENT, ACTION, ACTIVITY, SITUATION, OCCURRENCE, THING, ITEM, OBJECT, PROCESS, INFORMATION, KNOWLEDGE, STUFF. You are not allowed to use these for roots.
- **Banned MODIFIERs:** GENERAL, QUALITY, THING, STUFF, EVENT, CONTEXT, TOPIC, AREA, DOMAIN, PEOPLE, PERSON, ENTITY, KNOWLEDGE, INFORMATION; plus specific names and single-instance items when a domain or category is available.

Output: A single JSON array exactly matching the schema described in Output Format.

Return ONLY one JSON value. Do not output anything before or after it.
Wrap the array inside <JSON> ... </JSON> tags.
Provide output in the following format:
<JSON>
[
  "MODIFIER_ROOT1",
  "MODIFIER_ROOT2",
  ...
]
</JSON>

"""