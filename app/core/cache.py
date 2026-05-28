import hashlib
from functools import lru_cache
from typing import Dict, Any

# A local in-memory storage tray to house the actual agent payloads
_GLOBAL_CACHE_TRAY: Dict[str, Any] = {}

@lru_cache(maxsize=256)
def _lookup_lru_engine(cache_key: str, cache_version_signal: int) -> Any:
    """
    The core LRU engine. By tracking a numeric 'version signal', we can 
    force the function to re-evaluate whenever a new value gets written,
    bypassing stale cache reads safely without wiping out other valid keys.
    """
    return _GLOBAL_CACHE_TRAY.get(cache_key)


def generate_cache_key(endpoint_prefix: str, *args, **kwargs) -> str:
    """
    Creates a deterministic MD5 hash string based on input values.
    Guarantees that identical complaints and sectors produce identical keys.
    """
    serialized_inputs = f"{args}_{sorted(kwargs.items())}".lower().strip()
    hash_object = hashlib.md5(serialized_inputs.encode("utf-8"))
    return f"{endpoint_prefix}:{hash_object.hexdigest()}"


class AutoCareCacheService:
    """
    Pragmatic interface to handle ultra-fast caching across the AutoCare ecosystem.
    """
    # Track writes globally to update our LRU function signature on changes
    _write_counter = 0

    @classmethod
    def get(cls, cache_key: str) -> Any:
        """Looks up a request key in the high-speed memory tray."""
        # Check through the LRU function wrapper
        return _lookup_lru_engine(cache_key, cls._write_counter)

    @classmethod
    def set(cls, cache_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Saves an agent computation back into the memory tray."""
        # 1. Update the raw tracking directory
        _GLOBAL_CACHE_TRAY[cache_key] = data
        
        # 2. Increment version counter to notify the LRU engine of state changes
        cls._write_counter += 1
        
        # 3. Prime the cache by running an immediate lookup tracking event
        _lookup_lru_engine(cache_key, cls._write_counter)
        return data

    @classmethod
    def inspect_diagnostics(cls) -> dict:
        """Helper to print cache efficiency stats in your terminal logs."""
        engine_stats = _lookup_lru_engine.cache_info()
        return {
            "hits": engine_stats.hits,
            "misses": engine_stats.misses,
            "current_lru_tracked_size": engine_stats.currsize,
            "total_raw_stored_items": len(_GLOBAL_CACHE_TRAY),
            "max_capacity": engine_stats.maxsize
        }