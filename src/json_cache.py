'''
Base class that saves its cache as JSON.
'''

import hashlib
import abc
from pathlib import Path
import json

from .abstract_cache import AbstractCache

class JsonCache(AbstractCache):

    def __init__(self, hasher = lambda: hashlib.sha256(usedforsecurity=False), save_path = None):
        super().__init__(hasher, save_path)

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

    def get_state(self):
        '''
        Get all data relevant to the cacher, suitable for passing
        to json.load.
        '''

        return {
            "metadata": self.metadata(),
            "cache": self.json_cache()
        }
    
    def save(self, path: Path = None, json_kwargs: dict = None):
        '''
        Save the state as a json file.
        '''

        path = self.save_path if path is None else path
        json_kwargs = {} if json_kwargs is None else json_kwargs

        path.parents[0].mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.get_state(), f, **json_kwargs)

        return self
    
    def load(self, path: Path = None) -> dict:
        '''
        Load the state as saved by `save()`.
        '''

        path = self.save_path if path is None else path

        with open(path) as f:
            saved_cache = json.load(f)

        return saved_cache["cache"]