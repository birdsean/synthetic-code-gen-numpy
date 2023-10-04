import json
import os

if os.path.exists("rewrites.json"):
    with open("rewrites.json", "r") as f:
        rewrites = json.load(f)

for function_name in rewrites.keys():
    raw_answer = rewrites[function_name]
    # grab all contents of ```python``` blocks
    if "``` python" in raw_answer:
        code_block = raw_answer.split("``` python")[1].split("```")[0]
    elif "```python" in raw_answer:
        code_block = raw_answer.split("```python")[1].split("```")[0]
    else:
        code_block = raw_answer
    
    rewrites[function_name] = {
        'raw_code': raw_answer,
        'code': code_block
    }

with open("cleaned_rewrites.json", "w") as f:
    json.dump(rewrites, f, indent=4)