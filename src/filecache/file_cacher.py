"""
Cacher that tracks the state of files by their hash digest.
"""

from pathlib import Path
import os
import hashlib

from .utils.path import expand_directories, match_all
from .json_cacher import JsonCacher
from .mixin.abstract_cache_comparison import AbstractCacheComparisonMixin
from .utils.compare import compare_dict_values
from .abstract_cacher import CacherState

type Cache = dict[Path, str]


class FileCacher(JsonCacher, AbstractCacheComparisonMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache: Cache

    def set_auto_save(self, val):
        return super().set_auto_save(val)

    def cache_to_state_cache(self):
        """
        Return the cache with the paths as absolute strings.
        """
        return {str(file.absolute()): digest for file, digest in self.cache.items()}

    @JsonCacher.auto_save_after()
    def hash_file(self, file: Path):
        """
        Add a hash of the contents of `file` to cache.
        """

        with open(file, "rb") as f:
            hash_object = hashlib.file_digest(f, self.hasher)

        self.cache[file] = hash_object.hexdigest()
        return self

    @JsonCacher.auto_save_after()
    def hash_files(
        self,
        paths: list[Path],
        match_patterns: list[os.PathLike] | None = None,
        depth=0,
    ):
        """
        Hash the files pointed to by the paths in `paths`. If a path
        is a folder, hash all the files in that folder (and subfolders
        up to depth `depth`). Only
        hash files which have a match in `match_patterns` (if None, accept all).
        """
        ...

        flattened_paths = expand_directories(paths, depth=depth)

        if not (match_patterns is None):
            flattened_paths = filter(
                lambda path: match_all(path, match_patterns), flattened_paths
            )

        # don't want to auto-save each time hash_file is invoked
        with self.temp_auto_save(False):
            for path in flattened_paths:
                self.hash_file(path)
        return self

    def state_cache_to_cache(self, state_cache: CacherState[dict], relative=True):
        """
        If `relative`,
        compute the file paths relative to current working directory.
        """

        def convert_path(path_str):

            path_obj = Path(path_str)
            if relative:
                path_obj = path_obj.relative_to(Path().absolute())

            return path_obj

        return {
            convert_path(file_path): digest for file_path, digest in state_cache.items()
        }

    def compare_caches(self, other: Cache) -> dict[Path, bool]:
        """
        Compares `self.cache` and `other`,
        Returning True for all keys in `self.cache` where either the
        key is not in `other` or the matching value is different.
        """
        return compare_dict_values(self.cache, other)
