# only for testing
# ver of 2017-09-01

import inspect
import json
import os

import numpy as np
import pandas as pd


class __settings:

    last = True
    varlist_count = 1


def __value_conv(value):

    num = value

    if not isinstance(num, (str, bool, int, float)):

        # np types
        if isinstance(num, np.number):

            if np.issubdtype(num, int):
                num = int(num)

            elif np.issubdtype(num, float):
                num = float(num)

            elif isinstance(num, (np.uint8, np.uint16, np.uint32, np.uint64)):
                num = int(num)

            elif np.issubdtype(num, np.complex):
                num = str(num)

            else:
                num = str(num)

        elif isinstance(num, np.datetime64):
            num = np.datetime_as_string(num)

        elif isinstance(num, np.bool_):
            num = bool(num)


        # complex types recursion
        # DataFrame, np arrays
        elif isinstance(num, pd.core.frame.DataFrame):
            num = num.applymap(__value_conv).to_dict()

        elif isinstance(num, np.ndarray):
            fun = np.vectorize(__value_conv)
            num = fun(num).tolist()

        # list, dict
        elif isinstance(num, list):
            num = [__value_conv(i) for i in num]

        elif isinstance(num, dict):
            num = dict(zip([i for i in num.keys()], [__value_conv(j) for j in num.values()]))

        # other - to string
        else:
            num = str(num)

    return num


def __varname(var, last=__settings.last):

    for fi in reversed(inspect.stack()):
        names = [var_name for var_name, var_val in fi.frame.f_locals.items() if var_val is var]

        if len(names) > 0:
            if last:
                return names[-1]
            else:
                return names[0]


def __serialize(var, name, check_values):

    if name == '':
        name = __varname(var)

    if check_values:

        if isinstance(var, pd.core.frame.DataFrame):
            type_var = 'DF'
            serialized_var = json.dumps(var.applymap(__value_conv).to_dict(orient='list'))

        elif isinstance(var, np.ndarray):
            type_var = 'MA'
            fun1 = np.vectorize(__value_conv)
            serialized_var = json.dumps(dict(zip([str(i) for i in range(1, len(var.tolist()) + 1)], fun1(var).tolist())))

        else:
            type_var = 'RAW'

            if isinstance(var, list):
                serialized_var = json.dumps([__value_conv(i) for i in var])
            elif isinstance(var, dict):
                serialized_var = json.dumps(dict(zip([i for i in var.keys()], [__value_conv(j) for j in var.values()])))
            else:
                serialized_var = json.dumps(__value_conv(var))

    else:

        if isinstance(var, pd.core.frame.DataFrame):
            type_var = 'DF'
            serialized_var = json.dumps(var.to_dict(orient='list'))

        elif isinstance(var, np.ndarray):
            type_var = 'MA'
            serialized_var = json.dumps(dict(zip([str(i) for i in range(1, len(var.tolist()) + 1)], var.tolist())))

        else:
            type_var = 'RAW'
            serialized_var = json.dumps(var)


    len_var = len(serialized_var)

    _dict = {'{}&%&{}&%&{}'.format(len_var, type_var, name): serialized_var}

    return _dict


def __packing(var, varname, varlist, check_values):

    name = varname
    packed = ''

    if not varlist:

        if name != '':
            assert isinstance(name, str), 'Varname must be a string. In other case you need to check "varlist" parameter.'

        packed = json.dumps(__serialize(var, name, check_values))

    elif varlist:

        if name == '':

            listvars = var
            _vars = []

            for _var in listvars:
                _vars.append(__serialize(_var, name, check_values))

            varlist_name = 'varlist_' + str(__settings.varlist_count)
            __settings.varlist_count += 1

            len_var = len(json.dumps(_vars))
            type_var = 'VL'

            packed = json.dumps({'{}&%&{}&%&{}'.format(len_var, type_var, varlist_name): _vars})


        elif name != '':

            assert isinstance(name, (list, tuple)), 'Varname must be a list or a tuple'
            assert len(var) == len(name), 'The number of given varnames does not match the number of given variables'

            _vars = []

            for _name, _var in zip(name, var):
                _vars.append(__serialize(_var, _name, check_values))

            varlist_name = 'varlist_' + str(__settings.varlist_count)
            __settings.varlist_count += 1

            len_var = len(json.dumps(_vars))
            type_var = 'VL'

            packed = json.dumps({'{}&%&{}&%&{}'.format(len_var, type_var, varlist_name): _vars})

    return packed


