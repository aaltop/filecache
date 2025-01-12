import shelve


def save_dict(save_path: str, _dict: dict) -> None:
    '''
    Save `_dict` as shelve database data at `save_path`.
    '''

    with shelve.open(save_path) as db:

        db.update(_dict)


def load_dict(save_path) -> dict:
    '''
    Load the shelve data from `save_path`.
    '''

    _dict = {}

    with shelve.open(save_path) as db:

        _dict.update(db)

    return _dict