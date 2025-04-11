import pandas as pd
import pytest

from pathlib import Path
import string
from collections import deque

from src.function_cacher import FunctionCacher
from src.exceptions import StateNotFoundError

# NOTE: tmp_path is a pytest thing
def test_wrapped_function(tmp_path: Path):
    '''
    The wrapped function works.
    '''

    cache_path = tmp_path / "cache"
    cache_path.mkdir()

    function_cache = FunctionCacher(save_path = cache_path)

    @function_cache()
    def dummy_function(string_value):

        return string_value
    
    string_value = "this is a string value"
    returned_value = dummy_function(string_value = string_value)

    assert returned_value == string_value

def test_caching_simple(tmp_path: Path):
    '''
    Test caching with basic Python data type.
    '''

    cache_path = tmp_path / "cache"
    cache_path.mkdir()

    function_cache = FunctionCacher(save_path = cache_path)

    @function_cache()
    def dummy_function(string_value, list_of_ints = [1, 2, 3]):
    
        return string_value
    
    string_value = "this is a string_value"
    return_value = dummy_function(string_value)
    
    # test normally
    deq = list(function_cache.cache.values())[0]
    value = deq[0]
    assert value["input"] == {
        "string_value": string_value,
        "list_of_ints": [1,2,3]
    }
    assert value["output"] == return_value

    # test save and load
    function_cache.save()
    function_cache.load_cache(inplace = True)

    deq = list(function_cache.cache.values())[0]
    value = deq[0]
    assert value["input"] == {
        "string_value": string_value,
        "list_of_ints": [1,2,3]
    }
    assert value["output"] == return_value

def test_caching_complex(tmp_path: Path):
    '''
    Test caching with a more complex value.
    '''

    cache_path = tmp_path / "cache"
    cache_path.mkdir()

    function_cache = FunctionCacher(save_path = cache_path)

    @function_cache()
    def dummy_function(capital = False):
    
        letters = string.ascii_uppercase if capital else string.ascii_lowercase
        return pd.DataFrame(dict(
            idx = range(len(letters)),
            letters = letters
        ))
    
    # test first that it looks okay normally
    return_value = dummy_function()
    deq = list(function_cache.cache.values())[0]
    value = deq[0]
    assert value["input"] == dict(capital = False)
    assert (value["output"] == return_value).all().all()

    # test save and load
    function_cache.save()
    function_cache.load_cache(inplace = True)
    deq = list(function_cache.cache.values())[0]
    value = deq[0]
    assert value["input"] == dict(capital = False)
    assert (value["output"] == return_value).all().all()
    

def test_is_cached(tmp_path: Path):
    '''
    The return value is actually cached, i.e. that
    the function is not unnecessarily invoked again.
    '''

    cache_path = tmp_path / "cache"
    cache_path.mkdir()

    function_cache = FunctionCacher(save_path = cache_path)

    mutated = 0

    @function_cache()
    def mutate(dummy_val = 0):

        nonlocal mutated
        mutated += 1
        return mutated

    assert 1 == mutate()
    assert mutated == 1
    # second call uses cached value, no mutation
    assert 1 == mutate()
    assert mutated == 1
    print(function_cache.cache)
    # passing in new argument changes value
    assert 2 == mutate(dummy_val = 1)
    assert mutated == 2
    print(function_cache.cache)
    # again, cached value when calling with original argument
    assert 1 == mutate()
    assert mutated == 2

def test_cache_size(tmp_path: Path):
    '''
    Setting cache size works for new items.
    '''

    cache_path = tmp_path / "cache"
    cache_path.mkdir()

    function_cache = FunctionCacher(save_path = cache_path)

    @function_cache()
    def dummy_function(dummy_val):

        return dummy_val + 1
    
    function_cache.cache_size = 3
    for i in range(5): dummy_function(i)
    assert len(next(iter(function_cache.cache.values()))) == 3

def test_cache_size_dynamic(tmp_path: Path):
    '''
    Setting cache size works dynamically.
    '''

    cache_path = tmp_path / "cache"
    cache_path.mkdir()

    function_cache = FunctionCacher(save_path = cache_path)

    @function_cache()
    def dummy_function(dummy_val):

        return dummy_val + 1
    
    for i in range(5): dummy_function(i)
    assert len(next(iter(function_cache.cache.values()))) == 5
    function_cache.cache_size = 3
    assert len(next(iter(function_cache.cache.values()))) == 3


def test_lookup_function_cache():
    '''
    Function's cached data can be looked up.
    '''

    function_cache = FunctionCacher()

    @function_cache()
    def dummy_function(dummy_val):
        return dummy_val + 1
    
    cached_data = function_cache.get_cached_data(dummy_function)
    assert isinstance(cached_data, deque)
    assert len(cached_data) == 0
    dummy_function(0)
    cached_data = function_cache.get_cached_data(dummy_function)
    assert len(cached_data) == 1
    assert "input" in cached_data[0]
    assert "output" in cached_data[0]

def test_clear_cache(tmp_path):
    
    cache_path = tmp_path / "cache"
    cache_path.mkdir()

    function_cache = FunctionCacher(save_path = cache_path)

    @function_cache()
    def dummy_function(dummy_val):

        return dummy_val + 1
    
    for i in range(5): dummy_function(i)
    print(function_cache.cache)
    assert len(next(iter(function_cache.cache.values()))) == 5
    function_cache.save()
    assert len(next(iter(function_cache.load_cache().values()))) == 5
    function_cache.clear(where = "both")
    assert len(next(iter(function_cache.cache.values()))) == 0
    with pytest.raises(StateNotFoundError):
        function_cache.load_cache()