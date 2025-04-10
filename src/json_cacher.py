'''
Base class that saves its cache as JSON.
'''

import hashlib
import abc
from pathlib import Path
import json

from .abstract_cacher import AbstractCacher

class JsonCacher(AbstractCacher):

    def __init__(self, save_path = None, *args, **kwargs):
        super().__init__(save_path, *args, **kwargs)
        self.cache: dict

        self.save_path = (
            Path() / self.name_as_snake / "cache.json"
            if save_path is None
            else save_path
        )

    @classmethod
    def new_cache(self):
        return {}

    @abc.abstractmethod
    def json_cache(self):
        '''
        Return the cache such that it is suitable for json.load.
        '''

    def get_json_state(self):
        '''
        Get all data relevant to the cacher, suitable for passing
        to json.load.
        '''

        state = self.get_state()
        state["cache"] = self.json_cache()
        return state
    
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