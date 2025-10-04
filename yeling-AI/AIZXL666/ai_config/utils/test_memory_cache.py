import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from memory_cache import MemoryCache

import pytest

def test_set_and_get():
    cache = MemoryCache(max_items=2, default_ttl=2)
    cache.set('a', 123)
    assert cache.get('a') == 123
    cache.set('b', 456)
    cache.set('c', 789)
    # 'a' 应被淘汰
    assert cache.get('a') is None
    assert cache.get('b') == 456
    assert cache.get('c') == 789

def test_ttl_expiry():
    cache = MemoryCache(max_items=2, default_ttl=1)
    cache.set('x', 'y')
    import time; time.sleep(1.2)
    assert cache.get('x') is None
