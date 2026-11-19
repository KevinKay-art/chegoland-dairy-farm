import os
os.environ["DATABASE_URL"] = "sqlite:///./test_dairy.db"
os.environ["MPESA_MOCK_MODE"] = "true"
os.environ["TESTING"] = "true"

import weakref
import sys
print("Python version:", sys.version)

class TestLoader:
    pass

loader = TestLoader()
wr = weakref.ref(loader)
print("weakref:", wr)
print("weakref hash:", hash(wr))

# Test tuple with weakref
key = (wr, "admin/dashboard.html")
print("key:", key)
print("key hash:", hash(key))

# Test dict with tuple key
d = {}
d[key] = "template"
print("dict[key] works:", d[key])

# Test LRUCache
from jinja2.utils import LRUCache
cache = LRUCache(10)
cache[key] = "template"
print("LRUCache[key] works:", cache[key])
print("LRUCache.get(key):", cache.get(key))

# Now test with actual FileSystemLoader
from jinja2 import FileSystemLoader
fs_loader = FileSystemLoader("app/templates")
wr2 = weakref.ref(fs_loader)
print("\nFS loader weakref:", wr2)
print("FS loader weakref hash:", hash(wr2))

key2 = (wr2, "admin/dashboard.html")
print("key2 hash:", hash(key2))

cache2 = LRUCache(10)
cache2[key2] = "template2"
print("LRUCache2[key2] works:", cache2[key2])
print("LRUCache2.get(key2):", cache2.get(key2))
