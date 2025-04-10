


def compare_dict_values(dict1: dict, dict2: dict):
    '''
    Compare the values in dict1 and dict2.
    Returns a dictionary with each key in dict1
    as keys and booleans as values denoting whether the dicts differ
    on the given key. No match for a key in `dict2` is considered a
    differ. NOTE: function is not commutative.
    '''

    comp = {}
    for key, value in dict1.items():

        value_in_other = dict2.get(key)
        comp[key] = True if value_in_other is None else (value_in_other != value)
    
    return comp