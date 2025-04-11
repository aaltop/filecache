'''
Class that saves its cache using the shelve module.
'''

from typing import Self

from .abstract_cacher import AbstractCacher, CacherState
from src.utils.shelve import load_dict, save_dict

class ShelveCacher(AbstractCacher):
    '''
    Uses the shelve module to save and load pickled cache data from
    file.
    '''

    @classmethod
    def new_cache(self):
        return {}

    def get_state(self) -> CacherState[dict]:
        return super().get_state()
    
    def get_cache_for_state(self) -> dict:
        return super().get_cache_for_state()
    
    def cache_from_state_cache(self, state_cache) -> dict:
        return super().cache_from_state_cache(state_cache)

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

        return load_dict(path)
    
    def load_cache(self, path = None, inplace=False, *args, **kwargs) -> dict | Self:
        return super().load_cache(path, inplace, *args, **kwargs)

