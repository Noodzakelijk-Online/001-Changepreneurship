import os
import time
from typing import Optional, Dict, Any
from src.utils.llm_audit_logger import LLMAuditLogger
from src.utils.llm_cache import LLMCache


class LLMClient:
    """
    Thin abstraction over multiple LLM providers. Keeps one public method: generate(prompt, system, options).
    Providers supported via env: LLM_PROVIDER=openai|azure-openai|anthropic|ollama|mock
    """

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai").strip()
        self.model = os.getenv("LLM_MODEL", "gpt-4.1-mini").strip()
        self.timeout = int(os.getenv("LLM_TIMEOUT_SECONDS", "60"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1200"))
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        
        # Use mock client if key is 'mock-' prefixed or provider is 'mock'
        if self.provider == "mock" or (self.api_key and self.api_key.startswith("mock-")):
            self.provider = "mock"
        
        # Initialize audit logger and cache
        self.audit_logger = LLMAuditLogger()
        self.cache = LLMCache()

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        # Check cache first
        cached_response = self.cache.get(self.provider, self.model, prompt, system)
        if cached_response:
            return cached_response
        
        # Log request
        request_id = self.audit_logger.log_request(
            provider=self.provider,
            model=self.model,
            prompt=prompt,
            system_message=system,
            options=options or {}
        )
        
        start_time = time.time()
        error = None
        response = ""
        
        try:
            provider = self.provider
            if provider == "mock":
                response = self._generate_mock(prompt, system, options)
            elif provider == "openai":
                response = self._generate_openai(prompt, system, options)
            elif provider == "azure-openai":
                response = self._generate_azure_openai(prompt, system, options)
            elif provider == "anthropic":
                response = self._generate_anthropic(prompt, system, options)
            elif provider == "ollama":
                response = self._generate_ollama(prompt, system, options)
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
            
            # Cache the successful response
            self.cache.set(
                provider=self.provider,
                model=self.model,
                prompt=prompt,
                system=system,
                response=response,
                metadata={"request_id": request_id}
            )
            
            return response
            
        except Exception as e:
            error = str(e)
            raise
        finally:
            # Always log response (success or failure)
            latency_ms = int((time.time() - start_time) * 1000)
            self.audit_logger.log_response(
                request_id=request_id,
                response_text=response,
                latency_ms=latency_ms,
                error=error
            )
    
    def _generate_mock(self, prompt: str, system: Optional[str], options: Optional[Dict[str, Any]]) -> str:
        """Use mock client for testing without real API calls."""
        from .mock_llm_client import MockLLMClient
        mock = MockLLMClient()
        return mock.generate(prompt, system, options)

    # Provider implementations are minimal and import lazily to avoid hard deps
    def _generate_openai(self, prompt: str, system: Optional[str], options: Optional[Dict[str, Any]]) -> str:
        try:
            from openai import OpenAI
        except Exception:
            raise RuntimeError("OpenAI client not installed. Add 'openai' to requirements.txt.")
        client = OpenAI(api_key=self.api_key or None)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        temperature = (options or {}).get("temperature", self.temperature)
        max_tokens = (options or {}).get("max_tokens", self.max_tokens)
        start = time.time()
        resp = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if time.time() - start > self.timeout:
            raise TimeoutError("LLM request exceeded timeout")
        return (resp.choices[0].message.content or "").strip()

    def _generate_azure_openai(self, prompt: str, system: Optional[str], options: Optional[Dict[str, Any]]) -> str:
        try:
            from openai import AzureOpenAI
        except Exception:
            raise RuntimeError("Azure OpenAI client not installed. Add 'openai' to requirements.txt.")
        if not self.azure_endpoint or not self.azure_api_key:
            raise RuntimeError("Missing Azure OpenAI env: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY")
        client = AzureOpenAI(api_key=self.azure_api_key, azure_endpoint=self.azure_endpoint)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        temperature = (options or {}).get("temperature", self.temperature)
        max_tokens = (options or {}).get("max_tokens", self.max_tokens)
        resp = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return (resp.choices[0].message.content or "").strip()

    def _generate_anthropic(self, prompt: str, system: Optional[str], options: Optional[Dict[str, Any]]) -> str:
        try:
            import anthropic
        except Exception:
            raise RuntimeError("Anthropic client not installed. Add 'anthropic' to requirements.txt.")
        client = anthropic.Anthropic(api_key=self.api_key or None)
        temperature = (options or {}).get("temperature", self.temperature)
        max_tokens = (options or {}).get("max_tokens", self.max_tokens)
        sys_msg = system or ""
        resp = client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=sys_msg,
            messages=[{"role": "user", "content": prompt}],
        )
        # Anthropic returns content as a list of blocks
        parts = resp.content or []
        text = "\n".join([p.text for p in parts if hasattr(p, "text")])
        return text.strip()

    def _generate_ollama(self, prompt: str, system: Optional[str], options: Optional[Dict[str, Any]]) -> str:
        import json
        import urllib.request

        payload = {
            "model": self.model,
            "prompt": (system + "\n\n" if system else "") + prompt,
            "options": {
                "temperature": (options or {}).get("temperature", self.temperature),
            },
            "stream": False,
        }
        req = urllib.request.Request(
            url="http://localhost:11434/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return (data.get("response") or "").strip()
