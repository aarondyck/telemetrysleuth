# Classes in data_export.py

## DataExporter
**Description:** Handles data export in various formats (CSV, JSON, Excel)

### Key Methods:
- `__init__`: Initializes the exporter with optional database manager
- `export_to_csv`: Exports records to CSV format
- `export_to_json`: Exports records to JSON format
- `export_to_excel`: Exports records to Excel format
- `export_records_by_filters`: Exports records based on specified filters
- `create_export_archive`: Creates a ZIP archive of exports
- `get_export_summary`: Retrieves summary information about potential exports

### Key Attributes:
- `db_manager`: Database manager for retrieving records
- `field_mappings`: Dictionary mapping internal field names to display names

# Classes in config.py

## Config (Base Configuration Class)
**Description:** Base configuration class for application settings

### Key Attributes:
- Database Configuration:
  - `DB_HOST`
  - `DB_PORT`
  - `DB_NAME`
  - `DB_USER`
  - `DB_PASSWORD`

- TCP Listener Configuration:
  - `TCP_HOST`
  - `TCP_PORT`

- Flask Configuration:
  - `SECRET_KEY`
  - `DEBUG`

- Application Settings:
  - `MAX_RECORDS_PER_PAGE`

### Key Methods:
- `DATABASE_URL` (property): Constructs database connection URL

## DevelopmentConfig
**Description:** Development-specific configuration inheriting from Config
- Enables DEBUG mode

## ProductionConfig
**Description:** Production-specific configuration inheriting from Config
- Disables DEBUG mode

## TestingConfig
**Description:** Testing-specific configuration inheriting from Config
- Enables TESTING mode
- Uses a separate test database

# Classes in logging_config.py
**No Classes Defined**

### Key Functions:
- `configure_logging()`: Configures logging with console and file handlers
  - Supports different log levels
  - Creates rotating file logs
  - Sets up formatters for console and file logging

### Global Logger Instances:
- `app_logger`
- `tcp_listener_logger`
- `websocket_logger`

# Classes in models.py

## CallRecord
**Description:** SQLAlchemy ORM model representing a single SMDR call record from Avaya IP Office

### Key Attributes:
- 37 fields mapped from Avaya SMDR documentation
- Fields include:
  - `call_start_time`
  - `caller`
  - `called_number`
  - `direction`
  - `connected_time`
  - And many more detailed SMDR record fields

### Key Methods:
- `__repr__()`: String representation of the call record
- `to_dict()`: Convert CallRecord to a dictionary for JSON serialization

## DatabaseSession
**Description:** Context manager for database sessions
- Manages database session lifecycle
- Handles session commit and rollback

# Classes in parser.py

## SMDRParser
**Description:** Parser for Avaya IP Office SMDR records
- Converts comma-separated SMDR strings into CallRecord objects
- Performs data validation and type conversion

### Key Methods:
- `parse_record()`: Parse a raw SMDR record string into a CallRecord object
- Private parsing methods:
  - `_parse_string()`
  - `_parse_integer()`
  - `_parse_boolean()`
  - `_parse_datetime()`
  - `_parse_duration_to_seconds()`

### Attributes:
- `expected_field_count`: Number of expected fields in an SMDR record (37)

### Related Functions:
- `validate_smdr_record()`: Validate a parsed SMDR record for basic consistency

# Classes in tcp_listener.py

## SMDRHandler
**Description:** Handler for individual SMDR client connections
- Processes incoming byte streams
- Decodes and splits records based on \r\n terminators
- Manages individual client connection lifecycle

### Key Methods:
- `handle()`: Primary method for processing client connection
- `process_smdr_record()`: Parse and store individual SMDR records

## ThreadedTCPServer
**Description:** Threaded TCP Server for handling multiple SMDR connections simultaneously
- Allows concurrent SMDR data processing
- Supports daemon threads

## SMDRTCPListener
**Description:** Main SMDR TCP Listener service
- Manages TCP server lifecycle
- Handles graceful startup and shutdown
- Initializes database connection

### Key Methods:
- `start()`: Start the SMDR TCP listener
- `stop()`: Stop the SMDR TCP listener
- `run_forever()`: Run service until interrupted

# Classes in websocket_manager.py

## WebSocketManager
**Description:** Manages WebSocket connections and real-time updates
- Handles client connections and subscriptions
- Broadcasts messages with optional filtering
- Provides real-time statistics and monitoring

### Key Methods:
- `register_client()`: Register a new WebSocket client
- `unregister_client()`: Remove a WebSocket client
- `handle_client_message()`: Process incoming client messages
- `broadcast_message()`: Send messages to connected clients
- `start_server()`: Initialize WebSocket server
- `stop_server()`: Gracefully stop WebSocket server

### Key Features:
- Thread-safe client management
- Subscription and filtering system
- Background message processing
- Connection statistics tracking

# Classes in smdr_parser.py
**No Classes Defined**

### Key Functions:
- (See file for function details; no class-based structure present)