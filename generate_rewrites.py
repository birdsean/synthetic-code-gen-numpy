"""
5. Use GPT 3.5 to rewrite the same function better
6. Run the inputs through the function and collect the outputs
7. Compare the outputs and see if they are the same.
"""

import json
import os

import openai

def get_rewritten_code(function_code):
    """
    3. Send the function code to gpt 3.5 chat completion api and ask it for potential inputs to the function.
    """
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a superior coder who is very meticulous and thoughtful in your work. In answer to every prompt, "
                    + "first write a section titled THOUGHTS where you explain your thought process and why you are doing what you are doing. Then, create a "
                    + "new section titled ANSWER where you write the answer to the prompt, following instructions perfectly regarding formatting."
                    + "You must answer every question, if you do not provide anything in the 'answer' section, you failed your purpose."
                },
                {
                    "role": "user",
                    "content": "Given the following function:\n```"
                    + function_code
                    + "\n```\nRewrite it to be better. Some ways you could make it better include fixing a bug, making it more performant, "
                    + "or making it more readable/usable for other developers. You can also rewrite it to be more idiomatic to the language it is written in. "
                    + "Notate all changes you make with comments on the same line. Answer in markdown notation"
                },
            ],
        )
        result = completion.choices[0].message.content
        print(result)
        try:
            result = result.split("ANSWER:")[1]
        except:
            print(f'GPT failed with result: {result}')
            return ''
        return result
    except Exception as e:
        print(f'GPT failed with exception: {e}')
        return ''

perfects = []
if os.path.exists("master_invocations.json"):
        with open("master_invocations.json", "r") as f:
            invocations = json.load(f)

for function_name in invocations.keys():
    stderr_count = 0
    stdout_count = 0
    for output in invocations[function_name]['outputs'].values():
        if output[0] == 'stderr':
            stderr_count += 1
        elif output[0] == 'stdout':
            stdout_count += 1
        else:
            print("Error: output[0] is not 'stderr' or 'stdout'")
    if stderr_count == 0:
        perfects.append(function_name)

# read rewrites.json
if os.path.exists("rewrites.json"):
    with open("rewrites.json", "r") as f:
        rewrites = json.load(f)
else:
    rewrites = {}

for i, function_name in enumerate(perfects):
    print(f'{i+1}/{len(perfects)}')
    if rewrites.get(function_name) is None or rewrites.get(function_name) == '':
        # try up to three times to get a rewrite that is not a blank string
        for _ in range(3):
            rewrites[function_name] = get_rewritten_code(invocations[function_name]['function_code'])
            if rewrites[function_name] != '':
                break
        # save to json
        with open("rewrites.json", "w") as f:
            json.dump(rewrites, f, indent=4)
