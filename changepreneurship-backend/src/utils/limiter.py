"""Rate limiter instance — import this in routes to apply limits."""
import os
from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def _get_rate_limit_key():
    """
    Use Bearer session token as the rate-limit key for authenticated requests.
    Falls back to IP for unauthenticated requests.
    This prevents all Docker/proxy users sharing the same IP bucket.
    """
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        token = auth[7:].strip()
        if token:
            return f"token:{token}"
    return get_remote_address()


limiter = Limiter(
    key_func=_get_rate_limit_key,
    default_limits=["2000 per day", "500 per hour"],
    storage_uri=os.getenv("REDIS_URL", "memory://"),
)
