import abc
import hashlib
from pathlib import Path
from typing import Self, Any, TypedDict, Callable

from src.utils.string import pascal_to_snake_case
from src.typing import Hasher

type CacheObject = Any

class MetadataDict(TypedDict):

    hash_algorithm: str

class StateDict(TypedDict):

    metadata: MetadataDict
    cache: CacheObject
    

class AbstractCacher(abc.ABC):

    name_as_snake = None

    @classmethod
    def _calculate_name(cls):

        cls.name_as_snake = pascal_to_snake_case(cls.__name__)

    def __init__(self, save_path: Path = None, *, hasher: Callable[[], Hasher] = lambda: hashlib.sha256(usedforsecurity=False)):
        '''

        Arguments:
            save_path:
                The path to save the cache to, by default 
                "./{class_name}/cache", where {class_name} is the name
                of the class in snake case. (Assumes that the class name is
                Pascal case.)
            hasher:
                Factory returning a hashlib-type hasher.

        '''

        if self.name_as_snake is None:
            self._calculate_name()

        self.hasher = hasher
        self.cache = self.new_cache()
        self.save_path = (
            Path() / self.name_as_snake / "cache"
            if save_path is None 
            else save_path
        )
        self.save_path.parents[0].mkdir(parents=True, exist_ok=True)

    def metadata(self) -> MetadataDict:
        '''
        Get metadata about this cacher.
        '''

        return {
            "hash_algorithm": self.hasher().name
        }
    
    def get_state(self) -> StateDict:
        '''
        Get all data relevant to the cacher.
        '''

        return {
            "metadata": self.metadata(),
            "cache": self.cache
        }
    
    @classmethod
    @abc.abstractmethod
    def new_cache(self) -> CacheObject:
        '''
        Return a new cache object.
        '''
    
    @abc.abstractmethod
    def save(self, path: Path = None) -> Self:
        '''
        Save the state.

        If `path` is None, defaults to self.save_path.
        '''
    
    @abc.abstractmethod
    def load(self, path: Path = None) -> CacheObject:
        '''
        Load the state as saved by `save()`.

        If `path` is None, defaults to self.save_path.
        '''