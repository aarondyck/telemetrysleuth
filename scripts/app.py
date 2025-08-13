#!/usr/bin/env python3
"""
Main Flask application for Telemetry Sleuth web interface.
"""

import logging
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
"""
Flask Web Application for Telemetry Sleuth SMDR Data Display.

This module provides a web interface for viewing, filtering, and managing
SMDR call records captured from Avaya IP Office systems.
"""

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from datetime import datetime, timedelta
import sys
import os
from math import ceil

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import init_database, get_db_context, CallRecord

from app.config import Config
from app.websocket_manager import start_websocket_server, get_websocket_manager
from sqlalchemy import and_, or_, desc
# Create Flask application
app = Flask(__name__)

# Placeholder for get_dashboard_stats if missing
def get_dashboard_stats(session):
    # TODO: Implement actual dashboard stats logic
    return {}

# Create Flask application
app = Flask(__name__)

# Load configuration
config = Config()
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['DEBUG'] = config.DEBUG

# Initialize database
try:
    init_database()
    print("Database initialized successfully")
except Exception as e:
    print(f"Failed to initialize database: {e}")
    sys.exit(1)


@app.route('/')
def index():
    """Main dashboard page showing recent call records."""
    page = request.args.get('page', 1, type=int)
    per_page = 50  # Records per page
    
    try:
        with get_db_context() as session:
            # Get total count
            total_records = session.query(CallRecord).count()
            
            # Get recent records with pagination
            records_query = session.query(CallRecord).order_by(desc(CallRecord.call_start_time))
            
            # Calculate offset
            offset = (page - 1) * per_page
            records = records_query.offset(offset).limit(per_page).all()
            
            # Calculate pagination info
            total_pages = ceil(total_records / per_page)
            
            # Get some basic statistics
            stats = get_dashboard_stats(session)
            
            return render_template('index.html',
                                 records=records,
                                 stats=stats,
                                 pagination={
                                     'page': page,
                                     'per_page': per_page,
                                     'total': total_records,
                                     'total_pages': total_pages,
                                     'has_prev': page > 1,
                                     'has_next': page < total_pages,
                                     'prev_num': page - 1 if page > 1 else None,
                                     'next_num': page + 1 if page < total_pages else None
                                 })
    
    except Exception as e:
        flash(f'Error loading records: {str(e)}', 'error')
        return render_template('index.html', records=[], stats={}, pagination={})



@app.route('/search')
def search():
    """Search and filter call records."""
    # Example implementation: just render the search page
    return render_template('search.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
