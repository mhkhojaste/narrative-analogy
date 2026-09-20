prompt_message_mapping_ARN_zs = """Narratives can be mapped to each other in terms of the high-level message they strive to convey.
This high-level message can be related to traditions, common knowledge, or moral principles.
We call this mapping analogical mapping. 

Which one of the two target stories (0, 1) can create a better analogical mapping with the base story?

Input Format:
```
Base Story: {base_story}
Target0: {target_0}
Target1: {target_1}
```

### **Output Format:**
Provide **only the number** (0 or 1) of the best target. **Do not include any explanations."""


prompt_message_mapping_ARN_cot = """
Narratives can be mapped to each other in terms of the high-level message they strive to convey.  
This high-level message can be related to traditions, common knowledge, or moral principles.  
We call this mapping *analogical mapping*.

**Task**  
Decide which of the two target stories (0 or 1) creates the stronger analogical mapping with the base story.

First, think carefully and reason step by step under the section labeled "Explanation:".  
In this part, briefly describe your thought process and how you arrived at the decision.  

After that, provide your final decision under the section labeled "Answer:".  
This part must contain only the result — either "Answer: 0" or "Answer: 1" — with no additional text or explanation.  

Example (structure only):
Explanation: ...
Answer: 0


#### Input 
Base Story: {base_story}
Target0: {target_0}
Target1: {target_1}

### Output Format  
Provide your output in the following format:

Explanation: ... (Your step-by-step reasoning here)
Answer: ... (Your answer here. 0 or 1 with no explanation)
"""

prompt_message_mapping_MCQ_zs = """Narratives can be mapped to each other in terms of the high-level message they strive to convey.
This high-level message can be related to traditions, common knowledge, or moral principles.
We call this mapping analogical mapping. 
Which one of the four target stories (0, 1, 2, or 3) can create a better analogical mapping with the base story?

Input Format:
```
Base Story: {base_story}
Target0: {target_0}
Target1: {target_1}
Target2: {target_2}
Target3: {target_3}
```

### **Output Format:**
Provide **only the number** (0, 1, 2, or 3) of the best target. **Do not include any explanations."""





prompt_message_mapping_MCQ_cot = """
Narratives can be mapped to each other in terms of the high-level message they strive to convey.  
This high-level message can be related to traditions, common knowledge, or moral principles.  
We call this mapping *analogical mapping*.

**Task**  
Decide which of the four target stories (0, 1, 2, or 3) creates the stronger analogical mapping with the base story.

First, think carefully and reason step by step under the section labeled "Explanation:".  
In this part, briefly describe your thought process and how you arrived at the decision.  

After that, provide your final decision under the section labeled "Answer:".  
This part must contain only the result — either "Answer: 0" or "Answer: 1" or "Answer: 2" or "Answer: 3" — with no additional text or explanation.  

Example (structure only):
Explanation: ...
Answer: 0


#### Input 
Base Story: {base_story}
Target0: {target_0}
Target1: {target_1}
Target2: {target_2}
Target3: {target_3}

### Output Format  
Provide your output in the following format:

Explanation: ... (Your step-by-step reasoning here)
Answer: ... (Your answer here. 0, 1, 2, or 3 with no explanation)
"""
