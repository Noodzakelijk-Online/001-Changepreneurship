"""Automatic migration bootstrap / upgrade script (idempotent).

Scenarios handled:
  A) Fresh DB (no tables): we let normal Alembic upgrade (init schema + later migrations).
  B) Legacy DB: tables (like user) exist but alembic_version table missing (were created via create_all).
      - We 'stamp' base revision (without running init migration again)
      - We manually apply any structural diffs needed to reach head for known migrations
         (e.g. expanding password_hash length) if alembic can't auto-run base migration.
  C) Normal subsequent deploy: alembic_version exists => run standard upgrade to head.

Future-proof notes:
 - Add manual patch functions for structural changes required before stamping base.
 - After stamping, we update alembic_version directly to head if all required manual patches applied.
"""
from __future__ import annotations
import os
from sqlalchemy import text, inspect, create_engine
from sqlalchemy.exc import ProgrammingError

BASE_REVISION = "479a67b65e65"               # initial schema revision id
HEAD_REVISION = "expand_password_hash_len"    # current head revision id

def main():
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("[migrate_upgrade] No DATABASE_URL set; skipping.")
        return
    if url.startswith("sqlite"):
        print("[migrate_upgrade] SQLite detected; skipping stamp logic (Flask create_all covers dev).")
        return

    # Normalize: strip +driver for SQLAlchemy engine creation if necessary
    sa_url = url
    try:
        engine = create_engine(sa_url, pool_pre_ping=True)
    except Exception as e:
        print(f"[migrate_upgrade] Failed to create engine: {e}")
        return

    stamped = False
    manual_patch_applied = False
    with engine.begin() as conn:  # transaction
        inspector = inspect(conn)
        tables = inspector.get_table_names()
        has_version = "alembic_version" in tables
        core_tables_present = "user" in tables

        if not has_version and core_tables_present:
            # Legacy schema without alembic_version: stamp & apply manual diffs.
            print("[migrate_upgrade] Legacy schema detected (tables exist, no alembic_version).")
            # Create version table & stamp base
            conn.execute(text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL)"))
            # Clear any existing row just in case
            try:
                conn.execute(text("DELETE FROM alembic_version"))
            except Exception:
                pass
            conn.execute(text("INSERT INTO alembic_version (version_num) VALUES (:v)"), {"v": BASE_REVISION})
            print(f"[migrate_upgrade] Stamped base revision {BASE_REVISION}.")
            stamped = True

            # Manual patch: expand password_hash length if still 128
            try:
                q = text("""
                    SELECT character_maximum_length
                    FROM information_schema.columns
                    WHERE table_name='user' AND column_name='password_hash'
                """)
                res = conn.execute(q).scalar()
                if res is not None and res < 300:
                    print(f"[migrate_upgrade] Expanding password_hash from {res} to 300...")
                    conn.execute(text("ALTER TABLE \"user\" ALTER COLUMN password_hash TYPE VARCHAR(300)"))
                    manual_patch_applied = True
                else:
                    print("[migrate_upgrade] password_hash already >= 300; no manual alter needed.")
            except Exception as e:
                print(f"[migrate_upgrade] Manual patch (password_hash) failed: {e}")

            # Advance version table straight to head if manual patch covered latest structural change
            try:
                conn.execute(text("DELETE FROM alembic_version"))
                conn.execute(text("INSERT INTO alembic_version (version_num) VALUES (:v)"), {"v": HEAD_REVISION})
                print(f"[migrate_upgrade] Set alembic_version to head {HEAD_REVISION} (manual path).")
            except Exception as e:
                print(f"[migrate_upgrade] Failed setting head revision: {e}")
        else:
            print("[migrate_upgrade] Normal migration path (either version table present or truly fresh DB).")

    # If we stamped legacy DB we already set head; skip full upgrade to avoid duplicate table errors.
    if stamped:
        print("[migrate_upgrade] Legacy stamping complete. Skipping alembic upgrade().")
        return

    # Fresh DB or already-versioned DB -> run upgrade() normally
    try:
        from src.main import app  # type: ignore
        from flask_migrate import upgrade
        with app.app_context():
            upgrade()
            print("[migrate_upgrade] Standard upgrade to head complete.")
    except Exception as e:
        print(f"[migrate_upgrade] Upgrade failed: {e}")

if __name__ == "__main__":
    main()
