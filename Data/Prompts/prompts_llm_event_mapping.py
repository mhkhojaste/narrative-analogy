prompt_event_mapping_ARN_zs = """
Narratives can be mapped to each other in terms of the similarity of their events and how those events function in the story.  
Each story is represented as a numbered list of events. 
We call the mapping between corresponding events in two stories *analogical mapping*.

Here, you are given:
- One **base story**
- Two **target stories** (Target 0 and Target 1)
Each story is written as a numeric list of its events.

Your goal is to decide which target story (0 or 1) is **more analogous** to the base story, based on how well the events in the base story can be matched to events in the target stories.

**How to approach the task (internal reasoning)**

1. **Understand the base story**
   - Read through the base story’s events.
   - For each event, identify:
     - Its **general meaning** (what happens, at an abstract level).
     - Its **role in the story**, such as:
       - introduction / setup  
       - problem / difficulty  
       - cause of a problem  
       - reaction / decision  
       - attempt to solve a problem  
       - help / intervention  
       - outcome / consequence  
       - punishment / reward, etc.

2. **Analyze each target story with respect to the base**
   For Target 0 and Target 1 **separately**:
   - Read through the target story’s events.
   - Try to **map** events in the base story to events in the target story.
   - Two events are considered a good analogical match if:
     - They have a **similar general meaning** when described at a more abstract level (for example, “being overwhelmed by obligations,” “receiving help,” “being punished by an authority,” etc.), and
     - They play a **similar role in the story** (for example, both events are the main problem, both are the cause of the problem, both are the reaction, both are the final consequence, etc.).
   - Also consider how the events are **ordered**:
     - Problems typically precede reactions and outcomes.
     - Causes precede their consequences.
     - See whether these patterns line up between the base and the target.

3. **Compare the two target stories**
   - For each target, internally assess:
     - How many base events have clear, analogous events in the target?
     - How well the **roles** of the events are preserved (problem ↔ problem, cause ↔ cause, reaction ↔ reaction, outcome ↔ outcome).
     - How consistent the mapping is with the story order and structure.
   - The target with the **stronger analogical mapping** is the one where:
     - More base events can be matched to target events in terms of general meaning and role.
     - The matched events collectively preserve the structure and roles of the base story more clearly.

**Task**

Decide which of the two target stories (0 or 1) creates the stronger analogical mapping with the base story, based on event similarity in general meaning and role.

#### Input 
Base Story: {base_story}
Target0: {target_0}
Target1: {target_1}

#### Output Format

- Your **entire output** must be exactly one character:
  - `0` if Target 0 is the better analogical match.
  - `1` if Target 1 is the better analogical match.

Do not provide any explanations. Output just one number, either 0 or 1.
Provide your output in the following format:
0 or 1 (without any explanation)


"""


