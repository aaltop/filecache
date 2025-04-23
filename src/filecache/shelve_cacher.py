'''
Class that saves its cache using the shelve module.
'''

from typing import Self

from .abstract_cacher import AbstractCacher, CacherState
from src.filecache.utils.shelve import load_dict, save_dict, clear_shelve
from src.filecache.exceptions import StateNotFoundError

class ShelveCacher(AbstractCacher):
    '''
    Uses the shelve module to save and load pickled cache data from
    file.
    '''

    @classmethod
    def new_cache(cls):
        return {}

    def get_state(self) -> CacherState[dict]:
        return super().get_state()
    
    def cache_to_state_cache(self) -> dict:
        return super().cache_to_state_cache()
    
    def state_cache_to_cache(self, state_cache, *args, **kwargs) -> dict:
        return super().state_cache_to_cache(state_cache)

    def save(self, path = None) -> Self:
        

        path = (
            self.save_path
            if path is None
            else path
        )

        save_dict(path, self.get_state())
        return self
    
    def load(self, path = None) -> CacherState[dict]:
        
        path = (
            self.save_path
            if path is None
            else path
        )

        state = load_dict(path)
        if not "metadata" in state and not "cache" in state:
            raise StateNotFoundError()
        return state
    
    def load_cache(self, path = None, *args, inplace=False, overwrite_loaded_cache_attributes=False, **kwargs) -> dict | Self:
        return super().load_cache(
            path,
            *args,
            inplace=inplace,
            overwrite_loaded_cache_attributes=overwrite_loaded_cache_attributes,
            **kwargs
        )

    def clear_file_cache(self, path = None):
        clear_shelve(path)
        return self