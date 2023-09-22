"""
1. Parse all functions in repos/numpy into a dict with a reference to the file address they are in.
2. Pick one function and go retrieve the code from the file address.
3. Pass the function code to gpt 3.5 and ask it for potential inputs to the function.
4. Run the inputs through the function and collect the outputs
5. Use GPT 3.5 to rewrite the same function better
6. Run the inputs through the function and collect the outputs
7. Compare the outputs and see if they are the same.
"""

import json
import os
import openai
import subprocess


def get_all_functions():
    """
    1. Parse all functions in repos/numpy into a dict with a reference to the file address they are in.
    """
    functions = {}
    for root, dirs, files in os.walk("repos/numpy"):
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file), "r") as f:
                    for line in f:
                        if line.startswith("def "):
                            functions[
                                line.split("def ")[1].split("(")[0]
                            ] = os.path.join(root, file)
    return functions


def get_function_code(function_name, file_address):
    """
    2. Pick one function and go retrieve the code from the file address.
    """
    with open(file_address, "r") as f:
        for line in f:
            if line.startswith("def " + function_name):
                function_code = line
                for line in f:
                    if line.startswith("def ") or line.startswith("class "):
                        break
                    function_code += line
                return function_code


def get_potential_inputs(function_code):
    """
    3. Send the function code to gpt 3.5 cat completion api and ask it for potential inputs to the function.
    """
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a superior coder who is very meticulous and thoughtful in your work. In answer to every prompt, "
                    + "first write a section titled THOUGHTS where you explain your thought process and why you are doing what you are doing. Then, create a "
                    + "new section titled ANSWER where you write the answer to the prompt, following instructions perfectly regarding formatting.",
                },
                {
                    "role": "user",
                    "content": "Given the following function:\n```"
                    + function_code
                    + "\n```\nReturn a list of valid inputs that would thoroughly test "
                    + "the capabilities of the function. Your answer should be a list of ten new line separated list of cases, where each "
                    + "case is a comma separated list of function parameter values.\nFor example, if the function was slice_string(str, start_index, "
                    + "end_index), your answer would look something like:\n\nANSWER:\n'foobar',0,3\n'test_string_2,0,0'\nJust respond with inputs, NO "
                    + "COMMENTARY, NO NUMBERING, NO LABELS, NO BULLET POINTS, NO DASHES. If the param value is a string, be sure to surround it with double quotes."
                    + "If the function takes no params, return an empty line. Each line should be unique."
                },
            ],
        )
        result = completion.choices[0].message.content
        try:
            result = result.split("ANSWER:")[1]
        except:
            print(f'GPT failed with result: {result}')
            return ''
        return result
    except Exception as e:
        print(f'GPT failed with exception: {e}')
        return ''


def get_invocations(function_name, inputs):
    """
    4. Run the inputs through the function and collect the outputs.
    """
    # inputs looks like this: 'foobar',0,3\n'test_string_2,0,0', needs to be split by line and by comma and inserted into string surrounded by function call
    inputs = inputs.split("\n")
    inputs = [input.split(",") for input in inputs]
    invocations = []
    for input in inputs:
        if len(input) == 0 or input[0] == "":
            continue
        # if line starts with '- ', remove it
        if input[0].startswith("- "):
            # remove first 2 chars
            input[0] = input[0][2:]
        invocation = function_name + "(" + ",".join(input) + ")"
        invocations.append(invocation)

    return invocations


def execute_inputs(function_name, invocations):
    #  Execute `docker run numpy python ...` and collect the function outputs
    results = {}
    for invocation in invocations:
        # remove all backslashes form invocation
        cmd = f"docker run numpy python -c 'import numpy as np; print(np.{invocation})'"
        # exec command and collect output

        # Run a command and capture its output
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        stdout, stderr = process.communicate()

        # Check for errors
        if process.returncode == 0:
            results[invocation] = ["stdout", stdout.decode("utf-8")]
        else:
            results[invocation] = ["stderr", stderr.decode("utf-8")]
    return results


def determine_public_functions():
    cmd = f"docker run numpy python -c 'import numpy as np; print(dir(np))'"
    # exec command and collect output
    output = os.popen(cmd).read()
    # remove first and last char
    public_functions = output[1:-1]
    # remove all whitespace
    public_functions = public_functions.replace(" ", "")
    # remove all single quotes
    public_functions = public_functions.replace("'", "")
    # split by comma
    return public_functions.split(",")


def generate_invocation_outputs():
    public_functions = determine_public_functions()
    functions = get_all_functions()

    master_invocations = {}

    # filter out functions that are not public
    for function_name in list(functions.keys()):
        if function_name not in public_functions:
            del functions[function_name]

    # filter out functions that are already in master_invocations.json
    if os.path.exists("master_invocations.json"):
        with open("master_invocations.json", "r") as f:
            master_invocations = json.load(f)

        for function_name in list(functions.keys()):
            if function_name in master_invocations:
                del functions[function_name]

    print(f"Generating invocation outputs for {len(functions)} functions")
    for i, function_name in enumerate(functions.keys()):
        print(
            f"Generating invocation outputs for '{function_name}'. {i+1}/{len(functions)}."
        )
        if function_name not in public_functions:
            continue

        cache = {}

        file_address = functions[function_name]
        function_code = get_function_code(function_name, file_address)
        cache["function_code"] = function_code

        raw_inputs = get_potential_inputs(function_code)
        cache["raw_inputs"] = raw_inputs

        invocations = get_invocations(function_name, raw_inputs)
        cache["invocations"] = invocations

        outputs = execute_inputs(function_name, invocations)
        cache["outputs"] = outputs

        master_invocations[function_name] = cache

        with open("master_invocations.json", "w") as f:
            json.dump(master_invocations, f)
        
    print(f"Generated {len(master_invocations)} invocation outputs")
    with open("master_invocations.json", "w") as f:
        json.dump(master_invocations, f)


generate_invocation_outputs()
