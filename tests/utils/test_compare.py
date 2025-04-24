import pytest

from filecache.utils.compare import compare_dict_values, all_instance_of


def test_simple_compare():
    """Dictionaries can be compared simply"""

    dict1 = dict(hello="there", alist=[1, 2, 3], booli=False)

    dict2 = dict1 | dict(booli=True)

    assert not any(compare_dict_values(dict1, dict1).values())
    comp = compare_dict_values(dict1, dict2)
    assert sum(comp.values()) == 1
    assert comp["booli"]


def test_recursive_compare():

    dict1 = dict(hello="there", alist=[1, 3, 3], inner_dict=dict(i_am="a dictionary"))
    dict2 = dict1 | dict(inner_dict=dict(i_am="something else"))

    assert not any(compare_dict_values(dict1, dict1).values())
    comp = compare_dict_values(dict1, dict2)
    assert sum(comp.values()) == 1
    assert comp["inner_dict"]


def test_comparison_funcs():

    class Dummy:

        def __init__(self, value):
            self.value = value

        def __eq__(self, other):
            raise NotImplementedError

    def compare_dummy(dum1, dum2):
        if all_instance_of(Dummy, dum1, dum2):
            return dum1.value == dum2.value

    dict1 = dict(hello="there", alist=[1, 3, 3], dummy=Dummy(value=0))
    dict2 = dict1 | dict(dummy=Dummy(value=1))

    with pytest.raises(NotImplementedError):
        assert not any(compare_dict_values(dict1, dict1).values())
    assert not any(compare_dict_values(dict1, dict1, [compare_dummy]).values())
    comp = compare_dict_values(dict1, dict2, [compare_dummy])
    assert sum(comp.values()) == 1
    assert comp["dummy"]
