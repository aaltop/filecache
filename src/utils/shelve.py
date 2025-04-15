import shelve
from pathlib import Path
import dbm
from typing import TypedDict


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

class DeletedDatabase(TypedDict):
    '''
    Properties:
        deleted_files:
            Whether a given path was deleted successfully.
    '''
    database_type: str | None
    deleted_files: dict[Path, bool]

def clear_shelve(save_path: Path) -> DeletedDatabase:
    '''
    Remove the shelve data at `save_path`.
    '''

    db_type = dbm.whichdb(save_path)
    deletion_info: DeletedDatabase = {"database_type": db_type, "deleted_files": {}}
    # TODO: figure out the other dbms' file extension cases
    # see open methods? (e.g. https://docs.python.org/3/library/dbm.html#dbm.ndbm.open
    # talks of .dir and .pag, though dbm.dumb's one doesn't mention .bak)
    match db_type:
        case "dbm.sqlite3":
            try:
                save_path.unlink(missing_ok = False)
                deletion_info["deleted_files"][save_path] = True
            except FileNotFoundError:
                deletion_info["deleted_files"][save_path] = False

        case "dbm.dumb":
            file_suffixes = ("bak", "dat", "dir")
            file_prefix = save_path.stem

            suffixes_deleted = {}
            for suffix in file_suffixes:
                file_path = save_path.parent / f"{file_prefix}.{suffix}"
                try:
                    file_path.unlink(missing_ok = False)
                    suffixes_deleted[file_path] = True
                except FileNotFoundError:
                    suffixes_deleted[file_path] = False

            deletion_info["deleted_files"] = suffixes_deleted

    return deletion_info