#!/bin/sh
set -e

# Wait for DB and Redis
echo "Waiting for database and redis..."
python << END
import os
import sys
import time
import socket
import psycopg2
from urllib.parse import urlparse

db_url = os.getenv('DATABASE_URL')
redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')

# Check DB Connectivity and Authentication
if db_url:
    p = urlparse(db_url)
    host = p.hostname
    port = p.port or 5432
    print(f"Checking DB connection at {host}:{port}...")
    
    start = time.time()
    while time.time() - start < 30:
        try:
            # First check if port is open
            s = socket.create_connection((host, port), timeout=2)
            s.close()
            
            # Then try to authenticate
            try:
                conn = psycopg2.connect(db_url, connect_timeout=5)
                conn.close()
                print("DB connection and authentication successful!")
                break
            except psycopg2.OperationalError as e:
                if "password authentication failed" in str(e):
                    print("\n" + "="*50)
                    print("CRITICAL ERROR: Database password authentication failed!")
                    print("Please verify the credentials in your .env file.")
                    print("="*50 + "\n")
                    sys.exit(1)
                print(f"DB reachable but connection failed: {e}")
                time.sleep(2)
        except Exception as e:
            print(f"Waiting for DB port... ({e})")
            time.sleep(2)
    else:
        print("Timeout waiting for DB")
        sys.exit(1)

# Check Redis
r = urlparse(redis_url)
r_host = r.hostname
r_port = r.port or 6379
print(f"Checking Redis connection at {r_host}:{r_port}...")
start = time.time()
while time.time() - start < 30:
    try:
        s = socket.create_connection((r_host, r_port), timeout=2)
        s.close()
        print("Redis is up!")
        break
    except:
        time.sleep(1)
else:
    print("Timeout waiting for Redis")
    sys.exit(1)
END

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout "${GUNICORN_TIMEOUT:-60}" \
  --reload \
  --access-logfile - \
  --error-logfile -
