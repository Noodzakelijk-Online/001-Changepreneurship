import os
import json
import redis

_redis_client = None

def get_redis():
    global _redis_client
    if _redis_client is None:
        url = os.environ.get("REDIS_URL")
        if not url:
            return None
        try:
            _redis_client = redis.Redis.from_url(url, decode_responses=True)
            # simple ping test
            _redis_client.ping()
        except Exception:
            _redis_client = None
    return _redis_client

def cache_session(token: str, user_id: int, ttl_seconds: int = 60 * 60 * 24 * 30):
    client = get_redis()
    if not client:
        return False
    try:
        client.set(f"session:{token}", user_id, ex=ttl_seconds)
        return True
    except Exception:
        return False

def get_session_user(token: str):
    client = get_redis()
    if not client:
        return None
    try:
        val = client.get(f"session:{token}")
        if val is None:
            return None
        return int(val)
    except Exception:
        return None

# -------------------- Generic JSON/object caching helpers --------------------

def cache_json(key: str, data, ttl_seconds: int = 60 * 5) -> bool:
    """Cache arbitrary JSON-serialisable data under a namespaced key.

    Args:
        key: cache key WITHOUT namespace prefix (we add 'json:').
        data: python object serialisable by json.dumps
        ttl_seconds: expiration (default 5 minutes)
    Returns: True if cached, False otherwise
    """
    client = get_redis()
    if not client:
        return False
    try:
        payload = json.dumps(data, ensure_ascii=False)
        client.set(f"json:{key}", payload, ex=ttl_seconds)
        return True
    except Exception:
        return False

def get_cached_json(key: str):
    """Retrieve cached JSON object (or None)."""
    client = get_redis()
    if not client:
        return None
    try:
        raw = client.get(f"json:{key}")
        if raw is None:
            return None
        return json.loads(raw)
    except Exception:
        return None