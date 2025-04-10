from pathlib import Path
import os

def path_depth(base_path: Path, child_path: Path):
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

def expand_directories(paths: list[Path], depth = 0):
    '''
    Expand a list of paths (up to `depth`) to only contain actual file paths,
    effectively expanding the directories in the list if any are present.
    '''

    flattened_paths = []
    for path in paths:
        if not path.is_dir():
            flattened_paths.append(path)
        else:
            flattened_paths.extend(get_files(path, depth = depth))

    return flattened_paths


def match_all(path: Path, patterns: list[os.PathLike], case_sensitive = None):
    '''
    for matching multiple patterns against a path. If any of the
    patterns in `patterns` match, returns True, otherwise returns False;
    see `PurePath.match()`.
    '''

    for pattern in patterns:
        if path.match(pattern, case_sensitive = case_sensitive):
            return True

    return False

type FolderStructure = dict[str, FolderStructure | str | bytes]
def write_dict_files(base_path: Path, folder_structure: FolderStructure):
    '''
    Write the contents specified by `folder_structure` to `path`.

    Arguments:
        path:
        folder_structure:
            If a key points to
                - dict: key is folder name, FolderStructure is
                - string: key is file name, string is written to file
                - bytes: key is file name, bytes are written to file
    '''

    base_path.mkdir(exist_ok = True)
    for fso_name, fso_content in folder_structure.items():
        if isinstance(fso_content, dict):
            write_dict_files(base_path / fso_name, fso_content)
        elif isinstance(fso_content, str):
            with open(base_path / fso_name, "w") as f:
                f.write(fso_content)
        elif isinstance(fso_content, bytes):
            with open(base_path / fso_name, "wb") as f:
                f.write(fso_content)
        else:
            raise TypeError("Keys should point to either dicts, strings or bytes")