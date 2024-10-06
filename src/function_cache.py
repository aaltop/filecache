from functools import wraps
import inspect
import hashlib
from pathlib import Path
import json


class FunctionCache:


    def __init__(self, hasher = lambda: hashlib.sha256(usedforsecurity=False), save_path = None):
        '''
        `hasher` is expected to be a hashlib-type hasher factory.

        `save_path` is the path to save the cache to, by default 
        "./file_cache/cache.json"
        '''

        self.hasher = hasher
        self.cache = {}
        self.save_path = (
            Path() / "function_cache" / "cache.json"
            if save_path is None 
            else save_path
        )

    def dict_cache(self):
        '''
        Return the cache with the arguments dict as a regular dict.
        '''
        return {key: args.arguments for key, args in self.cache.items()}
    
    def str_cache(self):
        '''
        Return the cache as a JSON-compliant string.
        '''

        return json.dumps(self.dict_cache())

    def cache_function(self, func, args, kwargs):
        '''
        Cache the invocation of `func()` which was invoked with
        `args` and `kwargs`.

        Return the hex hash of the function (used as key in cache) and 
        the dictionary of the used arguments (used as value in cache).
        '''

        hasher = self.hasher()
        hasher.update(bytes(inspect.getsource(func), encoding="utf-8"))
        function_hash = hasher.hexdigest()
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        self.cache[function_hash] = bound_args
        return (function_hash, bound_args)

def function_cache_wrapper(cacher: FunctionCache):
    '''
    Wrap a function to have it's invocations be saved in `cacher`.
    '''

    def inner_wrapper(func):

        @wraps(func)
        def wrapper_func(*args, **kwargs):


            cacher.cache_function(func, args, kwargs)
            func(*args, **kwargs)
        
        return wrapper_func
    
    return inner_wrapper


