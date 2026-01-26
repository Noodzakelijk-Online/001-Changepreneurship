"""Production server runner using Waitress (Windows-compatible)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from waitress import serve
from main import app

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    threads = int(os.getenv('WAITRESS_THREADS', 8))
    
    print(f"[Production] Starting Waitress WSGI server")
    print(f"[Production] Host: {host}:{port}")
    print(f"[Production] Threads: {threads}")
    print(f"[Production] Environment: {os.getenv('FLASK_ENV', 'production')}")
    
    serve(
        app,
        host=host,
        port=port,
        threads=threads,
        url_scheme='https' if os.getenv('SSL_ENABLED', 'false').lower() == 'true' else 'http',
        # Connection timeouts
        channel_timeout=120,
        # Performance settings
        asyncore_use_poll=True,
        # Logging
        _quiet=False
    )
