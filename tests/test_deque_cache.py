import pytest

from collections import deque

from src.deque_cache import DequeCache




def test_deque_added_automatically():
    '''Deque is automatically added when using key'''

    deq = DequeCache()

    assert len(deq._cache) == 0
    deq["dummy_key"]
    assert len(deq._cache) == 1
    assert isinstance(deq["dummy_key"], deque)

@pytest.mark.parametrize(
        "set_to, expected",
        [
            (None, None),
            (0, None),
            (-1, None),
            (5, 5),
            (10000, 10000)
        ]
)
def test_max_size_can_be_set(set_to, expected):
    '''Test that the max size can be set properly.'''

    deq = DequeCache()

    assert deq.max_size is None
    deq.max_size = set_to
    assert deq.max_size == expected

def test_dynamic_max_size():
    '''Max length of deques is automatically adjusted when max size is set.'''

    deq = DequeCache()

    # put some stuff in first
    dummy_values = list(range(10))
    deq["dummy_key"].extendleft(dummy_values)
    print(deq)
    assert dummy_values == list(reversed(deq["dummy_key"]))

    # max size dynamically changes existing values
    deq.max_size = 3
    print(deq)
    assert dummy_values[:-(deq.max_size + 1):-1] == list(deq["dummy_key"])

    # new deques are also limited by max size set
    dummy_values2 = list(range(10, 20))
    deq["dummy_key2"].extendleft(dummy_values2)
    print(deq)
    assert dummy_values2[:-(deq.max_size + 1):-1] == list(deq["dummy_key2"])

def test_find_cached_simple():
    '''Whether finding cached object works with default values.'''

    deq = DequeCache()

    deq["dummy_key"].extendleft([1,2,3])
    assert list(deq["dummy_key"]) == [3,2,1]
    assert 2 == deq.find_cached_item("dummy_key", 2)
    # moves found object to front
    assert list(deq["dummy_key"]) == [2,3,1]

    with pytest.raises(LookupError):
        deq.find_cached_item("dummy_key", 4)

def test_find_cached_complex():
    '''Whether finding cached object works with non-default values'''

    deq = DequeCache()

    with deq.no_moving_recent_to_front():

        deq["dummy_key"].extendleft([1,2,3])
        assert deq.find_cached_item(
            "dummy_key",
            2.5,
            lambda one,two: two < one
        ) == 2
        assert deq.find_cached_item("dummy_key", 1) == 1
        
        with pytest.raises(LookupError):
            deq.find_cached_item("dummy_key", 2.5)
        # same as the above comparison, set as instance default
        deq.compare_deque_objects = lambda one,two: two < one
        assert deq.find_cached_item("dummy_key", 2.5) == 2

        # no value less than 1
        with pytest.raises(LookupError):
            deq.find_cached_item("dummy_key", 1)
        # passed function overwrites instance default
        assert deq.find_cached_item(
            "dummy_key",
            1,
            lambda one, two: one == two
        ) == 1

