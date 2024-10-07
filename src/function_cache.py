from .abstract_cache import AbstractCache

from functools import wraps
import inspect

class FunctionCache(AbstractCache):

    def json_cache(self):
        return {key: args.arguments for key, args in self.cache.items()}

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
    
    def __call__(self):

        def inner_wrapper(func):

            @wraps(func)
            def wrapper_func(*args, **kwargs):


                self.cache_function(func, args, kwargs)
                func(*args, **kwargs)
            
            return wrapper_func
        
        return inner_wrapper


