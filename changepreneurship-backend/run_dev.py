"""Development runner for Changepreneurship backend.
Run with: python run_dev.py
Avoids FLASK_APP env issues on Windows PowerShell.
"""

from src.main import app  # noqa: E402

if __name__ == "__main__":
    # Enable debug reload for development convenience
    app.run(host="0.0.0.0", port=5000, debug=True)
