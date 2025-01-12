from pathlib import Path

from src.function_cache import FunctionCache

# NOTE: tmp_path is a pytest thing
def test_wrapped_function(tmp_path: Path):
    '''
    Test that the wrapped function works.
    '''

    cache_path = tmp_path / "cache"
    cache_path.mkdir()

    function_cache = FunctionCache(save_path = cache_path)

    @function_cache()
    def dummy_function(string_value):

        return string_value
    
    string_value = "this is a string value"
    returned_value = dummy_function(string_value = string_value)

    assert returned_value == string_value


# TODO: might be nice to have
# a way to lookup what the function points to directly in the cache,
# though the end user would ultimately not care about the cacher at all,
# really.
def test_caching(tmp_path: Path):

    cache_path = tmp_path / "cache"
    cache_path.mkdir()

    function_cache = FunctionCache(save_path = cache_path)

    @function_cache()
    def dummy_function(string_value, list_of_ints = [1, 2, 3]):
    
        return string_value
    
    string_value = "this is a string_value"
    return_value = dummy_function(string_value)
    
    _, value = list(function_cache.cache.items())[0]

    assert value["input"] == {
        "string_value": string_value,
        "list_of_ints": [1,2,3]
    }
    assert value["output"] == return_value


