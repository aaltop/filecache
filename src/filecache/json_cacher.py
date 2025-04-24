"""
Base class that saves its cache as JSON.
"""

from pathlib import Path
import json

from .abstract_cacher import AbstractCacher, CacherState
from .exceptions import StateNotFoundError


class JsonCacher(AbstractCacher):

    def __init__(self, save_path=None, *args, **kwargs):
        super().__init__(save_path, *args, **kwargs)
        self.cache: dict

    def create_save_path(self, path=None):
        return super().create_save_path(path, file_suffix="json")

    @classmethod
    def new_cache(cls):
        return {}

    def cache_to_state_cache(self) -> dict:
        return super().cache_to_state_cache()

    def state_cache_to_cache(self, state_cache) -> dict:
        return super().state_cache_to_cache(state_cache)

    def get_state(self) -> CacherState[dict]:
        return super().get_state()

    def save(self, path: Path = None, json_kwargs: dict = None):
        """
        Save the state as a json file.
        """

        json_kwargs = dict(indent=4) | ({} if json_kwargs is None else json_kwargs)
        path = self.save_path if path is None else path
        json_kwargs = {} if json_kwargs is None else json_kwargs

        path.parents[0].mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.get_state(), f, **json_kwargs)

        return self

    def load(self, path: Path = None) -> CacherState[dict]:

        path = self.save_path if path is None else path
        try:
            with open(path) as f:
                state = json.load(f)
        except FileNotFoundError:
            raise StateNotFoundError()

        return state

    def clear_file_cache(self, path=None):
        return super().clear_file_cache(path)
