from .utils.path import expand_directories, match_all

from pathlib import Path
import os
import hashlib
import typing
import json

class FileCache:


    def __init__(self, hasher = lambda: hashlib.sha256(usedforsecurity=False), save_path = None):
        '''
        `hasher` is expected to be a hashlib-type hasher factory.

        `save_path` is the path to save the cache to, by default 
        "./file_cache/cache.json"
        '''

        self.hasher = hasher
        self.cache = {}
        self.save_path = (
            Path() / "file_cache" / "cache.json"
            if save_path is None 
            else save_path
        )

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
        Save the state as a json file.
        '''

        path = self.save_path if path is None else path
        json_kwargs = {} if json_kwargs is None else json_kwargs

        path.parents[0].mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.get_state(), f, **json_kwargs)

        return self

    def load(self, path:Path = None, relative = True):
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
        
        self.cache = {
            convert_path(file_path): digest
            for file_path, digest in saved_cache["hashes"].items()
        }

        return self
        
