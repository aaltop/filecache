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
    '''Test that hashing files works'''

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


def test_comparison(tmp_path, test_folder_text):
    '''Test that comparing caches works'''

    content_folder = tmp_path / "content"
    write_dict_files(content_folder, test_folder_text)
    cache_path = tmp_path / "cache"
    file_cacher = FileCacher(save_path = cache_path)

    # take just the top file(s)
    file_cacher.hash_files([content_folder])

    file_cacher_newer = FileCacher(save_path = cache_path)
    # hash further down
    file_cacher_newer.hash_files([content_folder], depth = 1)

    # test that newer cacher has deeper values that are not matched
    # -------------------------------------------------------------
    is_different = file_cacher_newer.compare_caches(file_cacher.cache)
    assert len(is_different) == 3
    top_path = list(file_cacher.cache)[0]
    # top path file the same
    assert not is_different[top_path]
    del is_different[top_path]
    # all others not
    assert all(is_different.values())
    # =============================================================