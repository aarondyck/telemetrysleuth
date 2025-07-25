"""
Database models for Telemetry Sleuth SMDR data capture.

This module defines the CallRecord model that maps to the 37 fields
specified in the Avaya IP Office SMDR documentation.
"""

from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Interval, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()


class CallRecord(Base):
    """
    Model representing a single SMDR call record from Avaya IP Office.
    
    Maps to the 37 fields specified in the official Avaya SMDR documentation.
    Each record contains call information in comma-separated format (CSV).
    """
    __tablename__ = 'call_records'
    
    # Primary key (auto-generated)
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # SMDR Fields (in exact order as specified in Avaya documentation)
    
    # Field 1: Call Start Time - YYYY/MM/DD HH:MM:SS format
    call_start_time = Column(DateTime, nullable=True, index=True)
    
    # Field 2: Connected Time - Duration in HH:MM:SS format (converted to seconds)
    connected_time = Column(Integer, nullable=True)  # Duration in seconds
    
    # Field 3: Ring Time - Duration in seconds
    ring_time = Column(Integer, nullable=True)
    
    # Field 4: Caller - The caller's number
    caller = Column(String(100), nullable=True, index=True)
    
    # Field 5: Direction - I for inbound, O for outbound
    direction = Column(String(1), nullable=True)
    
    # Field 6: Called Number - The number called by the system
    called_number = Column(String(100), nullable=True, index=True)
    
    # Field 7: Dialed Number - For internal/outbound same as Called Number, for inbound the DDI
    dialed_number = Column(String(100), nullable=True)
    
    # Field 8: Account Code - The last account code attached to the call
    account_code = Column(String(50), nullable=True)
    
    # Field 9: Is Internal - 1 if both parties internal, 0 if not
    is_internal = Column(Boolean, nullable=True)
    
    # Field 10: Call ID - Numerical identifier for the call
    call_id = Column(Integer, nullable=True, index=True)
    
    # Field 11: Continuation - 1 if further records exist, 0 otherwise
    continuation = Column(Boolean, nullable=True)
    
    # Field 12: Party1 Device - Device 1 number (call initiator)
    party1_device = Column(String(50), nullable=True, index=True)
    
    # Field 13: Party1 Name - Name of device 1 (UTF-8 encoded)
    party1_name = Column(String(200), nullable=True)
    
    # Field 14: Party2 Device - The other party device
    party2_device = Column(String(50), nullable=True)
    
    # Field 15: Party2 Name - The other party's name
    party2_name = Column(String(200), nullable=True)
    
    # Field 16: Hold Time - Number of seconds call was held
    hold_time = Column(Integer, nullable=True)
    
    # Field 17: Park Time - Number of seconds call was parked
    park_time = Column(Integer, nullable=True)
    
    # Field 18: Authorization Valid - 1 for valid, 0 for invalid, blank for no code
    authorization_valid = Column(Boolean, nullable=True)
    
    # Field 19: Authorization Code - Shows n/a for security (always blank/n/a)
    authorization_code = Column(String(10), nullable=True)
    
    # Field 20: User Charged - User to which call charge assigned (AoC)
    user_charged = Column(String(100), nullable=True)
    
    # Field 21: Call Charge - Total call charge calculated
    call_charge = Column(String(20), nullable=True)
    
    # Field 22: Currency - System wide currency setting
    currency = Column(String(10), nullable=True)
    
    # Field 23: Amount at Last User Change - Current AoC amount at user change
    amount_at_last_user_change = Column(String(20), nullable=True)
    
    # Field 24: Call Units - Total call units
    call_units = Column(Integer, nullable=True)
    
    # Field 25: Units at Last User Change - Current AoC units at user change
    units_at_last_user_change = Column(Integer, nullable=True)
    
    # Field 26: Cost per Unit - Value in 1/10,000th of currency unit
    cost_per_unit = Column(Integer, nullable=True)
    
    # Field 27: Mark Up - Mark up value in 1/100th units
    mark_up = Column(Integer, nullable=True)
    
    # Field 28: External Targeting Cause - Who/what caused external call + reason
    external_targeting_cause = Column(String(10), nullable=True)
    
    # Field 29: External Targeter ID - Associated name of the targeter
    external_targeter_id = Column(String(100), nullable=True)
    
    # Field 30: External Targeted Number - External number called by system
    external_targeted_number = Column(String(100), nullable=True)
    
    # Field 31: Calling Party Server IP Address - Server IP where calling extension logged in
    calling_party_server_ip = Column(String(45), nullable=True)  # IPv6 compatible length
    
    # Field 32: Unique Call ID for Caller Extension - Unique identifier on calling server
    unique_call_id_caller = Column(String(50), nullable=True)
    
    # Field 33: Called Party Server IP Address - Server IP where called extension logged in
    called_party_server_ip = Column(String(45), nullable=True)  # IPv6 compatible length
    
    # Field 34: Unique Call ID for Called Extension - Unique identifier on called server
    unique_call_id_called = Column(String(50), nullable=True)
    
    # Field 35: SMDR Record Time - System date/time when record generated (YYYY/MM/DD HH:MM:SS)
    smdr_record_time = Column(DateTime, nullable=True)
    
    # Field 36: Caller Consent Directive - Auto-attendant consent (0, 2, 6)
    caller_consent_directive = Column(Integer, nullable=True)
    
    # Field 37: Calling Number Verification - Authentication level (A, B, C, N/A)
    calling_number_verification = Column(String(3), nullable=True)
    
    # Metadata fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    raw_data = Column(Text, nullable=True)  # Store original raw SMDR line for debugging
    
    def __repr__(self):
        return (f"<CallRecord(id={self.id}, "
                f"start_time={self.call_start_time}, "
                f"caller={self.caller}, "
                f"called={self.called_number}, "
                f"connected_time={self.connected_time}s)>")
    
    def to_dict(self):
        """Convert the CallRecord to a dictionary for JSON serialization."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat() if value else None
            elif isinstance(value, timedelta):
                result[column.name] = str(value) if value else None
            else:
                result[column.name] = value
        return result


# Database configuration
def get_database_url():
    """Get database URL from environment variables with fallback defaults."""
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'telemetrysleuth')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def create_database_engine():
    """Create and return a SQLAlchemy engine."""
    database_url = get_database_url()
    engine = create_engine(database_url, echo=False)
    return engine


def create_tables(engine):
    """Create all tables in the database."""
    Base.metadata.create_all(engine)


def get_session_factory(engine):
    """Create and return a session factory."""
    return sessionmaker(bind=engine)


# Global variables that will be initialized by the application
engine = None
SessionLocal = None


def init_database():
    """Initialize the database connection and create tables."""
    global engine, SessionLocal
    engine = create_database_engine()
    create_tables(engine)
    SessionLocal = get_session_factory(engine)
    return engine, SessionLocal


def get_db_session():
    """Get a database session. Use this in a context manager."""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    session = SessionLocal()
    return session


class DatabaseSession:
    """Context manager for database sessions."""
    
    def __init__(self):
        self.session = None
    
    def __enter__(self):
        self.session = get_db_session()
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type is not None:
                self.session.rollback()
            else:
                self.session.commit()
            self.session.close()


def get_db_context():
    """Get a database session context manager."""
    return DatabaseSession()