prompt_event_mapping_ARN_cot = """
Narratives can be mapped to each other in terms of the similarity of their events and how those events function in the story.  
Each story is represented as a numbered list of events. 
We call the mapping between corresponding events in two stories *analogical mapping*.

Here, you are given:
- One **base story**
- Two **target stories** (Target 0 and Target 1)
Each story is written as a numeric list of its events.

Your goal is to decide which target story (0 or 1) is **more analogous** to the base story, based on how well the events in the base story can be matched to events in the target stories.

**How to think about the problem**

1. **Understand the base story**
   - Read through the base story’s events.
   - For each event, think about:
     - Its **general meaning** (what happens, at an abstract level).
     - Its **role in the story**, such as:
       - introduction / setup  
       - problem / difficulty  
       - cause of a problem  
       - reaction / decision  
       - attempt to solve a problem  
       - help / intervention  
       - outcome / consequence  
       - punishment / reward, etc.

2. **Analyze each target story with respect to the base**
   For Target 0 and Target 1 **separately**:
   - Read through the target story’s events.
   - Try to **map** events in the base story to events in the target story.
   - Two events are considered a good analogical match if:
     - They have a **similar general meaning** when described at a more abstract level (for example, “being overwhelmed by obligations,” “receiving help from another,” “being punished by an authority,” etc.), and
     - They play a **similar role in the story** (for example, both events are the main problem, both are the cause of the problem, both are the reaction to the problem, both are the final consequence, etc.).
   - Pay attention not only to individual events, but also to how they are positioned in the story:
     - Does an event that is a problem in the base correspond to a problem in the target?
     - Does a cause in the base correspond to a cause in the target?
     - Does a resolution in the base correspond to a resolution in the target?

3. **Compare the two target stories**
   - For each target, consider:
     - How many base events have a clear, analogous event in the target?
     - How well the **roles** of the events are preserved (problem ↔ problem, cause ↔ cause, reaction ↔ reaction, outcome ↔ outcome).
     - How consistent the mapping is with the story order and structure (for example, problems come before reactions, reactions come before outcomes, etc.).
   - The target with the **stronger analogical mapping** is the one where:
     - More base events can be matched to target events in terms of general meaning and role.
     - The matched events collectively preserve the structure and roles of the base story more clearly.

**Task**

Decide which of the two target stories (0 or 1) creates the stronger analogical mapping with the base story, based on event similarity in general meaning and role.


### Output Format  
Return your answer wrapped between <JSON> and </JSON> tags **exactly as shown below**.

Inside the tags output a single JSON object with **two keys, in this order**:

1. "explanation": In the section labeled "explanation", think carefully and reason step by step and provide a concise explanation in exactly this format: (1) Base structure — 1–2 sentences summarizing the base story’s overall event structure. (2) Target0 structure — 1-2 sentence explaining how Target 0 aligns or fails at the structural level. (3) Target1 structure — 1-2 sentence explaining how Target 1 aligns or fails at the structural level. Therefore, Target X is a better mapping.

2. "answer": the integer 0 or 1 indicating the better target, with **no additional explanation**.

Example (structure only):
<JSON> 
{{ "explanation": "(1) Base structure: ...", 
"answer": 0 }} 
</JSON>
Produce nothing outside the <JSON> tags.


---

#### Input 
Base Story: {base_story}
Target0: {target_0}
Target1: {target_1}

---

#### Provide the output in the following format:
<JSON> 
{{ "explanation": Your reasoning goes here in this format: "(1) Base structure — ... (1–2 sentences). (2) Target0 structure — ... (1–2 sentences). (3) Target1 structure — ... (1–2 sentences). Therefore, Target X is a better mapping.", 
"answer": Provide **only the number** (0 or 1) of the best target. **Do not include any explanations.}} 
</JSON>

Produce nothing outside the <JSON> tags.


"""

prompt_event_mapping_MCQ_zs = """
Narratives can be mapped to each other in terms of the similarity of their events and how those events function in the story.  
Each story is represented as a numbered list of events.  
We call the mapping between corresponding events in two stories *analogical mapping*.

Here, you are given:
- One **base story**
- Four **target stories** (Target 0, Target 1, Target 2, Target 3)
Each story is written as a numeric list of its events.

Your goal is to decide which target story (0, 1, 2, or 3) is **most analogous** to the base story, based on how well the events in the base story can be matched to events in each of the target stories.

**How to approach the task (internal reasoning)**

1. **Understand the base story**
   - Read through the base story’s events.
   - For each event, identify:
     - Its **general meaning** (what happens, at an abstract level).
     - Its **role in the story**, such as:
       - introduction / setup  
       - problem / difficulty  
       - cause of a problem  
       - reaction / decision  
       - attempt to solve a problem  
       - help / intervention  
       - outcome / consequence  
       - punishment / reward, etc.

2. **Analyze each target story with respect to the base**
   For Target 0, Target 1, Target 2, and Target 3 **separately**:
   - Read through the target story’s events.
   - Try to **map** events in the base story to events in the target story.
   - Two events are considered a good analogical match if:
     - They have a **similar general meaning** when described at a more abstract level (for example, “being overwhelmed by obligations,” “receiving help,” “being punished by an authority,” etc.), and
     - They play a **similar role in the story** (for example, both events are the main problem, both are the cause of the problem, both are the reaction, both are the final consequence, etc.).
   - Also consider how the events are **ordered**:
     - Problems typically precede reactions and outcomes.
     - Causes precede their consequences.
     - See whether these patterns line up between the base story and each target story.

3. **Compare the four target stories**
   - For each target, internally assess:
     - How many base events have clear, analogous events in that target?
     - How well the **roles** of the events are preserved (problem ↔ problem, cause ↔ cause, reaction ↔ reaction, outcome ↔ outcome).
     - How consistent the mapping is with the story order and structure.
   - The target with the **strongest analogical mapping** is the one where:
     - More base events can be matched to target events in terms of general meaning and role.
     - The matched events collectively preserve the structure and roles of the base story more clearly than in the other targets.

**Task**

Decide which of the four target stories (0, 1, 2, or 3) creates the strongest analogical mapping with the base story, based on event similarity in general meaning and role.

#### Input 
Base Story: {base_story}
Target0: {target_0}
Target1: {target_1}
Target2: {target_2}
Target3: {target_3}

#### Output Format

- Your **entire output** must be exactly one character:
  - `0` if Target 0 is the best analogical match.
  - `1` if Target 1 is the best analogical match.
  - `2` if Target 2 is the best analogical match.
  - `3` if Target 3 is the best analogical match.

Do not provide any explanations. Output just one number, either 0, 1, 2, or 3.
Provide your output in the following format:
0, 1, 2, or 3 (without any explanation)


"""


