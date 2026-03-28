"""Rate limiter instance — import this in routes to apply limits."""
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["500 per day", "100 per hour"],
    storage_uri=os.getenv("REDIS_URL", "memory://"),
)
