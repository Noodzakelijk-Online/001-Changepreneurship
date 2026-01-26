"""Comprehensive LLM Consensus Integration Tests."""
import sys
import os

# Fix Windows encoding
if os.name == 'nt':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, 'src')

from main import app
import json

class LLMTestRunner:
    """Test LLM consensus system."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
    
    def test(self, name, func):
        """Run test."""
        try:
            func()
            self.passed += 1
            print(f"✓ {name}")
        except AssertionError as e:
            self.failed += 1
            print(f"✗ {name}: {e}")
        except Exception as e:
            self.failed += 1
            print(f"✗ {name}: ERROR - {e}")
    
    def summary(self):
        """Print summary."""
        print(f"\n{'='*70}")
        print(f"PASSED: {self.passed} | FAILED: {self.failed}")
        if self.passed + self.failed > 0:
            print(f"SUCCESS RATE: {self.passed / (self.passed + self.failed) * 100:.1f}%")
        print(f"{'='*70}\n")

def run_llm_tests():
    """Run LLM consensus tests."""
    tester = LLMTestRunner()
    
    with app.app_context():
        print("\n🤖 LLM CONSENSUS INTEGRATION TESTS\n")
        
        # ========== MOCK LLM CLIENT ==========
        print("📋 MOCK LLM CLIENT TESTS")
        
        def test_mock_llm_import():
            from services.mock_llm_client import MockLLMClient
            client = MockLLMClient()
            assert client is not None, "Mock client should initialize"
            assert client.model == "mock-gpt-4o-mini", "Should have mock model name"
        tester.test("MockLLMClient initialization", test_mock_llm_import)
        
        def test_mock_llm_generation():
            from services.mock_llm_client import MockLLMClient
            client = MockLLMClient()
            
            response = client.generate("Test prompt about business readiness")
            assert response is not None, "Should return response"
            assert len(response) > 0, "Response should not be empty"
            assert isinstance(response, str), "Response should be string"
        tester.test("MockLLMClient generate response", test_mock_llm_generation)
        
        def test_mock_llm_variations():
            from services.mock_llm_client import MockLLMClient
            client = MockLLMClient()
            
            # Different calls should return different responses (simulating model variations)
            resp1 = client.generate("executive summary prompt")
            resp2 = client.generate("executive summary prompt")
            
            # Responses might differ due to variant logic
            assert resp1 is not None and resp2 is not None, "Both should return responses"
        tester.test("MockLLMClient response variations", test_mock_llm_variations)
        
        # ========== REAL LLM CLIENT ==========
        print("\n🔌 LLM CLIENT TESTS")
        
        def test_llm_client_initialization():
            from services.llm_client import LLMClient
            
            # Should work with mock API key
            client = LLMClient(api_key="mock-test-key")
            assert client is not None, "Client should initialize"
            assert client.provider == "openai", "Default provider should be openai"
        tester.test("LLMClient initialization with mock key", test_llm_client_initialization)
        
        def test_llm_client_mock_mode():
            from services.llm_client import LLMClient
            
            client = LLMClient(api_key="mock-key-test")
            # Should auto-switch to mock mode
            response = client.generate("Test prompt")
            assert response is not None, "Mock mode should return response"
        tester.test("LLMClient auto-switches to mock mode", test_llm_client_mock_mode)
        
        # ========== LLM CONSENSUS ==========
        print("\n🗳️  LLM CONSENSUS TESTS")
        
        def test_consensus_initialization():
            from services.llm_consensus import LLMConsensus
            
            configs = [
                {"provider": "openai", "model": "gpt-4o-mini"},
                {"provider": "openai", "model": "gpt-4o-mini"},
            ]
            
            consensus = LLMConsensus(configs=configs)
            assert consensus is not None, "Consensus should initialize"
            assert len(consensus.configs) == 2, "Should have 2 model configs"
        tester.test("LLMConsensus initialization", test_consensus_initialization)
        
        def test_consensus_majority():
            from services.llm_consensus import LLMConsensus
            import os
            
            # Set mock API key for testing
            os.environ['OPENAI_API_KEY'] = 'mock-key-test-consensus'
            
            configs = [
                {"provider": "openai", "model": "gpt-4o-mini"},
                {"provider": "openai", "model": "gpt-4o-mini"},
            ]
            
            consensus = LLMConsensus(configs=configs)
            result = consensus.run(
                prompt="Generate executive summary for a tech startup",
                system="You are a business analyst"
            )
            
            assert result is not None, "Consensus should return result"
            assert len(result) > 0, "Result should not be empty"
        tester.test("LLMConsensus majority finding", test_consensus_majority)
        
        def test_consensus_with_single_model():
            from services.llm_consensus import LLMConsensus
            import os
            
            os.environ['OPENAI_API_KEY'] = 'mock-key-test-consensus'
            
            # Single model - consensus should still work
            configs = [{"provider": "openai", "model": "gpt-4o-mini"}]
            
            consensus = LLMConsensus(configs=configs)
            result = consensus.run(prompt="Test prompt")
            
            assert result is not None, "Single model consensus should work"
        tester.test("LLMConsensus with single model", test_consensus_with_single_model)
        
        # ========== LLM CACHE ==========
        print("\n💾 LLM CACHE TESTS")
        
        def test_cache_initialization():
            from utils.llm_cache import LLMCache
            
            cache = LLMCache()
            assert cache is not None, "Cache should initialize"
        tester.test("LLMCache initialization", test_cache_initialization)
        
        def test_cache_set_get():
            from utils.llm_cache import LLMCache
            
            cache = LLMCache()
            
            cache.set("test_prompt", "test_response")
            result = cache.get("test_prompt")
            
            assert result == "test_response", "Cache should return stored value"
        tester.test("LLMCache set and get", test_cache_set_get)
        
        def test_cache_miss():
            from utils.llm_cache import LLMCache
            
            cache = LLMCache()
            
            result = cache.get("nonexistent_prompt_12345")
            assert result is None, "Cache miss should return None"
        tester.test("LLMCache miss returns None", test_cache_miss)
        
        # ========== LLM AUDIT LOGGER ==========
        print("\n📝 LLM AUDIT LOGGER TESTS")
        
        def test_audit_logger_initialization():
            from utils.llm_audit_logger import LLMAuditLogger
            
            logger = LLMAuditLogger()
            assert logger is not None, "Audit logger should initialize"
        tester.test("LLMAuditLogger initialization", test_audit_logger_initialization)
        
        def test_audit_logging():
            from utils.llm_audit_logger import LLMAuditLogger
            import tempfile
            import os
            
            # Use temp file for testing
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl')
            temp_file.close()
            
            logger = LLMAuditLogger(log_file=temp_file.name)
            
            logger.log(
                provider="openai",
                model="gpt-4o-mini",
                prompt="Test prompt",
                response="Test response",
                duration_ms=150.5
            )
            
            # Read back
            with open(temp_file.name, 'r') as f:
                lines = f.readlines()
                assert len(lines) >= 1, "Should have at least one log entry"
                
                entry = json.loads(lines[-1])
                assert entry['provider'] == "openai", "Should log provider"
                assert entry['model'] == "gpt-4o-mini", "Should log model"
            
            os.unlink(temp_file.name)
        tester.test("LLMAuditLogger logging to file", test_audit_logging)
        
        # ========== INTEGRATION ==========
        print("\n🔗 INTEGRATION TESTS")
        
        def test_end_to_end_consensus():
            from services.llm_consensus import LLMConsensus
            import os
            
            os.environ['OPENAI_API_KEY'] = 'mock-key-test-consensus'
            os.environ['USE_LLM'] = 'true'
            os.environ['LLM_CONSENSUS'] = 'true'
            
            configs = [
                {"provider": "openai", "model": "gpt-4o-mini"},
                {"provider": "openai", "model": "gpt-4o-mini"},
            ]
            
            consensus = LLMConsensus(configs=configs)
            result = consensus.run(
                prompt="Analyze business readiness for a SaaS startup with 100 users and $5K MRR",
                system="You are a business consultant"
            )
            
            assert result is not None, "Should complete end-to-end"
            assert len(result) > 50, "Should return substantial response"
        tester.test("End-to-end LLM consensus flow", test_end_to_end_consensus)
    
    tester.summary()
    return tester.passed, tester.failed

if __name__ == '__main__':
    passed, failed = run_llm_tests()
    sys.exit(0 if failed == 0 else 1)
