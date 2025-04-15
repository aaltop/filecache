import pytest

import datetime as dt
import time

from src.invalidation_dict import InvalidationDict


def test_invalidation_time():
    '''
    It is possible to set an invalidation period which also has a default
    value
    '''

    assert InvalidationDict().valid_for == dt.timedelta.max
    dc = InvalidationDict(valid_for = dt.timedelta(days = 1))
    assert dc.valid_for == dt.timedelta(days = 1)
    # 
    dc.valid_for = dt.timedelta(days = 2)
    assert dc.valid_for == dt.timedelta(days = 2)

def test_only_positive_times():
    '''property setter accepts only positive times'''
    dc = InvalidationDict()
    with pytest.raises(ValueError):
        dc.valid_for = dt.timedelta(days = -1)

def test_invalidate_old_data():
    '''It is possible to invalidate old data'''

    dc = InvalidationDict()

    dummy_key = "dummy_key"
    dc.set_and_update(dummy_key, "dummy_value")
    dummy_key2 = "some"
    dc.set_and_update(dummy_key2, "value")

    dc.invalidate_old_data()
    assert len(dc) == 2
    assert len(dc._last_accessed) == 2

    # fake the access time
    dc._last_accessed[dummy_key] = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days = 1)
    dc.invalidate_old_data(valid_for = dt.timedelta(minutes = 1))
    # other value should still be good (as long as a minute doesn't
    # somehow pass)
    assert len(dc) == 1
    assert len(dc._last_accessed) == 1

def test_normal_access():
    '''Normal keyed access does not refresh access time'''

    dc = InvalidationDict()

    dummy_key = "dummy_key"
    dc[dummy_key] = "dummy data"
    old_last_accessed = dc._last_accessed.copy()

    time.sleep(0.2)
    dc[dummy_key]
    assert old_last_accessed == dc._last_accessed