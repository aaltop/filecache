from typing import Self


from .abstract_cache import AbstractCache
from src.utils.shelve import load_dict, save_dict

class ShelveCache(AbstractCache):
    '''
    Uses the shelve module to save and load pickled cache data from
    file.
    '''


    def save(self, path = None) -> Self:
        

        path = (
            self.save_path
            if path is None
            else path
        )

        save_dict(path, self.cache)
        return self
    
    def load(self, path = None) -> dict:
        
        path = (
            self.save_path
            if path is None
            else path
        )

        return load_dict(path)          

