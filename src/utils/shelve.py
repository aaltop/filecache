import shelve
from pathlib import Path


def save_dict(save_path: Path, _dict: dict) -> None:
    '''
    Save `_dict` as shelve database data at `save_path`.
    '''

    with shelve.open(save_path) as db:

        db.update(_dict)


def load_dict(save_path: Path) -> dict:
    '''
    Load the shelve data from `save_path`.
    '''

    _dict = {}

    with shelve.open(save_path) as db:

        _dict.update(db)

    return _dict

def clear_shelve(save_path: Path) -> dict[Path, bool]:
    '''
    Remove the shelve data at `save_path`.

    Returns:
        Dictionary of whether a specific path was found for deletion.
    '''

    file_suffixes = ("bak", "dat", "dir")
    file_prefix = save_path.stem

    suffixes_deleted = {}
    for suffix in file_suffixes:
        file_path = save_path.parent / f"{file_prefix}.{suffix}"
        try:
            file_path.unlink(missing_ok = False)
        except FileNotFoundError:
            suffixes_deleted[file_path] = False
            continue
        suffixes_deleted[file_path] = True