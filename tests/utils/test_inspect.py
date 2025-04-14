from hashlib import sha256
import inspect as base_inspect

from src.utils import inspect



def test_function_hash():


    def dummy_function():

        return "Hello, dummy"

    hasher = sha256(usedforsecurity = False)

    hexdigest = inspect.function_hash(dummy_function, hasher = hasher)

    function_body = '    def dummy_function():\n\n        return "Hello, dummy"\n'
    
    other_hasher = sha256(usedforsecurity = False)
    other_hasher.update(bytes(function_body, encoding = "utf-8"))

    assert hexdigest == other_hasher.hexdigest()


def test_bind_arguments():


    def dummy_function(string_value, other_string_value = "Hello"):

        return string_value

    string_value = "goodbye"
    other_string_value = "some"

    bound_args = inspect.bind_arguments(
        dummy_function,
        [string_value],
        { "other_string_value": other_string_value }
    )

    assert "string_value" in bound_args
    assert "other_string_value" in bound_args

    assert bound_args["string_value"] == string_value
    assert bound_args["other_string_value"] == other_string_value

def test_bind_ignore():
    '''Some kwargs can be ignored'''

    def dummy_function(string_value, other_string_value, ignored_kw_argument):
        return string_value

    string_value = "goodbye"
    other_string_value = "some"

    bound_args = inspect.bind_arguments(
        dummy_function,
        [string_value],
        { "other_string_value": other_string_value, "ignored_kw_argument": "not here"},
        ignore_in_kwargs = ("ignored_kw_argument", )
    )

    assert "string_value" in bound_args
    assert "other_string_value" in bound_args
    assert not ("ignored_kw_argument" in bound_args)
    assert len(bound_args) == 2

    assert bound_args["string_value"] == string_value
    assert bound_args["other_string_value"] == other_string_value