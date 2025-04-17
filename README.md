# Filecache

Utilities for caching various things on file. Currently main two
cachers are a [FunctionCacher](#functioncacher) similar to the python standard
library [functools.lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache),
and a file hashing utility [FileCacher](#filecacher) which can be used to hash files
in a directory nestedly.

[Examples](examples) might contain some examples of interest.

## FunctionCacher

FunctionCacher allows caching the invocations of functions, with subsequent
invocations being loaded from the in-memory cache. The cache can
also be saved to and loaded from file, allowing separate runs of a program
to reuse the calculated values. The main aim with this solution is
to save even more time over the likes of the cache utilities in the
standard library.

As a simple example: (copied from [examples](examples/dummy_function.py))

```python
function_cacher = FunctionCacher(
    save_path = Path() / "caches" / __name__ / "cache",
    cache_size = 3,
    auto_save = True
)

@function_cacher()
def dummy_function(value = 0):
    time.sleep(0.5)
    return f"You passed {value=}"
```

The save path -- where the cache is saved to -- is set, cache_size
sets a limit to how many different invocations of each function
can be saved, and auto_save saves the in-memory cache to file after
each invocation if the invocation is a never before seen one. The cacher
is then used to wrap the wanted function, and the function
can be called after this. Multiple functions can be wrapped with the
same cacher which will keep track of all their invocations.
By default, loading in a cache happens
automatically when a new instance is created and the passed save path
contains a viable cache. The cacher also allows setting a validity
period for the cached data, which allows getting rid of very old,
unused invocations more easily to limit how large the cache becomes.

Behind the scenes, FunctionCacher uses the [shelve module](https://docs.python.org/3/library/shelve.html)
to save and load the cached data. This allows working with a variety
of types without having to explicitly define (de)serialisation.
Values gotten from the cache are deepcopied such that the returned
value can be modified without modifying the value in the cache.

### Determining different invocations

In order for FunctionCacher to know when a new function is invoked,
it needs to know two things: the state of the function it is wrapping
and the passed-in arguments.

If a function's body changes (e.g. above,
dummy_function prints "executing" on its first line), the function's
operation might have changed and might now return something new.
To keep track of changes to the body, the body's state is hashed with the help of
[inspect](https://docs.python.org/3/library/inspect.html)
and [hashlib](https://docs.python.org/3/library/hashlib.html). The cached
invocations are matched to this hash.

When the passed in arguments change, the function may return something
new. Therefore, the inputs are also tracked, again using
[inspect](https://docs.python.org/3/library/inspect.html), and cached
along with the output from the function. While
shelve allows saving and loading a wide variety of Python data types,
the solution here requires also that the input types are comparable, which
is not always the case by default. One example is using [pandas](https://pandas.pydata.org/)
dataframes, which don't allow direct equality comparisons based on content
alone:

```python
>>> df = pd.DataFrame(dict(values = range(5)))
>>> bool(df == df)
ValueError: The truth value of a DataFrame is ambiguous. Use a.empty, a.bool(), a.item(), a.any() or a.all().
>>> df2 = df.copy()
>>> _dict = dict(df = df)
>>> _dict2 = dict(df = df2)
>>> _dict == _dict2
ValueError: The truth value of a DataFrame is ambiguous. Use a.empty, a.bool(), a.item(), a.any() or a.all()
```


To solve this issue, it is possible to pass comparison functions to
the wrapper. These functions are used to compare individual objects in the input
argument dictionary. An example (copied from [examples](examples/function_cacher.ipynb)):

```python
def compare_df(one, two):
    if all_instance_of(pd.DataFrame, one, two):

        if not (
            (len(one.index) == len(two.index))
            and (len(one.columns) == len(two.columns))
        ):
            return False
        
        return bool((one == two).all().all())

@function_cacher(compare_funcs = [compare_df])
def add_one(df: pd.DataFrame):
    time.sleep(1)
    called["add_one"] += 1
    return df + 1
```

`compare_df` obviously compares two dataframes, returning True
if they are the same (under the comparison). If the passed objects
are deemed uncomparable by the function (it returns None), the next
comparison function is called on the objects, or the basic equality
comparison is defaulted to if no comparison functions remain.

## FileCacher

Hashes the contents of files at given paths, allowing
caching the hashes in a JSON format. Useful for e.g. checking
if the contents of a data folder has changed and should be loaded
in again. Overall fairly simple and also less developed than FunctionCacher.
See [the example](examples/file_cacher.ipynb).