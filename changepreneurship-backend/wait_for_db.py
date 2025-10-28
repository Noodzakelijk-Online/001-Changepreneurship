import os, time, sys
import psycopg
from urllib.parse import urlparse

def main():
    raw_url = os.environ.get('DATABASE_URL', '')
    if 'postgresql' not in raw_url:
        print('[wait_for_db] Non-Postgres URL detected -> skipping wait')
        return

    # SQLAlchemy style URL may include +psycopg driver; psycopg.connect expects either DSN params or a plain URI without driver spec.
    # Example: postgresql+psycopg://user:pass@host:5432/dbname -> need to strip '+psycopg'
    if '+psycopg' in raw_url:
        pg_url = raw_url.replace('+psycopg', '')
    else:
        pg_url = raw_url

    # Fallback: build DSN manually if parsing needed
    try:
        parsed = urlparse(pg_url)
        if parsed.scheme.startswith('postgres'):  # postgres or postgresql
            dsn = f"host={parsed.hostname} port={parsed.port or 5432} dbname={parsed.path.lstrip('/')} user={parsed.username}"
            if parsed.password:
                dsn += f" password={parsed.password}"
        else:
            dsn = pg_url
    except Exception:
        dsn = pg_url
    max_attempts = 30
    for attempt in range(1, max_attempts+1):
        try:
            with psycopg.connect(dsn, connect_timeout=3) as conn:
                with conn.cursor() as cur:
                    cur.execute('SELECT 1')
                print('[wait_for_db] Database ready')
                return
        except Exception as e:
            print(f'[wait_for_db] Attempt {attempt}/{max_attempts} failed: {e}')
            time.sleep(2)
    print('[wait_for_db] Giving up after max attempts')
    sys.exit(1)

if __name__ == '__main__':
    main()