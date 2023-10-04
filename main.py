import json
import os
import subprocess


def execute_inputs(invocations):
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
        print(f'Executing command: {cmd}')
        stdout, stderr = process.communicate()

        # Check for errors
        if process.returncode == 0:
            results[invocation] = ["stdout", stdout.decode("utf-8")]
        else:
            results[invocation] = ["stderr", stderr.decode("utf-8")]
    return results

# read master_invocations.json
with open("master_invocations.json", "r") as f:
    master_invocations = json.load(f)

# read cleaned_rewrites.json
with open("cleaned_rewrites.json", "r") as f:
    rewrites = json.load(f)

# if results.json exists, read it
if os.path.exists("results.json"):
    with open("results.json", "r") as f:
        results = json.load(f)
else:
    results = {}

for i, function_name in enumerate(rewrites.keys()):
    print(f'Processing function {i+1}/{len(rewrites)}')
    outputs = master_invocations[function_name]['outputs']
    results[function_name] = []
    for j, invocation in enumerate(outputs.keys()):

        if results.get(function_name) is not None:
            continue

        print(f'Processing invocation {j+1}/{len(outputs)}. Invocation {i+1}/{len(rewrites)}')
        if outputs[invocation][0] == 'stdout':
            expected = outputs[invocation][1]
        else:
            print(f'Error: invocation {invocation} is not stdout')
            continue
        # execute rewritten code
        result = execute_inputs([invocation])

        # if result is not stdout, save to results array
        if result[invocation][0] != 'stdout' or result[invocation][1] != expected:
            results[function_name].append({
                'status': 'failed',
                'expected': expected,
                'actual': result[invocation][1],
                'invocation': invocation,
            })
        else:
            results[function_name].append({
                'status': 'passed',
                'expected': expected,
                'actual': result[invocation][1],
                'invocation': invocation,
            })
        print(f'Invocation {j+1}/{len(outputs)} {results[function_name][0]["status"]}')

#save results to json
with open("results.json", "w") as f:
    json.dump(results, f, indent=4)

# print each function with the count of passed and failed invocations
for function_name in results.keys():
    passed = 0
    failed = 0
    for invocation in results[function_name]:
        if invocation['status'] == 'passed':
            passed += 1
        elif invocation['status'] == 'failed':
            failed += 1
    print(f'{function_name}: {passed} passed, {failed} failed')