def __var_info(var):

    size_var, type_var, name_var = list(json.loads(var).items())[0][0].split('&%&')
    size_var = int(size_var)

    return size_var, type_var, name_var


def __var_content(var):

    return list(json.loads(var).items())[0][1]


def __unserialize(string):

    type_var = __var_info(string)[1]

    if type_var == 'RAW':
        return json.loads(__var_content(string))

    elif type_var == 'DF':
        return pd.DataFrame(json.loads(__var_content(string)))

    elif type_var == 'MA':
        return np.matrix(list(json.loads(__var_content(string)).values()))


def __unpacking(string):

    type_var = __var_info(string)[1]

    if type_var == 'VL':

        _vars = []
        for var in __var_content(string):
            _vars.append(__unserialize(json.dumps(var)))
        
        return tuple(_vars)

    else:
        return __unserialize(string)


def __varlist_names(string):

    assert __var_info(string)[1] == 'VL', 'It is not a varlist'

    varnames = []

    for var in __var_content(string):
        varnames.append(__var_info(json.dumps(var))[2])

    return varnames


def __varlist_lenght(string):

    assert __var_info(string)[1] == 'VL', 'It is not a varlist'
    return len(__var_content(string))


# -----------------------------------------------------------------------
# -----------------------------------------------------------------------


def save_var(variable, filename, path='', varname='', varlist=False, check_values=False):

    """save(variable, filename, path='', varname='', varlist=False)

Where:
    - path (optional) - a string with a path
    If you don't specify the place, path will be equal to current working directory.
    You can check your current WD by calling '[imported module].getwd()

    - varname (optional) - a string with a single variable name or a list/tuple with a list of variable names in
    varlist (if you want to save all them to one file).

    - varlist (optional) - a boolean that specifies whether 'variable' parameter gets a single variable
    or a list of other variables.
    If you want to save all variables of your current environment at once, you should do the following:
        - put all of your variables into a list like [var_A, var_B, etc...]
        - pass this list into 'variable' parameter
        - switch 'varlist' to 'True'
        - save by this function
        - Profit!
    """

    filename = filename + '.rpba'
    spath = os.path.join(path, filename)

    with open(spath, 'w', encoding='utf-8') as f:
        f.write(__packing(variable, varname, varlist, check_values))
        f.write('\n')

    if path == '':
        saved_to = os.path.join(os.getcwd(), filename)
    else:
        saved_to = spath

    print('Successfully saved to {}'.format(saved_to))

    return



def load_var(filename, path=''):

    """Returns variable(s) from .rpba file. To get the additional information about file use info() function.

load(filename, path='')

Where:
    - path (optional) - a string with a path, where .rpba file are located.
    If you don't specify the path, it will be equal to current working directory.
    You can check your current WD by calling '[imported module].getwd()
    """

    spath = os.path.join(path, filename)

    with open(spath, 'r', encoding='utf-8') as f:
        _vars = __unpacking(f.readline())

    return _vars



def getwd():
    return os.getcwd()


def info_rpba(filename, path=''):

    """Returns information about an .rpba file (in the dict format)"""

    spath = os.path.join(path, filename)

    with open(spath, 'r', encoding='utf-8') as f:
        string = f.readline()

    if __var_info(string)[1] == 'VL':

        lenght = __varlist_lenght(string)
        names = __varlist_names(string)

        return {'type': 'varlist', 'lenght': lenght, 'varnames': names}

    elif __var_info(string)[1] == 'MA':
        return {'type': 'matrix'}

    elif __var_info(string)[1] == 'DF':
        return {'type': 'DataFrame'}

    elif __var_info(string)[1] == 'RAW':
        return {'type': 'single_variable'}
