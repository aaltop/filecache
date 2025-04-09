'''
FunctionCache: Class that can be used to wrap functions, caching
their invocations and allowing saving and loading this cache from
file. 
'''

from functools import wraps
import inspect
from typing import (
    NamedTuple, Any, TypedDict
)
from collections.abc import Callable
from collections import deque

import logging
logger = logging.getLogger(__name__)

from .shelve_cacher import ShelveCacher
from src.utils.inspect import (
    function_hash as hash_function,
    bind_arguments
)



class CacheLookup(NamedTuple):
    '''
    Attributes:
        function_hash:
            Used as key in a `FunctionCache` cache
        input:
            Contains the input arguments to the function
        output:
            Contains the previous output from the function
            with the same input arguments.
    '''
    function_hash: str
    input: dict
    output: Any = None

class InputOutputDict(TypedDict):


    input: Any
    output: Any

# TODO:
# Another issue maybe how to work with methods. Just add an option
# to the wrapper for wrapping a method instead?  
class FunctionCacher(ShelveCacher):
    '''
    Class for caching the output from a function, such that the cache
    may also be saved to file.

    Properties:
        cache:
            Contains the cached data.
    '''

    def __init__(self, cache_size: int | None = None, *args, **kwargs):
        '''
        
        Arguments:
            cache_size:
                How large the LRU cache should be. Currently will affect
                only fresh function invocations: if a function invocation
                is already cached, the deque's max length has already
                been set.
        '''

        super().__init__(*args, **kwargs)
        self.cache: dict[str, deque[InputOutputDict]]

        self.cache_size = cache_size

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
        if function_hash in self.cache:
            for input_output in self.cache[function_hash]:
                previous_args = input_output["input"]
                if not (previous_args == bound_args):
                    continue
                # move the found cache value to the front of the deque
                # ----------------------------------------------------
                deq = self.cache[function_hash]
                # not going to continue the loop, so doesn't matter
                deq.remove(input_output)
                deq.appendleft(input_output)
                # ===================================================
                previous_output = input_output["output"]
                logger.debug("Found previous value, returning early")
                return CacheLookup(function_hash, bound_args, previous_output)

        else:
            self.cache[function_hash] = deque(maxlen = self.cache_size)

        # should be that there is key of <function_hash> yet
        self.cache[function_hash].appendleft({"input": bound_args, "output": None})
        return CacheLookup(function_hash, bound_args, None)
    
    def __call__(self):

        def inner_wrapper(func):

            @wraps(func)
            def wrapper_func(*args, **kwargs):


                function_hash, _, output = self.lookup_function(func, args, kwargs)
                if not (output is None):
                    return output
                
                output = func(*args, **kwargs)
                # the new invocation should be the first item
                # (most recently used)
                self.cache[function_hash][0] |= {"output": output}
                return output
            
            return wrapper_func
        
        return inner_wrapper


