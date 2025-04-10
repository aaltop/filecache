import pytest

from src.file_cacher import FileCacher
from src.utils.path import write_dict_files

@pytest.fixture
def test_folder_text():

    return {
        "folder1": {
            "file1.txt": "stuff here",
            "file2.txt": "this is file 2\nwith two lines"
        },
        "file1.txt": "Top-level file content"
    }


def test_hashing(tmp_path, test_folder_text):

    content_folder = tmp_path / "content"
    write_dict_files(content_folder, test_folder_text)
    file_cacher = FileCacher(save_path = tmp_path / "cache")
    file_cacher.hash_files([content_folder])

    assert len(file_cacher.cache) == 1
    for file_name in file_cacher.cache:
        assert file_name.stem in ["file1"]

    first_key, first_hash = list(file_cacher.cache.items())[0]
    file_cacher.hash_files([content_folder], depth = 1)
    # should still have the previous value all the same
    assert file_cacher.cache[first_key] == first_hash

    assert len(file_cacher.cache) == 3
    for file_name in file_cacher.cache:
        assert file_name.stem in ["file1", "file2"]
