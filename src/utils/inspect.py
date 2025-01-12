import inspect as base_inspect
from collections.abc import Callable


def function_hash(hasher, function: Callable)  -> str:
    '''
    Get the hexdigest of `function` (hex string of the hash of the function
    body) using the hashlib-compliant `hasher`.
    '''

    hasher.update(bytes(base_inspect.getsource(function), encoding="utf-8"))
    function_hash = hasher.hexdigest()
    return function_hash

def bind_arguments(func: Callable, args, kwargs):
    '''
    Bind the arguments `args` and `kwargs` based on the call signature
    of `function`.
    '''

    sig = base_inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    return bound_args.arguments