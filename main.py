'''
1. Parse all functions in repos/numpy into a dict with a reference to the file address they are in.
2. Pick one function and go retrieve the code from the file address.
3. Pass the function code to gpt 3.5 and ask it for potential inputs to the function.
4. Run the inputs through the function and collect the outputs
5. Use GPT 3.5 to rewrite the same function better
6. Run the inputs through the function and collect the outputs
7. Compare the outputs and see if they are the same.
'''

import os
import openai

def get_all_functions():
    '''
    1. Parse all functions in repos/numpy into a dict with a reference to the file address they are in.
    '''
    functions = {}
    for root, dirs, files in os.walk("repos/numpy"):
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file), "r") as f:
                    for line in f:
                        if line.startswith("def "):
                            functions[line.split("def ")[1].split("(")[0]] = os.path.join(root, file)
    return functions

def get_function_code(function_name, file_address):
    '''
    2. Pick one function and go retrieve the code from the file address.
    '''
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
    '''
    3. Send the function code to gpt 3.5 cat completion api and ask it for potential inputs to the function.
    '''
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
        {
            "role": "system", 
            "content": "You are a superior coder who is very meticulous and thoughtful in your work. In answer to every prompt, " + \
            "first write a section titled THOUGHTS where you explain your thought process and why you are doing what you are doing. Then, create a " + \
            "new section titled ANSWER where you write the answer to the prompt."
        },
        {
            "role": "user", 
            "content": "Given the following function:\n```" + function_code + "\n```\nReturn a list of inputs that would thoroughly test "+\
            "the capabilities of the function. Your answer should be a list of at least three new line separated list of cases, where each "+\
            "case is a comma separated list of function parameter values. For example, if the function was slice_string(str, start_index, "+\
            "end_index), your answer would look something like:\n\nANSWER:\n'foobar',0,3\n'test_string_2,0,0'\nJust respond with inputs, no "+\
            "commentary. If the param value is a string, be sure to surround it with single quotes."}
        ])
    result = completion.choices[0].message.content
    result = result.split("ANSWER:")[1]
    return result

def get_invocations(function_name, inputs):
    '''
    4. Run the inputs through the function and collect the outputs.
    '''
    # inputs looks like this: 'foobar',0,3\n'test_string_2,0,0', needs to be split by line and by comma and inserted into string surrounded by function call
    inputs = inputs.split("\n")
    inputs = [input.split(",") for input in inputs]
    invocations = []
    for input in inputs:
        if len(input) == 0 or input[0] == "":
            continue
        invocation = function_name + "(" + ",".join(input) + ")"
        invocations.append(invocation)
    
    print(invocations)

def get_import_statement_for_function(function_name, file_address):
    # file_address comes in like repos/numpy/pavement.py, need to convert to numpy.pavement
    # split on repos/, then replace / with ., then remove .py
    file_address = file_address.split("repos/")[1]
    file_address = file_address.replace("/", ".")
    file_address = file_address.removeprefix(".")
    file_address = file_address.removesuffix(".py")

    statement = f"from {file_address} import {function_name}"
    return statement

def execute_inputs(imports, invocations):
    #  Execute `docker run numpy python ...` and collect the function outputs
    cmds = []
    for invocation in invocations:
        cmd = f"docker run numpy python -c \"{imports};{invocation}\""
        cmds.append(cmd)
    return cmds


functions = get_all_functions()
function_name = list(functions.keys())[-1]
file_address = functions[function_name]
function_code = get_function_code(function_name, file_address)
print(function_code)
# raw_inputs = get_potential_inputs(function_code)
# invocations = get_invocations(function_name, raw_inputs)
invocations = ["tarball_name('gztar')", "tarball_name('zip')", "tarball_name('invalid')"]
imports = get_import_statement_for_function(function_name, file_address)
outputs = execute_inputs(imports, invocations)
print(outputs)