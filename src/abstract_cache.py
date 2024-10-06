from src.utils.string import pascal_to_snake_case

import abc
import hashlib
from pathlib import Path
import json

def compare_dict_values(dict1, dict2):
    '''
    Compare the values in dict1 and dict2.
    Returns a dictionary with each key in dict1
    as keys and booleans as values denoting whether the dicts differ
    on the given key. No match for a key in `dict2` is considered a
    differ. NOTE: function is not commutative.
    '''

    comp = {}
    for key, value in dict1.items():

        value_in_other = dict2.get(key)
        comp[key] = True if value_in_other is None else (value_in_other != value)
    
    return comp


class AbstractCache(abc.ABC):

    name_as_snake = None

    @classmethod
    def _calculate_name(cls):

        cls.name_as_snake = pascal_to_snake_case(cls.__name__)

    def __init__(self, hasher = lambda: hashlib.sha256(usedforsecurity=False), save_path = None):
        '''
        `hasher` is expected to be a hashlib-type hasher factory.

        `save_path` is the path to save the cache to, by default 
        "./{class_name}/cache.json", where {class_name} is the name
        of the class in snake case. (Assumes that the class name is
        Pascal case.)
        '''

        if AbstractCache.name_as_snake is None:
            self._calculate_name()

        self.hasher = hasher
        self.cache = {}
        self.save_path = (
            Path() / self.name_as_snake / "cache.json"
            if save_path is None 
            else save_path
        )

    @abc.abstractmethod
    def json_cache(self):
        '''
        Return the cache such that it is suitable for json.load.
        '''

    def metadata(self):
        '''
        Get metadata about this cacher.
        '''

        return {
            "hash_algorithm": self.hasher().name
        }
    
    def get_state(self):
        '''
        Get all data relevant to the cacher, suitable for passing
        to json.load.
        '''

        return {
            "metadata": self.metadata(),
            "cache": self.json_cache()
        }
    
    def save(self, path:Path = None, json_kwargs: dict = None):
        '''
        Save the state as a json file.
        '''

        path = self.save_path if path is None else path
        json_kwargs = {} if json_kwargs is None else json_kwargs

        path.parents[0].mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.get_state(), f, **json_kwargs)

        return self
    
    def load(self, path:Path = None) -> dict:
        '''
        Load the state as saved by `save()`.
        '''

        path = self.save_path if path is None else path

        with open(path) as f:
            saved_cache = json.load(f)

        return saved_cache["cache"]
    

    def compare_hashes(self, other = None):
        '''
        Compare the values in `self.cache` and in `other` using
        `compare_dict_values()`.

        By default `other` is gotten using `self.load()`.
        '''

        other = self.load() if other is None else other

        return compare_dict_values(self.cache, other)