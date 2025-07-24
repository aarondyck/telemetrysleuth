# Telemetry Sleuth

A self-contained, containerized application for capturing, storing, and displaying Avaya IP Office SMDR (Station Message Detail Recording) data through a web interface.

## 🎯 Project Overview

Telemetry Sleuth captures real-time call data from Avaya IP Office systems via TCP connection, parses the SMDR records, stores them in a PostgreSQL database, and provides a web interface for viewing and filtering call logs.

## 🏗️ Architecture

```
┌─────────────────┐    TCP:9000     ┌─────────────────┐
│   Avaya IP      │ ──────────────► │  TCP Listener   │
│   Office        │     SMDR        │   Service       │
│   System        │     Data        │                 │
└─────────────────┘                 └─────────────────┘
                                            │
                                            ▼
                                    ┌─────────────────┐
                                    │  SMDR Parser    │
                                    │                 │
                                    └─────────────────┘
                                            │
                                            ▼
                                    ┌─────────────────┐
                                    │  PostgreSQL     │
                                    │  Database       │
                                    └─────────────────┘
                                            │
                                            ▼
                                    ┌─────────────────┐
                                    │  Flask Web      │
                                    │  Interface      │
                                    └─────────────────┘
```

## 📋 Features Implemented

### ✅ Phase 1: Backend Foundation & Data Processing

- **Complete Database Model**: All 37 SMDR fields mapped according to Avaya documentation
- **Robust TCP Listener**: Multi-threaded server handling concurrent connections
- **SMDR Parser**: Comprehensive parser with data validation and type conversion
- **Error Handling**: Graceful handling of malformed records and connection issues

### 🔄 Current Status

**Completed Tasks:**
- ✅ Task 1.1: Project Scaffolding & Database Modeling
- ✅ Task 1.2: TCP Listener Service  
- ✅ Task 1.3: SMDR Parser & Database Integration

**Next Phase:**
- 🔄 Phase 2: Web Interface & Containerization (In Progress)

## 🗄️ Database Schema

The `CallRecord` model contains all 37 SMDR fields:

| Field | Description | Type |
|-------|-------------|------|
| call_start_time | Call start timestamp | DateTime |
| connected_time | Duration connected (seconds) | Integer |
| ring_time | Ring duration (seconds) | Integer |
| caller | Caller's number | String |
| direction | Call direction (I/O) | String |
| called_number | Number called | String |
| party1_device | Device 1 identifier | String |
| party1_name | Device 1 name | String |
| ... | ... | ... |

*See `app/models.py` for complete field definitions.*

## 🚀 Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

### Running with Docker

1. **Clone and navigate to project:**
   ```bash
   cd telemetrysleuth
   ```

2. **Start the services:**
   ```bash
   docker-compose up -d
   ```

3. **Verify services are running:**
   ```bash
   docker-compose ps
   ```

### Manual Setup (Development)

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL database:**
   ```bash
   # Update .env file with your database credentials
   cp .env.example .env
   ```

4. **Run the TCP listener:**
   ```bash
   python tcp_listener.py
   ```

## 🧪 Testing

### Run Parser Tests
```bash
python tests/test_parser.py
```

### Run All Tests
```bash
python run_tests.py
```

### Send Test SMDR Data
```bash
python tests/test_smdr_sender.py --count 10
```

## 🔧 Configuration

Configuration is managed through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | Database host | localhost |
| `DB_PORT` | Database port | 5432 |
| `DB_NAME` | Database name | telemetrysleuth |
| `DB_USER` | Database user | postgres |
| `DB_PASSWORD` | Database password | postgres |
| `TCP_HOST` | TCP listener host | 0.0.0.0 |
| `TCP_PORT` | TCP listener port | 9000 |

## 📡 Avaya IP Office Configuration

To configure your Avaya IP Office to send SMDR data to Telemetry Sleuth:

1. **Access System Configuration:**
   - Log into IP Office Manager
   - Navigate to System → System

2. **Configure SMDR Output:**
   - Go to System → Call Logging
   - Set Output → SMDR Output: On
   - Set SMDR Server IP: `<your-server-ip>`
   - Set SMDR Server Port: `9000`

3. **Save and Reboot:**
   - Save configuration
   - Reboot IP Office system

## 📊 SMDR Record Format

Each SMDR record contains 37 comma-separated fields terminated by `\r\n`:

```
2024/01/15 14:30:25,00:02:35,5,2001,O,5551234567,5551234567,,0,1000001,0,E2001,John Smith,T9001,Line 1,0,0,,,,,,,,,,,,,,,,,2024/01/15 14:33:00,0,
```

## 🐛 Troubleshooting

### TCP Listener Issues
- **Port already in use**: Check if another service is using port 9000
- **Connection refused**: Verify firewall settings and IP Office configuration
- **Database connection errors**: Ensure PostgreSQL is running and credentials are correct

### Parser Issues
- **Field count mismatch**: Check SMDR format version on IP Office
- **Invalid datetime**: Verify system time synchronization
- **Encoding issues**: Ensure UTF-8 encoding on IP Office SMDR output

## 📁 Project Structure

```
telemetrysleuth/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Configuration management
│   ├── models.py            # Database models
│   ├── parser.py            # SMDR parser
│   └── tcp_listener.py      # TCP listener service
├── tests/
│   ├── test_parser.py       # Parser unit tests
│   └── test_smdr_sender.py  # Test data sender
├── templates/               # HTML templates (future)
├── static/                  # Static assets (future)
├── docker-compose.yml       # Docker orchestration
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
├── tcp_listener.py         # Standalone listener script
└── README.md               # This file
```

## 🚧 Coming Next (Phase 2)

- **Flask Web Interface**: View and filter call records
- **Real-time Dashboard**: Live call monitoring
- **Advanced Filtering**: Date ranges, extensions, call types
- **Export Functionality**: CSV/Excel export of call data

## 📝 License

This project is developed for internal use. All rights reserved.

## 🤝 Contributing

This is an internal project. For questions or issues, please contact the development team.