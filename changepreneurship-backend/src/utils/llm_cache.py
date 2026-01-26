"""
LLM Response Cache - reduces API costs by caching responses keyed by prompt hash.
Uses Redis if available, falls back to in-memory dict.
"""
import os
import hashlib
import json
from typing import Optional, Dict, Any


class LLMCache:
    """Cache LLM responses to reduce API calls and costs."""
    
    def __init__(self):
        self.enabled = os.getenv("LLM_CACHE_ENABLED", "true").lower() == "true"
        self.ttl_seconds = int(os.getenv("LLM_CACHE_TTL_SECONDS", "86400"))  # 24h default
        self.redis_client = None
        self.memory_cache: Dict[str, Any] = {}
        
        # Try Redis first
        if self.enabled:
            try:
                from src.utils.redis_client import get_redis_client
                self.redis_client = get_redis_client()
                print("[LLM Cache] Using Redis backend")
            except Exception as e:
                print(f"[LLM Cache] Redis unavailable, using in-memory cache: {e}")
    
    def _generate_key(self, provider: str, model: str, prompt: str, system: Optional[str]) -> str:
        """Generate cache key from request parameters."""
        content = f"{provider}:{model}:{system or ''}:{prompt}"
        hash_obj = hashlib.sha256(content.encode('utf-8'))
        return f"llm:cache:{hash_obj.hexdigest()[:16]}"
    
    def get(self, provider: str, model: str, prompt: str, system: Optional[str] = None) -> Optional[str]:
        """Retrieve cached response if available."""
        if not self.enabled:
            return None
        
        key = self._generate_key(provider, model, prompt, system)
        
        try:
            if self.redis_client:
                cached = self.redis_client.get(key)
                if cached:
                    data = json.loads(cached)
                    print(f"[LLM Cache] HIT for key {key[:24]}...")
                    return data.get("response")
            else:
                cached = self.memory_cache.get(key)
                if cached:
                    print(f"[LLM Cache] HIT (memory) for key {key[:24]}...")
                    return cached.get("response")
        except Exception as e:
            print(f"[LLM Cache] Error retrieving: {e}")
        
        print(f"[LLM Cache] MISS for key {key[:24]}...")
        return None
    
    def set(
        self,
        provider: str,
        model: str,
        prompt: str,
        system: Optional[str],
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Store response in cache."""
        if not self.enabled or not response:
            return
        
        key = self._generate_key(provider, model, prompt, system)
        
        try:
            data = {
                "response": response,
                "provider": provider,
                "model": model,
                "metadata": metadata or {}
            }
            
            if self.redis_client:
                self.redis_client.setex(
                    key,
                    self.ttl_seconds,
                    json.dumps(data, ensure_ascii=False)
                )
                print(f"[LLM Cache] SET (Redis) key {key[:24]}... TTL={self.ttl_seconds}s")
            else:
                self.memory_cache[key] = data
                print(f"[LLM Cache] SET (memory) key {key[:24]}...")
        except Exception as e:
            print(f"[LLM Cache] Error storing: {e}")
    
    def invalidate(self, provider: str, model: str, prompt: str, system: Optional[str] = None):
        """Remove a specific cached response."""
        if not self.enabled:
            return
        
        key = self._generate_key(provider, model, prompt, system)
        
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                self.memory_cache.pop(key, None)
            print(f"[LLM Cache] Invalidated key {key[:24]}...")
        except Exception as e:
            print(f"[LLM Cache] Error invalidating: {e}")
    
    def clear_all(self):
        """Clear all cached LLM responses."""
        if not self.enabled:
            return
        
        try:
            if self.redis_client:
                # Delete all keys matching llm:cache:*
                pattern = "llm:cache:*"
                cursor = 0
                while True:
                    cursor, keys = self.redis_client.scan(cursor, match=pattern, count=100)
                    if keys:
                        self.redis_client.delete(*keys)
                    if cursor == 0:
                        break
                print("[LLM Cache] Cleared all Redis cache entries")
            else:
                self.memory_cache.clear()
                print("[LLM Cache] Cleared all memory cache entries")
        except Exception as e:
            print(f"[LLM Cache] Error clearing cache: {e}")
