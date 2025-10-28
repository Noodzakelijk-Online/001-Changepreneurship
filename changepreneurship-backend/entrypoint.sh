#!/usr/bin/env bash
set -e

python wait_for_db.py

# Idempotent migration bootstrap (stamps if needed then upgrades)
python migrate_upgrade.py || echo "[entrypoint] migrate_upgrade.py failed (continuing)"

echo "[entrypoint] Starting app: $@"
exec "$@"