prompt_event_mapping_MCQ_cot = """
Narratives can be mapped to each other in terms of the similarity of their events and how those events function in the story.  
Each story is represented as a numbered list of events.  
We call the mapping between corresponding events in two stories *analogical mapping*.

Here, you are given:
- One **base story**
- Four **target stories** (Target 0, Target 1, Target 2, Target 3)
Each story is written as a numeric list of its events.

Your goal is to decide which target story (0, 1, 2, or 3) is **most analogous** to the base story, based on how well the events in the base story can be matched to events in each of the target stories.

**How to think about the problem**

1. **Understand the base story**
   - Read through the base story’s events.
   - For each event, think about:
     - Its **general meaning** (what happens, at an abstract level).
     - Its **role in the story**, such as:
       - introduction / setup  
       - problem / difficulty  
       - cause of a problem  
       - reaction / decision  
       - attempt to solve a problem  
       - help / intervention  
       - outcome / consequence  
       - punishment / reward, etc.

2. **Analyze each target story with respect to the base**
   For Target 0, Target 1, Target 2, and Target 3 **separately**:
   - Read through the target story’s events.
   - Try to **map** events in the base story to events in the target story.
   - Two events are considered a good analogical match if:
     - They have a **similar general meaning** when described at a more abstract level (for example, “being overwhelmed by obligations,” “receiving help from another,” “being punished by an authority,” etc.), and
     - They play a **similar role in the story** (for example, both events are the main problem, both are the cause of the problem, both are the reaction to the problem, both are the final consequence, etc.).
   - Pay attention not only to individual events, but also to how they are positioned in the story:
     - Does an event that is a problem in the base correspond to a problem in the target?
     - Does a cause in the base correspond to a cause in the target?
     - Does a resolution in the base correspond to a resolution in the target?

3. **Compare the four target stories**
   - For each target, consider:
     - How many base events have a clear, analogous event in that target?
     - How well the **roles** of the events are preserved (problem ↔ problem, cause ↔ cause, reaction ↔ reaction, outcome ↔ outcome).
     - How consistent the mapping is with the story order and structure (for example, problems come before reactions, reactions come before outcomes, etc.).
   - The target with the **strongest analogical mapping** is the one where:
     - More base events can be matched to target events in terms of general meaning and role.
     - The matched events collectively preserve the structure and roles of the base story more clearly than in the other targets.

**Task**

Decide which of the four target stories (0, 1, 2, or 3) creates the strongest analogical mapping with the base story, based on event similarity in general meaning and role.

### Output Format  
Return your answer wrapped between <JSON> and </JSON> tags **exactly as shown below**.

Inside the tags output a single JSON object with **two keys, in this order**:

1. "explanation": In the section labeled "explanation", think carefully and reason step by step and provide a concise explanation in exactly this format: (1) Base structure — 1–2 sentences summarizing the base story’s overall event structure. (2) Target0 structure — 1–2 sentences explaining how Target 0 aligns with or fails to match that structure. (3) Target1 structure — 1–2 sentences explaining how Target 1 aligns with or fails to match that structure. (4) Target2 structure — 1–2 sentences explaining how Target 2 aligns with or fails to match that structure. (5) Target3 structure — 1–2 sentences explaining how Target 3 aligns with or fails to match that structure. Therefore, Target X is a better mapping.

2. "answer": the integer 0, 1, 2, or 3 indicating the better target, with **no additional explanation**.

Example (structure only):
<JSON> 
{{ "explanation": "(1) Base structure: ...", 
"answer": 0 }} 
</JSON>
Produce nothing outside the <JSON> tags.

---

#### Input 
Base Story: {base_story}
Target0: {target_0}
Target1: {target_1}
Target2: {target_2}
Target3: {target_3}

---

#### Provide the output in the following format:
<JSON> 
{{ "explanation": Your reasoning goes here in this format: "(1) Base structure — ... (1–2 sentences). (2) Target0 structure — ... (1–2 sentences). (3) Target1 structure — ... (1–2 sentences). (4) Target2 structure — ... (1–2 sentences). (5) Target3 structure — ... (1–2 sentences). Therefore, Target X is a better mapping.", 
"answer": Provide **only the number** (0, 1, 2, or 3) of the best target. **Do not include any explanations.}} 
</JSON>

Produce nothing outside the <JSON> tags.

"""