import os
import sys
from pathlib import Path
import time

root_path = os.path.abspath(os.path.join(os.getcwd(), '..'))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from src.function_cacher import FunctionCacher

function_cacher = FunctionCacher(
    save_path = Path() / "caches" / __name__ / "cache",
    cache_size = 3,
    auto_save = True
)

@function_cacher()
def dummy_function(value = 0):
    time.sleep(0.5)
    return f"You passed {value=}"