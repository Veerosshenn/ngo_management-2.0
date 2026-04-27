#!/usr/bin/env sh
set -eu

echo "Starting container..."

: "${PORT:=8000}"

wait_for_db() {
  if [ -z "${DATABASE_URL:-}" ]; then
    echo "DATABASE_URL not set; skipping DB wait."
    return 0
  fi

  echo "Waiting for database..."
  python - <<'PY'
import os, time
import dj_database_url
import psycopg2

url = os.environ.get("DATABASE_URL")
cfg = dj_database_url.parse(url)
host = cfg.get("HOST")
port = int(cfg.get("PORT") or 5432)
name = cfg.get("NAME")
user = cfg.get("USER")
pw = cfg.get("PASSWORD")

deadline = time.time() + 60
last = None
while time.time() < deadline:
    try:
        psycopg2.connect(host=host, port=port, dbname=name, user=user, password=pw).close()
        print("DB is ready.")
        raise SystemExit(0)
    except Exception as e:
        last = e
        time.sleep(2)
print(f"DB not ready after timeout: {last!r}")
raise SystemExit(1)
PY
}

wait_for_db

python manage.py collectstatic --noinput
python manage.py migrate

echo "Launching gunicorn on 0.0.0.0:${PORT}..."
exec gunicorn ngo_management.wsgi:application --bind "0.0.0.0:${PORT}" --workers 2 --threads 4 --timeout 120

