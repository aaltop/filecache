'''
FunctionCache: Class that can be used to wrap functions, caching
their invocations and allowing saving and loading this cache from
file. 
'''

from functools import wraps
from typing import (
    NamedTuple, Any, TypedDict, Self
)
from collections.abc import Callable
from collections import deque

import logging
logger = logging.getLogger(__name__)

from .shelve_cacher import ShelveCacher
from src.utils.inspect import (
    function_hash as hash_function,
    bind_arguments, unique_name
)
from .deque_cache import DequeCache
from src.abstract_cacher import CacherState



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

def _compare_inputs(expected_input, deque_object: InputOutputDict):

    return expected_input == deque_object["input"]

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
        cache_size:
            The currently set size of the deques in the cache.
    '''

    def __init__(self, cache_size: int | None = None, *args, **kwargs):
        '''
        
        Arguments:
            cache_size:
                How large the LRU caches should be.
        '''

        super().__init__(*args, **kwargs)
        self.cache: DequeCache # needs a little help with the typing
        self.cache.compare_deque_objects = _compare_inputs
        self._cache_size: int | None = None
        self.cache_size = cache_size
        
        self._function_name_to_hash: dict[str, str] = {}

    @classmethod
    def new_cache(self):
        return DequeCache()
    
    @property
    def cache_size(self):
        return self._cache_size
    
    @cache_size.setter
    def cache_size(self, value):

        self.cache.max_size = value
        self._cache_size = self.cache.max_size

    def hash_function(self, func):
        return hash_function(func, hasher = self.hasher())

    def lookup_function(self, func: Callable, args, kwargs) -> CacheLookup:
        '''
        Look for an invocation of `func()` invoked with
        `args` and `kwargs`, initialising the entry if not found.
        Mainly used internally.
        '''

        function_hash = self.hash_function(func)
        bound_args = bind_arguments(func, args, kwargs)

        # look for previous output that matches the function and call signature
        if function_hash in self.cache:
            try:
                input_output: InputOutputDict = self.cache.find_cached_item(function_hash, bound_args)
                previous_output = input_output["output"]
                return CacheLookup(function_hash, bound_args, previous_output)
            except LookupError:
                logger.debug("No previous value found")
                pass

        self.cache[function_hash].appendleft({"input": bound_args, "output": None})
        return CacheLookup(function_hash, bound_args, None)
    
    def __call__(self):

        def inner_wrapper(func):

            # initialise the cache
            function_hash = self.hash_function(func)
            self.cache[function_hash]
            self._function_name_to_hash[unique_name(func)] = function_hash

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

    def get_cached_data(self, func: Callable) -> deque[InputOutputDict]:
        '''
        Get the cached data of `func`.
        '''

        function_hash = self._function_name_to_hash[unique_name(func)]
        return self.cache[function_hash]
    
    def cache_to_state_cache(self) -> DequeCache:
        return self.cache
    
    def state_cache_to_cache(self, state_cache: DequeCache) -> DequeCache:
        return state_cache
    
    def get_state(self) -> CacherState[DequeCache]:
        return super().get_state()

    def load(self, path=None) -> CacherState[DequeCache]:
        return super().load(path)
    
    def load_cache(self, path=None, inplace=False, *args, **kwargs) -> DequeCache | Self:
        return super().load_cache(path, inplace, *args, **kwargs)