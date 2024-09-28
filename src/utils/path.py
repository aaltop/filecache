from pathlib import Path

def path_depth(base_path:Path, child_path:Path):
    '''
    Find the depth of the path `child_path` under
    `base_path`. Assumes `child_path` is actually
    a child path.
    '''

    return list(child_path.parents).index(base_path)

def get_files(base_dir: Path, depth = 0) -> list[Path]:
    '''
    Recursively expand `base_dir` to get all the files up
    to `depth`. For any value of `depth` less than one,
    no recursion happens.
    '''

    files = []
    for dirpath, dirnames, filenames in base_dir.walk():

        cur_depth = 0 if dirpath == base_dir else path_depth(base_dir, dirpath) + 1
        if cur_depth > depth: continue 
        file_paths = [dirpath / filename for filename in filenames]
        if len(file_paths) > 0: files.extend(file_paths)

    return files

def expand_directories(paths:list[Path], depth = 0):
    '''
    Expand a list of file-likes to only contain actual files,
    effectively expanding the directories in the list, if any are present.
    '''

    path: Path
    flattened_paths = []
    for path in paths:
        if not path.is_dir():
            flattened_paths.append(path)
        else:
            flattened_paths.extend(get_files(path, depth = depth))

    return flattened_paths


def match_all(path:Path, patterns, case_sensitive = None):
    '''
    for matching multiple patterns against a path; see `PurePath.match()`.
    '''

    for pattern in patterns:
        if path.match(pattern, case_sensitive = case_sensitive):
            return True

    return False