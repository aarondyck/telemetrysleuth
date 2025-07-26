"""
Centralized logging configuration for Telemetry Sleuth.
Supports different log levels and output formats.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

def configure_logging(service_type='app'):
    """
    Configure logging with rotating file handler and console output.
    
    Args:
        service_type (str): Type of service (app, tcp-listener, etc.)
    """
    # Ensure log directory exists
    log_dir = os.getenv('LOG_DIR', '/app/logs')
    os.makedirs(log_dir, exist_ok=True)

    # Determine log level
    log_level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    log_level = log_levels.get(log_level_str, logging.INFO)

    # Create logger
    logger = logging.getLogger('telemetry_sleuth')
    logger.setLevel(log_level)

    # Clear any existing handlers
    logger.handlers.clear()

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File Handler with Rotation
    log_filename = os.path.join(log_dir, f'{service_type}_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = RotatingFileHandler(
        log_filename, 
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger

# Global logger instances
app_logger = configure_logging('app')
tcp_listener_logger = configure_logging('tcp-listener')
websocket_logger = configure_logging('websocket')