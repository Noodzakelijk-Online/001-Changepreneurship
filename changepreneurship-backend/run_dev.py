"""Development runner for Changepreneurship backend"""
import os

try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(env_path)
except ImportError:
    print("[run_dev] python-dotenv not installed, using existing environment")

# Use local SQLite if DATABASE_URL_LOCAL is set
if os.getenv("DATABASE_URL_LOCAL"):
    os.environ["DATABASE_URL"] = os.getenv("DATABASE_URL_LOCAL")
    print("[run_dev] Using local SQLite database")

print(f"[run_dev] USE_LLM={os.getenv('USE_LLM')}, LLM_CONSENSUS={os.getenv('LLM_CONSENSUS')}")

from src.main import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
