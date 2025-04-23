import pytest
from pathlib import Path

from src.filecache.file_cacher import FileCacher
from src.filecache.utils.path import write_dict_files
from src.filecache.exceptions import StateNotFoundError

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
    '''Hashing files works'''

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
    '''Comparing caches works'''

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

    file_cacher_newer.save()
    assert not any(file_cacher_newer.compare_caches(file_cacher_newer.load_cache(relative = False)).values())

def test_save_and_load(tmp_path, test_folder_text):
    '''Saving and loading works'''

    content_folder = tmp_path / "content"
    write_dict_files(content_folder, test_folder_text)
    cache_path = tmp_path / "cache"
    file_cacher = FileCacher(save_path = cache_path)

    file_cacher.hash_files([content_folder], depth = 1)
    assert len(file_cacher.cache) == 3
    file_cacher.save()
    assert file_cacher.cache == file_cacher.load_cache(relative = False)

def test_clear_cache(tmp_path, test_folder_text):
    '''Clearing cache works'''

    content_folder = tmp_path / "content"
    write_dict_files(content_folder, test_folder_text)
    cache_path = tmp_path / "cache"
    file_cacher = FileCacher(save_path = cache_path)

    file_cacher.hash_files([content_folder], depth = 1)
    assert len(file_cacher.cache) == 3
    file_cacher.save()
    assert file_cacher.cache == file_cacher.load_cache(relative = False)

    file_cacher.clear()
    assert len(file_cacher.cache) == 0
    with pytest.raises(StateNotFoundError):
        file_cacher.load_cache(relative = False)


class TestAutoSave:

    def test_auto_save_init_attribute(self, tmp_path, test_folder_text):
        '''
        Cacher can be set to automatically save after each invocation
        when initialising
        '''

        content_folder = tmp_path / "content"
        write_dict_files(content_folder, test_folder_text)
        cache_path = tmp_path / "cache"
        file_cacher = FileCacher(save_path = cache_path)
        file_cacher.hash_files([content_folder])
        with pytest.raises(StateNotFoundError):
            file_cacher.load_cache(relative = False)
        
        file_cacher = FileCacher(save_path = cache_path, auto_save = True)
        file_cacher.hash_files([content_folder], depth = 1)
        assert len(file_cacher.load_cache(relative = False)) == 3


    def test_auto_save_property(self, tmp_path, test_folder_text):
        '''
        Cacher can be set to automatically save after each invocation
        through a property
        '''

        content_folder = tmp_path / "content"
        write_dict_files(content_folder, test_folder_text)
        cache_path = tmp_path / "cache"
        file_cacher = FileCacher(save_path = cache_path)
        file_cacher.hash_files([content_folder])
        with pytest.raises(StateNotFoundError):
            file_cacher.load_cache(relative = False)
        
        file_cacher.auto_save = True
        file_cacher.hash_files([content_folder], depth = 1)
        print(file_cacher.load_cache(relative = False))
        assert len(file_cacher.load_cache(relative = False)) == 3

    def test_save_all_and_invidiual(self, tmp_path: Path, test_folder_text):
        '''
        Cacher saves on both the individual hash function and vectorised
        one.
        '''

        content_folder = tmp_path / "content"
        write_dict_files(content_folder, test_folder_text)
        cache_path = tmp_path / "cache"
        file_cacher = FileCacher(save_path = cache_path, auto_save = True)
        for fso in content_folder.iterdir():
            if fso.is_file():
                file_cacher.hash_file(fso)
                break
        assert len(file_cacher.load_cache(relative = False)) == 1
        
        file_cacher.hash_files([content_folder], depth = 1)
        assert len(file_cacher.load_cache(relative = False)) == 3

def test_auto_load(tmp_path, test_folder_text, monkeypatch):
    '''
    Auto-loading cache works
    '''

    def init_load(self: FileCacher):
        try:
            # need to do relative again
            self.load_cache(inplace = True, relative = False)
        except StateNotFoundError:
            pass

    monkeypatch.setattr(FileCacher, "init_load", init_load)

    content_folder = tmp_path / "content"
    write_dict_files(content_folder, test_folder_text)
    cache_path = tmp_path / "cache"
    file_cacher = FileCacher(save_path = cache_path)
    file_cacher.hash_files([content_folder], depth = 1)

    assert len(file_cacher.cache) == 3
    new_file_cacher = FileCacher(save_path = cache_path)
    # nothing auto-loaded as not saved yet
    with pytest.raises(StateNotFoundError):
        new_file_cacher.load_cache(relative = False)

    # save allows auto-loading to succeed
    file_cacher.save()
    new_file_cacher = FileCacher(save_path = cache_path)
    assert len(new_file_cacher.cache) == 3