from .utils.path import expand_directories, match_all

from pathlib import Path
import os
import hashlib
import typing
import json

class FileCache:


    def __init__(self, hasher = lambda: hashlib.sha256(usedforsecurity=False)):
        '''
        `hasher` is expected to be a hashlib-type hasher factory.
        '''

        self.hasher = hasher
        self.cache = {}

    def str_cache(self):
        '''
        Return the cache with the paths as absolute strings.
        '''
        return {str(file.absolute()): digest for file, digest in self.cache.items()}

    def hash_file(self, file: os.PathLike):

        with open(file, "rb") as f:
            hash_object = hashlib.file_digest(f, self.hasher)

        return {
            "file": file,
            "digest": hash_object.hexdigest(),
            "hash_object": hash_object
        }
    
    def hash_files(
            self,
            paths:list[os.PathLike],
            match_patterns: list[str] | list[Path] = None,
            depth = 0) -> typing.Generator[dict[str, Path | str], None, None]:
        '''
        Hash the files pointed to by the paths in `paths`. If a path
        is a folder, hash all the files in that folder (and subfolders
        up to depth `depth`). Only
        hash files which have a match in `match_patterns` (if None, accept all).

        Returns a generator yielding 
        \{
            "file": pathlib.Path,
            "digest": str
        }
        for each file.
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
            file, digest, _ = self.hash_file(path).values()
            self.cache[file] = digest
            yield {
                "file": file,
                "digest": digest
            }

    def info(self):
        '''
        Get information about the file cacher.
        '''

        return {
            "hash_algorithm": self.hasher().name
        }
    
    def get_state(self):

        return {
            "info": self.info(),
            "hashes": self.str_cache()
        }
    
    def save(self, path:Path = None, json_kwargs: dict = None):
        '''
        Save the state as a json file, by default in "./file_cache/cache.json".
        '''

        path = Path() / "file_cache" / "cache.json" if path is None else path
        json_kwargs = {} if json_kwargs is None else json_kwargs

        path.parents[0].mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.get_state(), f, **json_kwargs)
