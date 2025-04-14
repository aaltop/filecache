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
import copy

import logging
logger = logging.getLogger(__name__)

from .shelve_cacher import ShelveCacher
from src.utils.inspect import (
    function_hash as hash_function,
    bind_arguments, unique_name
)
from src.deque_cache import DequeCache
from src.abstract_cacher import CacherState
from src.utils.compare import compare_dict_values, CompareFuncs



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

type Cache = DequeCache[InputOutputDict]

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
        self.cache: Cache # needs a little help with the typing
        self.compare_funcs: CompareFuncs = None
        self._cache_size: int | None = None
        self.cache_size = cache_size
        
        self._function_name_to_hash: dict[str, str] = {}

    @classmethod
    def new_cache(self):
        return DequeCache[InputOutputDict]()
    
    @property
    def cache_size(self):
        return self._cache_size
    
    @cache_size.setter
    def cache_size(self, value):

        self.cache.max_size = value
        self._cache_size = self.cache.max_size

    def hash_function(self, func):
        return hash_function(func, hasher = self.hasher())

    def lookup_function(self,
            func: Callable,
            args,
            kwargs,
            compare_funcs: CompareFuncs = None
        ) -> CacheLookup:
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
                compare_funcs = compare_funcs or self.compare_funcs
                input_output: InputOutputDict = self.cache.find_cached_item(
                    function_hash,
                    bound_args,
                    lambda one, two: not any(compare_dict_values(one, two["input"], compare_funcs).values())
                )
                previous_output = input_output["output"]
                return CacheLookup(function_hash, bound_args, previous_output)
            except LookupError:
                logger.debug("No previous value found")
                pass

        self.cache[function_hash].appendleft({"input": bound_args, "output": None})
        return CacheLookup(function_hash, bound_args, None)
    
    def __call__(self, compare_funcs: CompareFuncs = None):
        '''
        Arguments:
            compare_funcs:
                Functions that are used to compare current input dict's
                values with cached input dicts' values. Each function
                should take a matching pair of function arguments and
                compare them, returning None if not comparable by the
                function, or False or True if the compare equal.
        '''

        def inner_wrapper(func):

            # initialise the cache
            function_hash = self.hash_function(func)
            self.cache[function_hash]
            self._function_name_to_hash[unique_name(func)] = function_hash

            @wraps(func)
            def wrapper_func(*args, **kwargs):


                function_hash, _, output = self.lookup_function(func, args, kwargs, compare_funcs)
                if not (output is None):
                    return copy.deepcopy(output)
                
                output = func(*args, **kwargs)
                # the new invocation should be the first item
                # (most recently used)
                self.cache[function_hash][0] |= {"output": copy.deepcopy(output)}
                return output
            
            return wrapper_func
        
        return inner_wrapper

    def get_cached_data(self, func: Callable) -> deque[InputOutputDict]:
        '''
        Get the cached data of `func`.
        '''

        function_hash = self._function_name_to_hash[unique_name(func)]
        return self.cache[function_hash]
    
    def cache_to_state_cache(self) -> Cache:
        return self.cache
    
    def state_cache_to_cache(self, state_cache: Cache) -> Cache:
        return state_cache
    
    def get_state(self) -> CacherState[Cache]:
        return super().get_state()

    def load(self, path=None) -> CacherState[Cache]:
        return super().load(path)
    
    def load_cache(self, path = None, *args, inplace = False, overwrite_loaded_cache_size = False, **kwargs) -> Cache | Self:
        '''
        See AbstractCacher.

        Arguments:
            overwrite_loaded_cache_size:
                Whether to overwrite the cache size of the loaded in
                cache with the current cache size, or vice versa.
                
                
                By default, the loaded cache's cache size replaces
                the current cache size if the operation is performed
                in place. if not `inplace`, the loaded cache's
                size is replaced if `overwrite_loaded_cache_size` is
                True, but if False, the cacher's (`self`'s)
                cache size is not replaced (i.e. this argument has
                no effect).

        '''
        

        cache = super().load_cache(path, inplace, *args, **kwargs)
        match (inplace, overwrite_loaded_cache_size):
            case (True, True):
                # should set the cache as well
                self.cache_size = self.cache_size
            case (True, False):
                self.cache_size = self.cache.max_size
            case (False, True):
                cache.max_size = self.cache_size

        return super().load_cache(path, inplace = False, *args, **kwargs)
    
    def clear_memory_cache(self):
        for key in self.cache:
            self.cache[key].clear()