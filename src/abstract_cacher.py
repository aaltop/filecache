import abc
import hashlib
from pathlib import Path
from typing import Self, Any, TypedDict, Callable

from src.utils.string import pascal_to_snake_case
from src.typing import Hasher

type CacheObject = Any
type StateCacheObject = Any

class CacherMetadata(TypedDict):

    hash_algorithm: str

class CacherState[T](TypedDict):

    metadata: CacherMetadata
    cache: T
    

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

    def metadata(self) -> CacherMetadata:
        '''
        Get metadata about this cacher.
        '''

        return {
            "hash_algorithm": self.hasher().name
        }
    
    @abc.abstractmethod
    def get_cache_for_state(self) -> StateCacheObject:
        '''
        Get the cache such that it is suitable for saving.
        '''
        return self.cache

    @abc.abstractmethod
    def cache_from_state_cache(self, state_cache: StateCacheObject, *args, **kwargs) -> CacheObject:
        '''
        Get the proper cache from the state cache.
        '''
        return state_cache
    
    def get_state(self) -> CacherState[StateCacheObject]:
        '''
        Get all data (the state) relevant to the cacher. State
        should be saveable as-is using `.save`. 
        '''

        return {
            "metadata": self.metadata(),
            "cache": self.get_cache_for_state()
        }
    
    @classmethod
    @abc.abstractmethod
    def new_cache(self) -> CacheObject:
        '''
        Return a new cache object.
        '''
    
    @abc.abstractmethod
    def save(self, path: Path | None = None) -> Self:
        '''
        Save the state.

        If `path` is None, defaults to self.save_path.
        '''
    
    @abc.abstractmethod
    def load(self, path: Path | None = None) -> CacherState[StateCacheObject]:
        '''
        Load the state as saved by `save()`.

        If `path` is None, defaults to self.save_path.
        '''

    def load_cache(self, path: Path | None = None, inplace = False, *args, **kwargs):
        '''
        Load the cache.

        Arguments:
            path:
                Passed to `.load`.
            inplace:
                Whether to return cache or set it in the Cacher.
            args:
                Passed to `.cache_from_state_cache`.
            kwargs:
                Passed to `.cache_from_state_cache`.
        '''
        state = self.load(path)
        cache = self.cache_from_state_cache(state["cache"], *args, **kwargs)
        if inplace:
            self.cache = cache
            return self
        else:
            return cache