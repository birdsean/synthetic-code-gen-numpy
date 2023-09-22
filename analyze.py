# read master_invocations.json
import json

invocations = json.load(open("master_invocations.json", "r"))

successes = []

# each key of invocations is a function name
# for each function name, get a count of outputs that have the key 'stderr' and 'stdout', print results
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
    print(f"{function_name}: {stderr_count} stderr, {stdout_count} stdout")
    if stdout_count > 0:
        successes.append(function_name)

print(f'{len(successes)} of {len(invocations.keys())} functions have at least one successful invocation. Percent: {(len(successes)/len(invocations.keys())):.2f}')
