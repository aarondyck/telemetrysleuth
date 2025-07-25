# Telemetry Sleuth Development Guide

## 1. Project Overview

### Purpose
Telemetry Sleuth is a comprehensive SMDR (Station Message Detail Recording) data capture and analysis tool for Avaya IP Office systems. It provides real-time call data processing, storage, and visualization.

### Key Technologies
- **Backend**: Python 3.9+
- **Web Framework**: Flask
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Containerization**: Docker, Docker Compose
- **Testing**: Python unittest

### Architecture
- **TCP Listener**: Captures raw SMDR data from IP Office
- **SMDR Parser**: Converts raw data into structured records
- **Database**: Stores and indexes call records
- **Web Interface**: Provides query and visualization capabilities

## 2. Getting Started

### Prerequisites
- Python 3.9+
- Docker Engine 20.10+
- Docker Compose 2.0+
- PostgreSQL 13+

### Local Development Setup
1. Clone the repository
   ```bash
   git clone https://github.com/your-org/telemetry-sleuth.git
   cd telemetry-sleuth
   ```

2. Create virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # Or
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. Run application
   ```bash
   # Start TCP listener
   python tcp_listener.py
   
   # Run web interface
   flask run
   ```

### Docker Deployment
```bash
docker-compose up -d
```

## 3. Project Structure

```
telemetry-sleuth/
├── app/                  # Core application logic
│   ├── __init__.py       # Package initialization
│   ├── models.py         # Database models
│   ├── parser.py         # SMDR record parsing
│   └── tcp_listener.py   # Network data capture
├── tests/                # Unit and integration tests
├── templates/            # Web interface templates
├── static/               # Static web assets
├── docker-compose.yml    # Container orchestration
└── Dockerfile            # Container definition
```

## 4. Development Workflow

### Coding Standards
- Follow PEP 8 Python style guidelines
- Use type hints
- Write docstrings for all functions and classes
- Maintain 80-character line limit

### Testing
```bash
# Run all tests
python run_tests.py

# Run specific test suite
python -m unittest tests/test_parser.py
```

### Branching Strategy
- `main`: Stable production code
- `feature/`: New feature branches
- `bugfix/`: Bug resolution branches

### Commit Message Convention
```
<type>(<scope>): <description>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation update
- test: Test-related changes
- refactor: Code restructuring
```

## 5. Core Concepts

### SMDR Record Parsing
- 37 fields extracted from comma-separated records
- Robust error handling for malformed data
- Type conversion (string → datetime, int)

### Database Model
- Comprehensive `CallRecord` model
- Indexes on frequently queried fields
- Nullable fields for flexible data capture

### TCP Listener
- Multi-threaded socket server
- Configurable host and port
- Handles concurrent connection attempts

## 6. Common Tasks

### Adding New SMDR Field
1. Update `app/models.py`
2. Modify `app/parser.py`
3. Update database migration
4. Write corresponding tests

### Configuring IP Office
1. Access IP Office Manager
2. Navigate to Call Logging
3. Set SMDR Server IP and Port
4. Enable SMDR Output

## 7. Troubleshooting

### Common Issues
- Database connection failures
- TCP listener port conflicts
- SMDR parsing errors

### Debugging Tips
- Check `.env` configuration
- Verify network settings
- Review application logs
- Use `logging` module for tracing

## 8. Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | Database hostname | localhost |
| `DB_PORT` | Database port | 5432 |
| `DB_NAME` | Database name | telemetrysleuth |
| `TCP_HOST` | Listener IP | 0.0.0.0 |
| `TCP_PORT` | Listener port | 9000 |

## 9. References

- [Avaya IP Office SMDR Documentation](https://your-avaya-docs-link)
- [SQLAlchemy ORM Guide](https://docs.sqlalchemy.org/en/14/orm/)
- [Flask Documentation](https://flask.palletsprojects.com/)

## 10. Future Roadmap
- Real-time WebSocket dashboard
- Advanced call analytics
- Extended export capabilities

## 11. Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create pull request

**Note**: This is an internal project. Coordinate with team before significant changes.