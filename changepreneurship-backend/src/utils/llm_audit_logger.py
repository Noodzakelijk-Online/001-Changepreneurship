"""
LLM Audit Logger - tracks all LLM API calls for debugging and cost monitoring.
Stores prompts, responses, tokens, latency, and errors.
"""
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any


class LLMAuditLogger:
    """Logs all LLM interactions to file for audit and debugging."""
    
    def __init__(self, log_dir: Optional[str] = None):
        self.log_dir = log_dir or os.path.join(
            os.path.dirname(__file__), '..', '..', 'logs', 'llm'
        )
        os.makedirs(self.log_dir, exist_ok=True)
        self.enabled = os.getenv("LLM_AUDIT_LOGGING", "true").lower() == "true"
    
    def log_request(
        self,
        provider: str,
        model: str,
        prompt: str,
        system_message: Optional[str] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log an LLM request. Returns request_id for matching with response."""
        if not self.enabled:
            return request_id or datetime.utcnow().isoformat()
        
        req_id = request_id or datetime.utcnow().isoformat()
        log_entry = {
            "request_id": req_id,
            "timestamp": datetime.utcnow().isoformat(),
            "event": "request",
            "provider": provider,
            "model": model,
            "user_id": user_id,
            "options": options or {},
            "prompt_length": len(prompt),
            "prompt": prompt[:500] + ("..." if len(prompt) > 500 else ""),
            "system": system_message[:200] + ("..." if system_message and len(system_message) > 200 else "") if system_message else None,
        }
        self._write_log(log_entry)
        return req_id
    
    def log_response(
        self,
        request_id: str,
        response_text: Optional[str] = None,
        tokens_used: Optional[int] = None,
        latency_ms: Optional[float] = None,
        error: Optional[str] = None
    ):
        """Log an LLM response matching the request_id."""
        if not self.enabled:
            return
        
        log_entry = {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "event": "response",
            "response_length": len(response_text) if response_text else 0,
            "response": response_text[:500] + ("..." if response_text and len(response_text) > 500 else "") if response_text else None,
            "tokens_used": tokens_used,
            "latency_ms": latency_ms,
            "error": error,
            "success": error is None
        }
        self._write_log(log_entry)
    
    def _write_log(self, entry: Dict[str, Any]):
        """Write log entry to daily log file."""
        try:
            date_str = datetime.utcnow().strftime("%Y-%m-%d")
            log_file = os.path.join(self.log_dir, f"llm-audit-{date_str}.jsonl")
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception as e:
            # Don't fail requests due to logging issues
            print(f"[LLM Audit] Failed to write log: {e}")
    
    def get_daily_stats(self, date_str: Optional[str] = None) -> Dict[str, Any]:
        """Get aggregated stats for a specific day."""
        date_str = date_str or datetime.utcnow().strftime("%Y-%m-%d")
        log_file = os.path.join(self.log_dir, f"llm-audit-{date_str}.jsonl")
        
        if not os.path.exists(log_file):
            return {"date": date_str, "requests": 0, "errors": 0}
        
        stats = {
            "date": date_str,
            "requests": 0,
            "responses": 0,
            "errors": 0,
            "total_tokens": 0,
            "avg_latency_ms": 0,
            "providers": {}
        }
        
        latencies = []
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = json.loads(line)
                    
                    if entry.get("event") == "request":
                        stats["requests"] += 1
                        provider = entry.get("provider", "unknown")
                        stats["providers"][provider] = stats["providers"].get(provider, 0) + 1
                    
                    elif entry.get("event") == "response":
                        stats["responses"] += 1
                        if entry.get("error"):
                            stats["errors"] += 1
                        if entry.get("tokens_used"):
                            stats["total_tokens"] += entry["tokens_used"]
                        if entry.get("latency_ms"):
                            latencies.append(entry["latency_ms"])
            
            if latencies:
                stats["avg_latency_ms"] = sum(latencies) / len(latencies)
        
        except Exception as e:
            print(f"[LLM Audit] Failed to read stats: {e}")
        
        return stats
