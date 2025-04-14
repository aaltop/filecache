from typing import Callable, Any

def all_instance_of(type, *instances):
    '''
    Determine whether `instances` are all instances of `type`.
    '''
    return all(map(lambda inst: isinstance(inst, type), instances))

type CompareFuncs = list[Callable[[Any,Any], bool | None]] | None

def compare_dict_values(dict1: dict, dict2: dict, comparison_funcs: CompareFuncs = None):
    '''
    Compare the values in dict1 and dict2.
    Returns a dictionary with each key in dict1
    as keys and booleans as values denoting whether the dicts differ
    on the given key. No match for a key in `dict2` is considered a
    differ. NOTE: function is not commutative.

    Arguments:
        dict1:
        dict2:
        comparison_funcs:
            A list of callables that accept values from `dict1` and `dict2`.
            If the passed values cannot be compared with a callable,
            it should return None. If the values are equal under the
            comparison, return True, else False.

            If no callable is able to compare the values, the simple
            equality comparison is defaulted to (including when
            `comparison_func` is empty or None).
    '''

    def dict_equality(dict1, dict2):
        if all_instance_of(dict, dict1, dict2):
            return not any(compare_dict_values(dict1, dict2, comparison_funcs).values())

    comp = {}
    for key, value in dict1.items():

        value_in_other = dict2.get(key)
        if value_in_other is None:
            comp[key] = True
            continue
        
        comparison_funcs = [] if comparison_funcs is None else comparison_funcs
        comparison_funcs = [dict_equality] + comparison_funcs
        for comparison_func in comparison_funcs:
            result = comparison_func(value, value_in_other)
            if not (result is None):
                if not isinstance(result, bool):
                    print(value, value_in_other)
                    print(result, type(result), isinstance(result, bool))
                    raise TypeError("Result of comparison should be None, True, or False")
                # invert for differ
                comp[key] = not result
                break
        
        if not key in comp:
            # default to basic equality comparison
            comp[key] = value != value_in_other

    return comp