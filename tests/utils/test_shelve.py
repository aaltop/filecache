from src.filecache.utils.shelve import save_dict, load_dict, clear_shelve


def test_save_and_load(tmp_path):
    """
    Dictionary can be saved to file and loaded up.
    """

    example_dict = {"Hello": "world", "list_of_tuples": [(1, 2, 3), (5, 6, 7)]}

    database_path = tmp_path / "database"
    save_dict(database_path, example_dict)

    loaded_dict = load_dict(database_path)

    assert example_dict == loaded_dict


def test_clear(tmp_path):
    """cache can be cleared"""

    example_dict = {"Hello": "world", "list_of_tuples": [(1, 2, 3), (5, 6, 7)]}

    database_path = tmp_path / "database"
    save_dict(database_path, example_dict)
    assert load_dict(database_path) == example_dict
    assert all(clear_shelve(database_path)["deleted_files"].values())
