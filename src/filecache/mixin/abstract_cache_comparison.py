'''
Mixin intended for classes that implement AbstractCacher.
'''

import abc
from typing import Any

from src.filecache.abstract_cacher import CacheObject

class AbstractCacheComparisonMixin(abc.ABC):

    @classmethod
    @abc.abstractmethod
    def compare_caches(self, other: CacheObject) -> Any:
        '''
        Compare the values in `self.cache` and in `other`.
        '''