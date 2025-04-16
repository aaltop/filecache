import pandas as pd
import pytest

from pathlib import Path
import string
from collections import deque

from src.function_cacher import FunctionCacher
from src.exceptions import StateNotFoundError
from src.utils.compare import all_instance_of

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

    letters = string.ascii_lowercase
    df = pd.DataFrame(dict(
        idx = range(len(letters)),
        letters = iter(letters)
    ))

    def compare_df(one, two):
        if all_instance_of(pd.DataFrame, one, two):

            if not (len(one.index) == len(two.index)):
                return False
            
            if not (len(one.columns) == len(two.columns)):
                return False

            # numpy bool...
            return bool((one == two).all().all())

    called = 0

    @function_cache(compare_funcs = [compare_df])
    def dummy_function(df):
        nonlocal called
        called += 1
        return df
    
    # test first that it looks okay normally
    return_value = dummy_function(df)
    assert called == 1
    deq = list(function_cache.cache.values())[0]
    value = deq[0]
    assert value["input"] == dict(df = df)
    assert compare_df(value["output"], return_value)

    # test save and load
    function_cache.save()
    function_cache.load_cache(inplace = True)
    deq = list(function_cache.cache.values())[0]
    value = deq[0]
    assert compare_df(value["input"]["df"], df)
    assert compare_df(value["output"], return_value)
    dummy_function(df)
    assert called == 1
    
    df2 = df.copy()
    df2["capital"] = df["letters"].str.capitalize()
    dummy_function(df = df2)
    assert called == 2
    dummy_function(df = df2)
    assert called == 2
    

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
    # passing in new argument changes value
    assert 2 == mutate(dummy_val = 1)
    assert mutated == 2
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

def test_cache_size_after_load(tmp_path: Path):
    '''
    Cache size after loading is not automatically set to current
    cache size.
    '''

    cache_path = tmp_path / "cache"
    cache_path.mkdir()

    function_cache = FunctionCacher(save_path = cache_path, cache_size = 5)

    @function_cache()
    def dummy_function(dummy_val):
        return dummy_val + 1
    
    for i in range(5): dummy_function(i)
    function_cache.save()
    function_cache.cache_size = 3
    function_cache.load_cache(inplace=True)
    # inplace overwrites the cacher's cache size to keep consistency
    assert function_cache.cache_size == 5
    assert function_cache.cache.max_size == 5
    assert len(next(iter(function_cache.cache.values()))) == 5
    function_cache.cache_size = 3
    function_cache.load_cache(inplace = True, overwrite_loaded_cache_attributes = True)
    assert len(next(iter(function_cache.cache.values()))) == 3
    assert function_cache.cache.max_size == 3


def test_lookup_function_cache(tmp_path):
    ''' 
    Function's cached data can be looked up.
    '''

    cache_path = tmp_path / "cache"
    cache_path.mkdir()

    function_cache = FunctionCacher(save_path = cache_path)

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
    assert len(next(iter(function_cache.cache.values()))) == 5
    function_cache.save()
    assert len(next(iter(function_cache.load_cache().values()))) == 5
    function_cache.clear()
    assert len(next(iter(function_cache.cache.values()))) == 0
    with pytest.raises(StateNotFoundError):
        cac = function_cache.load_cache()

def test_returns_copy(tmp_path):
    '''
    Output from cached function can be modified without the contents
    of the cache changing.
    '''
    
    cache_path = tmp_path / "cache"
    cache_path.mkdir()

    function_cache = FunctionCacher(save_path = cache_path)

    @function_cache()
    def dummy_function():
        return { "value": 0 }
    
    dicti = dummy_function()
    dicti["value"] = 1
    assert dummy_function()["value"] == 0
    dummy_function()["value"] += 1
    assert dummy_function()["value"] == 0

def test_invocation_sets_cache_timestamp(tmp_path):
    '''Invoking a wrapped function sets the timestamp in the cache'''

    cache_path = tmp_path / "cache"
    cache_path.mkdir()

    function_cache = FunctionCacher(save_path = cache_path)

    @function_cache()
    def dummy_function():
        return { "value": 0 }
    
    assert len(function_cache.cache._last_accessed) == 0
    dummy_function()
    assert len(function_cache.cache._last_accessed) == 1

class TestAutoSave:

    def test_auto_save_init_attribute(self, tmp_path):
        '''
        Cacher can be set to automatically save after each invocation
        when initialising
        '''

        cache_path = tmp_path / "cache"
        cache_path.mkdir()

        function_cache = FunctionCacher(save_path = cache_path, auto_save = True)

        @function_cache()
        def dummy_function():
            return { "value": 0 }
        
        with pytest.raises(StateNotFoundError):
            function_cache.load_cache(inplace=False)

        dummy_function()

        assert len(function_cache.load_cache(inplace=False)) == 1

    def test_auto_save_property(self, tmp_path):
        '''
        Cacher can be set to automatically save after each invocation
        through a property
        '''

        cache_path = tmp_path / "cache"
        cache_path.mkdir()

        # auto save should default to False
        function_cache = FunctionCacher(save_path = cache_path)

        @function_cache()
        def dummy_function(value = 0):
            return { "value": value }
        
        with pytest.raises(StateNotFoundError):
            function_cache.load_cache(inplace=False)

        dummy_function()

        # not saved yet
        with pytest.raises(StateNotFoundError):
            function_cache.load_cache(inplace=False)

        function_cache.auto_save = True
        # When value is gotten from cache, auto-save is not performed 
        dummy_function()
        with pytest.raises(StateNotFoundError):
            function_cache.load_cache(inplace=False)

        # creating new value should cause cache to be saved
        dummy_function(value = 1)
        assert len(next(iter(function_cache.load_cache(inplace=False).values()))) == 2

def test_auto_load(tmp_path):
    '''
    Auto-loading cache works
    '''

    cache_path = tmp_path / "cache"
    cache_path.mkdir()

    # auto-load should default to True
    function_cache = FunctionCacher(save_path = cache_path, auto_load = False)

    @function_cache()
    def dummy_function(value = 0):
        return { "value": value }
    
    dummy_function()
    assert len(next(iter(function_cache.cache.values()))) == 1

    new_function_cacher = FunctionCacher(save_path = cache_path)
    assert len(new_function_cacher.cache) == 0

    function_cache.save()
    new_function_cacher = FunctionCacher(save_path = cache_path)
    assert len(next(iter(new_function_cacher.cache.values()))) == 1