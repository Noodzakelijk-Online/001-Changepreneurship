#!/usr/bin/env python
"""Check database and cache configuration"""
from src.main import app
from src.models.assessment import db
from src.utils.redis_client import get_redis_client
from src.utils.llm_cache import LLMCache
import os

print("="*70)
print("DATABASE & CACHE CONFIGURATION")
print("="*70)

with app.app_context():
    # Database info
    print("\n📊 DATABASE:")
    print(f"  Engine: {db.engine.url}")
    print(f"  Backend: {db.engine.url.get_backend_name()}")
    print(f"  DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT SET')}")
    print(f"  DATABASE_URL_LOCAL: {os.getenv('DATABASE_URL_LOCAL', 'NOT SET')}")
    
    # Check tables
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"  Tables: {len(tables)} - {', '.join(tables[:5])}")
    
    # Redis cache
    print("\n🔴 REDIS CACHE:")
    redis_url = os.getenv('REDIS_URL')
    print(f"  REDIS_URL: {redis_url or 'NOT SET'}")
    
    redis_client = get_redis_client()
    if redis_client:
        try:
            redis_client.ping()
            print(f"  Status: ✅ CONNECTED")
            info = redis_client.info('server')
            print(f"  Version: {info.get('redis_version', 'unknown')}")
        except Exception as e:
            print(f"  Status: ❌ ERROR - {e}")
    else:
        print(f"  Status: ⚠️  NOT CONFIGURED (using fallback)")
    
    # LLM Cache
    print("\n🧠 LLM CACHE:")
    cache = LLMCache()
    print(f"  Enabled: {cache.enabled}")
    print(f"  TTL: {cache.ttl_seconds}s ({cache.ttl_seconds/3600:.1f}h)")
    print(f"  Backend: {'Redis' if cache.redis_client else 'In-Memory Dict'}")
    
    # Session cache
    print("\n🔐 SESSION CACHE:")
    print(f"  Backend: {'Redis (if available)' if redis_client else 'Database only'}")
    print(f"  Fallback: Database (always available)")

print("\n" + "="*70)
