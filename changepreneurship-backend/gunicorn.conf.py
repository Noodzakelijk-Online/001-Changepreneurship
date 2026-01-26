"""Gunicorn WSGI production configuration."""
import multiprocessing
import os

# Bind to all interfaces on port 5000
bind = "0.0.0.0:5000"

# Worker processes
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = os.getenv("LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "changepreneurship-backend"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (disabled by default, enable via env vars)
keyfile = os.getenv("SSL_KEYFILE")
certfile = os.getenv("SSL_CERTFILE")

# Preload app for better memory efficiency
preload_app = True

# Graceful timeout for worker restart
graceful_timeout = 30

def on_starting(server):
    """Called just before master process is initialized."""
    print(f"[Gunicorn] Starting with {workers} workers")

def on_reload(server):
    """Called when reloading."""
    print("[Gunicorn] Reloading workers")

def when_ready(server):
    """Called just after master process is initialized."""
    print("[Gunicorn] Server is ready. Listening on:", bind)

def pre_fork(server, worker):
    """Called just before worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after worker is forked."""
    print(f"[Gunicorn] Worker spawned (pid: {worker.pid})")

def worker_exit(server, worker):
    """Called just after worker exited."""
    print(f"[Gunicorn] Worker exited (pid: {worker.pid})")
