"""Thread-safe TTL memory cache with simple cleanup."""
import time, threading
class MemoryCache:
    def __init__(self, max_items=2000, default_ttl=600):
        self._max = max_items
        self._ttl = default_ttl
        self._store = {}
        self._lock = threading.Lock()
    def set(self, key, value, ttl=None):
        expire = time.time() + (ttl if ttl is not None else self._ttl)
        with self._lock:
            if len(self._store) >= self._max:
                # evict oldest
                oldest = min(self._store.items(), key=lambda kv: kv[1][0])[0]
                del self._store[oldest]
            self._store[key] = (expire, value)
        def clear_cache(self):
            cache_dir = os.path.join(os.path.dirname(__file__), '__pycache__')
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir)
            # 可扩展更多缓存目录
    def get(self, key, default=None):
        with self._lock:
            v = self._store.get(key)
            if not v: return default
            if v[0] < time.time():
                del self._store[key]; return default
            return v[1]
    def delete(self,key):
        with self._lock:
            if key in self._store: del self._store[key]
    def clear(self):
        with self._lock: self._store.clear()
    def cleanup(self):
        now = time.time()
        with self._lock:
            to_del = [k for k,(exp,_) in self._store.items() if exp < now]
            for k in to_del: del self._store[k]

if __name__ == "__main__":
    print("MemoryCache 仅作为模块使用，不建议直接运行。")
