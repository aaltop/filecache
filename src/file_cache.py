from .utils.path import expand_directories, match_all

from pathlib import Path
import os
import hashlib

class FileCache:


    def __init__(self, hasher = None):

        self.hasher = (
            lambda: hashlib.sha256(usedforsecurity=False)
            if (hasher is None)
            else hasher
        )

    def hash_file(self, file: os.PathLike):

        with open(file, "rb") as f:
            hash_object = hashlib.file_digest(f, self.hasher)

        return {
            "file": file,
            "digest": hash_object.digest(),
            "hash_object": hash_object
        }
    
    def hash_files(self, paths:list[os.PathLike], match_patterns: list[str] | list[Path] = None, depth = 0):
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
            file, digest, _ = self.hash_file(path).values()
            yield {
                "file": file,
                "digest": digest
            }
