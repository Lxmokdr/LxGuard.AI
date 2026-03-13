import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'Expert_Agent'))
from data.cache_manager import cache

if cache.flush_all():
    print("Redis cache successfully flushed!")
else:
    print("Failed to flush redis cache.")
