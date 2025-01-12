from hashlib import sha256
import inspect as base_inspect

from src.utils import inspect



def test_function_hash():


    def dummy_function():

        return "Hello, dummy"

    hasher = sha256(usedforsecurity = False)

    hexdigest = inspect.function_hash(hasher, dummy_function)

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