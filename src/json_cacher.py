'''
Base class that saves its cache as JSON.
'''

import hashlib
import abc
from pathlib import Path
import json

from .abstract_cacher import AbstractCacher, CacherState

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

    def get_cache_for_state(self) -> dict:
        return super().get_cache_for_state()
    
    def cache_from_state_cache(self, state_cache) -> dict:
        return super().cache_from_state_cache(state_cache)
    
    def get_state(self) -> CacherState[dict]:
        return super().get_state()
    
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
    
    def load(self, path: Path = None) -> CacherState[dict]:
        '''
        Load the state as saved by `save()`.
        '''

        path = self.save_path if path is None else path

        with open(path) as f:
            saved_cache = json.load(f)

        return saved_cache