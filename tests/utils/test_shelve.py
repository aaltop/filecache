from src.utils.shelve import save_dict, load_dict



def test_save_and_load(tmp_path):
    '''
    Dictionary can be saved to file and loaded up.
    '''

    example_dict = {
        "Hello": "world",
        "list_of_tuples": [(1,2,3), (5,6,7)]
    }

    database_path = tmp_path / "database"
    save_dict(database_path, example_dict)
    
    loaded_dict = load_dict(database_path)

    assert example_dict == loaded_dict