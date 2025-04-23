import datetime as dt

class InvalidationDict[K, V](dict):
    '''
    Allows keeping track of when each of its keys were last accessed, allowing
    data to be removed based on a set validity period.

    To update, use the (get | set)_and_update methods: normal keyed
    access does not update access time.
    '''


    def __init__(self, valid_for = dt.timedelta.max):

        self._valid_for = None
        self.valid_for = valid_for
        self._last_accessed: dict[str, dt.datetime] = {}

    @property
    def valid_for(self):
        return self._valid_for
    
    @staticmethod
    def _validate_valid_period(val):
        if not isinstance(val, dt.timedelta):
            raise TypeError("valid period should be a timedelta")
        if not dt.timedelta() <= val:
            raise ValueError("valid period should be positive")

    @valid_for.setter
    def valid_for(self, val):
        self._validate_valid_period(val)
        self._valid_for = val

    def invalidate(self, key: K):
        '''
        Perform invalidation at `self.key`.
        '''
        del self[key]
        return self

    def invalidate_old_data(self, valid_for: dt.timedelta | None = None):
        '''
        Arguments:
            valid_for:
                If None, defaults to using `self.valid_for`.

        Raises:
            ValueError:
                `valid_for` is negative.
        '''

        now = dt.datetime.now(dt.timezone.utc)
        valid_for = self.valid_for if valid_for is None else valid_for
        self._validate_valid_period(valid_for)

        last_accessed = self._last_accessed.copy()
        for key, value in last_accessed.items():
            if valid_for < now - value:
                self.invalidate(key)



    def _update_access_time(self, key: K):

        # in order for this class to be loadable from a pickle
        # file, this is necessary
        # most likely because __setitem__ is called during deserialisation
        # to set the data,
        # at which point _last_accessed has not been initialised yet.
        if not hasattr(self, "_last_accessed"):
            self._last_accessed = {}
        self._last_accessed[key] = dt.datetime.now(dt.timezone.utc)

    def set_and_update(self, key, value):
        '''
        Sets `value` at `key` and updates the access time.
        '''
        self[key] = value
        self._update_access_time(key)
        return self
    
    def get_and_update(self, key: K) -> V:
        '''
        Gets the value at `key` and updates the access time.
        '''
        value = self[key]
        self._update_access_time(key)
        return value
    
    def __delitem__(self, key):
        super().__delitem__(key)
        if key in self._last_accessed:
            del self._last_accessed[key]