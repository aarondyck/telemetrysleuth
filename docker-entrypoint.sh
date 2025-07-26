#!/bin/bash
set -eo pipefail

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# Wait for PostgreSQL to be ready
wait_for_postgres() {
    local max_attempts=30
    local attempt=0

    log "Waiting for PostgreSQL to be ready at $DB_HOST:$DB_PORT..."
    
    while [ $attempt -lt $max_attempts ]; do
        if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -q; then
            log "PostgreSQL is ready!"
            return 0
        fi
        
        log "PostgreSQL is unavailable - attempt $((attempt+1))/$max_attempts"
        attempt=$((attempt+1))
        sleep 2
    done

    log "ERROR: PostgreSQL did not become ready in time"
    exit 1
}

# Initialize database if needed
init_database() {
    log "Initializing database..."
    python -c "
from app.models import init_database
import sys
try:
    init_database()
    print('Database initialized successfully')
except Exception as e:
    print(f'Database initialization error: {e}')
    sys.exit(1)
"
}

# Start WebSocket server
start_websocket_server() {
    log "Starting WebSocket server..."
    python -m websockets_server &
}

# Main execution
main() {
    # Set default log level if not specified
    export LOG_LEVEL=${LOG_LEVEL:-INFO}
    export LOG_DIR=${LOG_DIR:-/app/logs}

    # Ensure log directory exists
    mkdir -p "$LOG_DIR"

    # Wait for database
    wait_for_postgres

    # Initialize database
    init_database

    # Determine service type
    case "${SERVICE_TYPE:-auto}" in
        tcp-listener)
            log "Starting TCP Listener Service..."
            start_websocket_server
            python tcp_listener.py
            ;;
        web)
            log "Starting Web Application..."
            gunicorn \
                --workers=${GUNICORN_WORKERS:-4} \
                --threads=${GUNICORN_THREADS:-2} \
                --bind 0.0.0.0:5000 \
                --access-logfile "${LOG_DIR}/gunicorn_access.log" \
                --error-logfile "${LOG_DIR}/gunicorn_error.log" \
                app:app
            ;;
        test)
            log "Running Test Suite..."
            python -m pytest tests/ -v
            ;;
        *)
            log "ERROR: Invalid SERVICE_TYPE"
            exit 1
            ;;
    esac
}

# Trap signals for graceful shutdown
trap 'log "Container stopped"; exit 0' SIGTERM SIGINT

# Execute main function
main

