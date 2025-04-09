'''
Cacher that tracks the state of files by their hash digest.
'''


from pathlib import Path
import os
import hashlib
from typing import (
    Self
)
import json

from .utils.path import expand_directories, match_all
from .json_cacher import JsonCacher

class FileCache(JsonCacher):

    def json_cache(self):
        '''
        Return the cache with the paths as absolute strings.
        '''
        return {str(file.absolute()): digest for file, digest in self.cache.items()}

    def hash_file(self, file: os.PathLike):

        with open(file, "rb") as f:
            hash_object = hashlib.file_digest(f, self.hasher)

        digest = hash_object.hexdigest()
        self.cache[file] = digest

        return {
            "file": file,
            "digest": digest,
            "hash_object": hash_object
        }
    
    def hash_files(
            self,
            paths: list[os.PathLike],
            match_patterns: list[str] | list[Path] = None,
            depth = 0) -> Self:
        '''
        Hash the files pointed to by the paths in `paths`. If a path
        is a folder, hash all the files in that folder (and subfolders
        up to depth `depth`). Only
        hash files which have a match in `match_patterns` (if None, accept all).
        '''
        ...

        flattened_paths = expand_directories(paths, depth = depth)


        if not (match_patterns is None):
            flattened_paths = filter(
                lambda path: match_all(path, match_patterns),
                flattened_paths
            )

        path: Path
        for path in flattened_paths:
            self.hash_file(path).values()

        return self

    def load(self, path: Path = None, relative = True) -> dict:
        '''
        Load the state as saved by `save()`. If `relative`,
        compute the file paths relative to current working directory.
        '''

        path = self.save_path if path is None else path


        with open(path) as f:
            saved_cache = json.load(f)

        def convert_path(path_str):

            path_obj = Path(path_str)
            if relative:
                path_obj = path_obj.relative_to(Path().absolute())
            
            return path_obj
        
        return {
            convert_path(file_path): digest
            for file_path, digest in saved_cache["cache"].items()
        }
