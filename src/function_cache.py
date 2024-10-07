from .abstract_cache import AbstractCache

from functools import wraps
import inspect
import typing

import logging
logger = logging.getLogger(__name__)

class CacheFunctionReturn(typing.NamedTuple):
    '''
    `function_hash` is used as key in a `FunctionCache` cache,
    `input_args` contains the input arguments to the function,
    `previous_output` contains the previous output from the function
    with the same input arguments.
    '''
    function_hash: str
    input_args: dict
    previous_output: typing.Any = None



class FunctionCache(AbstractCache):
    '''
    Class for caching the output from a function, such that the cache
    may also be saved to file.

    <self.cache> has function hashes (hex strings of the hash of the function
    body) as keys, with each item being a dictionary of keys ("input","output")
    whose values match the input to a function and the output from
    a function.
    '''

    def json_cache(self):
        return self.cache

    def cache_function(self, func, args, kwargs) -> CacheFunctionReturn:
        '''
        Cache the invocation of `func()` which was invoked with
        `args` and `kwargs`.
        '''

        hasher = self.hasher()
        hasher.update(bytes(inspect.getsource(func), encoding="utf-8"))
        function_hash = hasher.hexdigest()
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        bound_args = bound_args.arguments

        # look for previous output that matches the function and call signature
        try:
            previous_args = self.cache[function_hash]["input"]
            if previous_args == bound_args:
                previous_output = self.cache[function_hash]["output"]
                logger.debug("Found previous value, returning early")
                return CacheFunctionReturn(function_hash, bound_args, previous_output)
        except LookupError:
            logger.debug("No previous data")
            pass

        self.cache[function_hash] = {"input": bound_args, "output": None}
        return CacheFunctionReturn(function_hash, bound_args, None)
    
    def __call__(self):

        def inner_wrapper(func):

            @wraps(func)
            def wrapper_func(*args, **kwargs):


                function_hash, _, output = self.cache_function(func, args, kwargs)
                if not (output is None):
                    return output
                
                output = func(*args, **kwargs)
                self.cache[function_hash] |= {"output": output}
                return output
            
            return wrapper_func
        
        return inner_wrapper


