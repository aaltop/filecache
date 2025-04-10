import inspect as base_inspect
from collections.abc import Callable
from hashlib import sha256

from src.typing import Hasher


def function_hash(function: Callable, *, hasher: Hasher | None = None)  -> str:
    '''
    Get the hexdigest of `function` (hex string of the hash of the function
    body).

    Arguments:
        function:
        hasher:
            Hashlib-compliant hasher, defaults to non-secure sha256.
    '''

    hasher = sha256(usedforsecurity=False) if hasher is None else hasher
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