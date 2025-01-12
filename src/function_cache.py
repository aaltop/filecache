from functools import wraps
import inspect
from typing import (
    NamedTuple, Any
)
from collections.abc import Callable

import logging
logger = logging.getLogger(__name__)

from .shelve_cache import ShelveCache
from src.utils.inspect import (
    function_hash as hash_function,
    bind_arguments
)



class CacheLookup(NamedTuple):
    '''
    `function_hash` is used as key in a `FunctionCache` cache,
    `input` contains the input arguments to the function,
    `output` contains the previous output from the function
    with the same input arguments.
    '''
    function_hash: str
    input: dict
    output: Any = None


# TODO:
# Another issue maybe how to work with methods. Just add an option
# to the wrapper for wrapping a method instead?  
class FunctionCache(ShelveCache):
    '''
    Class for caching the output from a function, such that the cache
    may also be saved to file.

    <self.cache> has function hashes (hex strings of the hash of the function
    body) as keys, with each item being a dictionary of keys ("input","output")
    whose values match the input to a function and the output from
    a function.
    '''

    def lookup_function(self, func: Callable, args, kwargs) -> CacheLookup:
        '''
        Look for an invocation of `func()` invoked with
        `args` and `kwargs`, initialising the entry if not found.
        Mainly used internally.
        '''

        hasher = self.hasher()
        function_hash = hash_function(hasher, func)
        bound_args = bind_arguments(func, args, kwargs)

        # look for previous output that matches the function and call signature
        try:
            previous_args = self.cache[function_hash]["input"]
            if previous_args == bound_args:
                previous_output = self.cache[function_hash]["output"]
                logger.debug("Found previous value, returning early")
                return CacheLookup(function_hash, bound_args, previous_output)
        except LookupError:
            logger.debug("No previous data")
            pass

        self.cache[function_hash] = {"input": bound_args, "output": None}
        return CacheLookup(function_hash, bound_args, None)
    
    def __call__(self):

        def inner_wrapper(func):

            @wraps(func)
            def wrapper_func(*args, **kwargs):


                function_hash, _, output = self.lookup_function(func, args, kwargs)
                if not (output is None):
                    return output
                
                output = func(*args, **kwargs)
                self.cache[function_hash] |= {"output": output}
                return output
            
            return wrapper_func
        
        return inner_wrapper


