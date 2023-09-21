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
            "new section titled ANSWER where you write the answer to the prompt, following instructions perfectly regarding formatting."
        },
        {
            "role": "user", 
            "content": "Given the following function:\n```" + function_code + "\n```\nReturn a list of inputs that would thoroughly test "+\
            "the capabilities of the function. Your answer should be a list of at three to ten new line separated list of cases, where each "+\
            "case is a comma separated list of function parameter values. For example, if the function was slice_string(str, start_index, "+\
            "end_index), your answer would look something like:\n\nANSWER:\n'foobar',0,3\n'test_string_2,0,0'\nJust respond with inputs, no "+\
            "commentary, numbering, labels, or bullet points. If the param value is a string, be sure to surround it with double quotes."}
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

def execute_inputs(function_name, invocations):
    #  Execute `docker run numpy python ...` and collect the function outputs
    cmds = []
    for invocation in invocations:
        # remove all backslashes form invocation
        cmd = f"docker run numpy python -c 'import numpy as np; print(np.{function_name}({invocation}))'"
        cmds.append(cmd)
    return cmds

# generated via dir(np)
PUBLIC_FUNCTIONS = ['ALLOW_THREADS', 'BUFSIZE', 'CLIP', 'DataSource', 'ERR_CALL', 'ERR_DEFAULT', 'ERR_IGNORE', 'ERR_LOG', 'ERR_PRINT', 'ERR_RAISE', 'ERR_WARN', 'FLOATING_POINT_SUPPORT', 'FPE_DIVIDEBYZERO', 'FPE_INVALID', 'FPE_OVERFLOW', 'FPE_UNDERFLOW', 'False_', 'Inf', 'Infinity', 'MAXDIMS', 'MAY_SHARE_BOUNDS', 'MAY_SHARE_EXACT', 'NAN', 'NINF', 'NZERO', 'NaN', 'PINF', 'PZERO', 'RAISE', 'RankWarning', 'SHIFT_DIVIDEBYZERO', 'SHIFT_INVALID', 'SHIFT_OVERFLOW', 'SHIFT_UNDERFLOW', 'ScalarType', 'True_', 'UFUNC_BUFSIZE_DEFAULT', 'UFUNC_PYVALS_NAME', 'WRAP', '_CopyMode', '_NoValue', '_UFUNC_API', '__NUMPY_SETUP__', '__all__', '__builtins__', '__cached__', '__config__', '__deprecated_attrs__', '__dir__', '__doc__', '__expired_functions__', '__file__', '__former_attrs__', '__future_scalars__', '__getattr__', '__loader__', '__name__', '__package__', '__path__', '__spec__', '__version__', '_add_newdoc_ufunc', '_builtins', '_distributor_init', '_financial_names', '_get_promotion_state', '_globals', '_int_extended_msg', '_mat', '_no_nep50_warning', '_pyinstaller_hooks_dir', '_pytesttester', '_set_promotion_state', '_specific_msg', '_typing', '_using_numpy2_behavior', '_utils', 'abs', 'absolute', 'add', 'add_docstring', 'add_newdoc', 'add_newdoc_ufunc', 'all', 'allclose', 'alltrue', 'amax', 'amin', 'angle', 'any', 'append', 'apply_along_axis', 'apply_over_axes', 'arange', 'arccos', 'arccosh', 'arcsin', 'arcsinh', 'arctan', 'arctan2', 'arctanh', 'argmax', 'argmin', 'argpartition', 'argsort', 'argwhere', 'around', 'array', 'array2string', 'array_equal', 'array_equiv', 'array_repr', 'array_split', 'array_str', 'asanyarray', 'asarray', 'asarray_chkfinite', 'ascontiguousarray', 'asfarray', 'asfortranarray', 'asmatrix', 'atleast_1d', 'atleast_2d', 'atleast_3d', 'average', 'bartlett', 'base_repr', 'binary_repr', 'bincount', 'bitwise_and', 'bitwise_not', 'bitwise_or', 'bitwise_xor', 'blackman', 'block', 'bmat', 'bool_', 'broadcast', 'broadcast_arrays', 'broadcast_shapes', 'broadcast_to', 'busday_count', 'busday_offset', 'busdaycalendar', 'byte', 'byte_bounds', 'bytes_', 'c_', 'can_cast', 'cast', 'cbrt', 'cdouble', 'ceil', 'cfloat', 'char', 'character', 'chararray', 'choose', 'clip', 'clongdouble', 'clongfloat', 'column_stack', 'common_type', 'compare_chararrays', 'compat', 'complex128', 'complex256', 'complex64', 'complex_', 'complexfloating', 'compress', 'concatenate', 'conj', 'conjugate', 'convolve', 'copy', 'copysign', 'copyto', 'corrcoef', 'correlate', 'cos', 'cosh', 'count_nonzero', 'cov', 'cross', 'csingle', 'ctypeslib', 'cumprod', 'cumproduct', 'cumsum', 'datetime64', 'datetime_as_string', 'datetime_data', 'deg2rad', 'degrees', 'delete', 'deprecate', 'deprecate_with_doc', 'diag', 'diag_indices', 'diag_indices_from', 'diagflat', 'diagonal', 'diff', 'digitize', 'disp', 'divide', 'divmod', 'dot', 'double', 'dsplit', 'dstack', 'dtype', 'dtypes', 'e', 'ediff1d', 'einsum', 'einsum_path', 'emath', 'empty', 'empty_like', 'equal', 'errstate', 'euler_gamma', 'exceptions', 'exp', 'exp2', 'expand_dims', 'expm1', 'extract', 'eye', 'fabs', 'fastCopyAndTranspose', 'fft', 'fill_diagonal', 'find_common_type', 'finfo', 'fix', 'flatiter', 'flatnonzero', 'flexible', 'flip', 'fliplr', 'flipud', 'float128', 'float16', 'float32', 'float64', 'float_', 'float_power', 'floating', 'floor', 'floor_divide', 'fmax', 'fmin', 'fmod', 'format_float_positional', 'format_float_scientific', 'format_parser', 'frexp', 'from_dlpack', 'frombuffer', 'fromfile', 'fromfunction', 'fromiter', 'frompyfunc', 'fromregex', 'fromstring', 'full', 'full_like', 'gcd', 'generic', 'genfromtxt', 'geomspace', 'get_array_wrap', 'get_include', 'get_printoptions', 'getbufsize', 'geterr', 'geterrcall', 'geterrobj', 'gradient', 'greater', 'greater_equal', 'half', 'hamming', 'hanning', 'heaviside', 'histogram', 'histogram2d', 'histogram_bin_edges', 'histogramdd', 'hsplit', 'hstack', 'hypot', 'i0', 'identity', 'iinfo', 'imag', 'in1d', 'index_exp', 'indices', 'inexact', 'inf', 'info', 'infty', 'inner', 'insert', 'int16', 'int32', 'int64', 'int8', 'int_', 'intc', 'integer', 'interp', 'intersect1d', 'intp', 'invert', 'is_busday', 'isclose', 'iscomplex', 'iscomplexobj', 'isfinite', 'isfortran', 'isin', 'isinf', 'isnan', 'isnat', 'isneginf', 'isposinf', 'isreal', 'isrealobj', 'isscalar', 'issctype', 'issubclass_', 'issubdtype', 'issubsctype', 'iterable', 'ix_', 'kaiser', 'kernel_version', 'kron', 'lcm', 'ldexp', 'left_shift', 'less', 'less_equal', 'lexsort', 'lib', 'linalg', 'linspace', 'little_endian', 'load', 'loadtxt', 'log', 'log10', 'log1p', 'log2', 'logaddexp', 'logaddexp2', 'logical_and', 'logical_not', 'logical_or', 'logical_xor', 'logspace', 'longcomplex', 'longdouble', 'longfloat', 'longlong', 'lookfor', 'ma', 'mask_indices', 'mat', 'matmul', 'matrix', 'max', 'maximum', 'maximum_sctype', 'may_share_memory', 'mean', 'median', 'memmap', 'meshgrid', 'mgrid', 'min', 'min_scalar_type', 'minimum', 'mintypecode', 'mod', 'modf', 'moveaxis', 'msort', 'multiply', 'nan', 'nan_to_num', 'nanargmax', 'nanargmin', 'nancumprod', 'nancumsum', 'nanmax', 'nanmean', 'nanmedian', 'nanmin', 'nanpercentile', 'nanprod', 'nanquantile', 'nanstd', 'nansum', 'nanvar', 'nbytes', 'ndarray', 'ndenumerate', 'ndim', 'ndindex', 'nditer', 'negative', 'nested_iters', 'newaxis', 'nextafter', 'nonzero', 'not_equal', 'numarray', 'number', 'obj2sctype', 'object_', 'ogrid', 'oldnumeric', 'ones', 'ones_like', 'outer', 'packbits', 'pad', 'partition', 'percentile', 'pi', 'piecewise', 'place', 'poly', 'poly1d', 'polyadd', 'polyder', 'polydiv', 'polyfit', 'polyint', 'polymul', 'polynomial', 'polysub', 'polyval', 'positive', 'power', 'printoptions', 'prod', 'product', 'promote_types', 'ptp', 'put', 'put_along_axis', 'putmask', 'quantile', 'r_', 'rad2deg', 'radians', 'random', 'ravel', 'ravel_multi_index', 'real', 'real_if_close', 'rec', 'recarray', 'recfromcsv', 'recfromtxt', 'reciprocal', 'record', 'remainder', 'repeat', 'require', 'reshape', 'resize', 'result_type', 'right_shift', 'rint', 'roll', 'rollaxis', 'roots', 'rot90', 'round', 'round_', 'row_stack', 's_', 'safe_eval', 'save', 'savetxt', 'savez', 'savez_compressed', 'sctype2char', 'sctypeDict', 'sctypes', 'searchsorted', 'select', 'set_numeric_ops', 'set_printoptions', 'set_string_function', 'setbufsize', 'setdiff1d', 'seterr', 'seterrcall', 'seterrobj', 'setxor1d', 'shape', 'shares_memory', 'short', 'show_config', 'show_runtime', 'sign', 'signbit', 'signedinteger', 'sin', 'sinc', 'single', 'singlecomplex', 'sinh', 'size', 'sometrue', 'sort', 'sort_complex', 'source', 'spacing', 'split', 'sqrt', 'square', 'squeeze', 'stack', 'std', 'str_', 'string_', 'subtract', 'sum', 'swapaxes', 'take', 'take_along_axis', 'tan', 'tanh', 'tensordot', 'test', 'testing', 'tile', 'timedelta64', 'trace', 'tracemalloc_domain', 'transpose', 'trapz', 'tri', 'tril', 'tril_indices', 'tril_indices_from', 'trim_zeros', 'triu', 'triu_indices', 'triu_indices_from', 'true_divide', 'trunc', 'typecodes', 'typename', 'ubyte', 'ufunc', 'uint', 'uint16', 'uint32', 'uint64', 'uint8', 'uintc', 'uintp', 'ulonglong', 'unicode_', 'union1d', 'unique', 'unpackbits', 'unravel_index', 'unsignedinteger', 'unwrap', 'ushort', 'vander', 'var', 'vdot', 'vectorize', 'version', 'void', 'vsplit', 'vstack', 'where', 'who', 'zeros', 'zeros_like']

functions = get_all_functions()

# if function_name is not in PUBLIC_FUNCTIONS, then remove it from functions
for function_name in list(functions.keys()):
    if function_name not in PUBLIC_FUNCTIONS:
        del functions[function_name]

function_name = list(functions.keys())[1]
file_address = functions[function_name]
function_code = get_function_code(function_name, file_address)

raw_inputs = get_potential_inputs(function_code)
# print(f'Raw inputs: {raw_inputs}')
invocations = get_invocations(function_name, raw_inputs)
# print(f'Invocations: {invocations}')

outputs = execute_inputs(function_name, invocations)
for exec in outputs:
    # print each exec without backslashes
    print(exec.replace("\\", ""))
