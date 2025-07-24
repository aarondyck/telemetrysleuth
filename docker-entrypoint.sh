#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
wait_for_postgres() {
    echo "Waiting for PostgreSQL to be ready..."
    until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 2
    done
    echo "PostgreSQL is ready!"
}

# Initialize database if needed
init_database() {
    echo "Initializing database..."
    python -c "
from app.models import init_database
try:
    init_database()
    print('Database initialized successfully')
except Exception as e:
    print(f'Database initialization error: {e}')
    exit(1)
"
}

# Main execution
case "$1" in
    tcp-listener)
        wait_for_postgres
        init_database
        echo "Starting TCP Listener..."
        exec python tcp_listener.py
        ;;
    web)
        wait_for_postgres
        init_database
        echo "Starting Web Application..."
        exec python app.py
        ;;
    test)
        wait_for_postgres
        init_database
        echo "Running tests..."
        exec python -m pytest tests/ -v
        ;;
    bash)
        exec /bin/bash
        ;;
    *)
        exec "$@"
        ;;
esac