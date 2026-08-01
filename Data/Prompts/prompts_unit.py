prompt_event_phrase_extraction = """
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