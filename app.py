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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.database import DatabaseManager
from app.config import Config
from app.websocket_manager import start_websocket_server, get_websocket_manager
from app.models import init_database, get_db_context, CallRecord
from sqlalchemy import and_, or_, desc

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
    # Get search parameters
    caller = request.args.get('caller', '').strip()
    called = request.args.get('called', '').strip()
    direction = request.args.get('direction', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()
    is_internal = request.args.get('is_internal', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    try:
        with get_db_context() as session:
            # Build query with filters
            query = session.query(CallRecord)
            
            # Apply filters
            filters = []
            
            if caller:
                filters.append(CallRecord.caller.ilike(f'%{caller}%'))
            
            if called:
                filters.append(CallRecord.called_number.ilike(f'%{called}%'))
            
            if direction and direction in ['I', 'O']:
                filters.append(CallRecord.direction == direction)
            
            if is_internal and is_internal in ['0', '1']:
                filters.append(CallRecord.is_internal == (is_internal == '1'))
            
            if date_from:
                try:
                    date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
                    filters.append(CallRecord.call_start_time >= date_from_dt)
                except ValueError:
                    flash('Invalid "from" date format. Use YYYY-MM-DD.', 'error')
            
            if date_to:
                try:
                    date_to_dt = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
                    filters.append(CallRecord.call_start_time < date_to_dt)
                except ValueError:
                    flash('Invalid "to" date format. Use YYYY-MM-DD.', 'error')
            
            # Apply all filters
            if filters:
                query = query.filter(and_(*filters))
            
            # Order by most recent first
            query = query.order_by(desc(CallRecord.call_start_time))
            
            # Get total count for pagination
            total_records = query.count()
            
            # Apply pagination
            offset = (page - 1) * per_page
            records = query.offset(offset).limit(per_page).all()
            
            # Calculate pagination info
            total_pages = ceil(total_records / per_page)
            
            # Prepare search parameters for template
            search_params = {
                'caller': caller,
                'called': called,
                'direction': direction,
                'date_from': date_from,
                'date_to': date_to,
                'is_internal': is_internal
            }
            
            return render_template('search.html',
                                 records=records,
                                 search_params=search_params,
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
        flash(f'Error searching records: {str(e)}', 'error')
        return render_template('search.html', records=[], search_params={}, pagination={})


@app.route('/record/<int:record_id>')
def record_detail(record_id):
    """Display detailed view of a single call record."""
    try:
        with get_db_context() as session:
            record = session.query(CallRecord).filter(CallRecord.id == record_id).first()
            
            if not record:
                flash('Record not found.', 'error')
                return redirect(url_for('index'))
            
            return render_template('record_detail.html', record=record)
    
    except Exception as e:
        flash(f'Error loading record: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics."""
    try:
        with get_db_context() as session:
            stats = get_dashboard_stats(session)
            return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recent')
def api_recent():
    """API endpoint for recent call records."""
    limit = request.args.get('limit', 10, type=int)
    
    try:
        with get_db_context() as session:
            records = session.query(CallRecord)\
                            .order_by(desc(CallRecord.call_start_time))\
                            .limit(limit)\
                            .all()
            
            records_data = []
            for record in records:
                records_data.append({
                    'id': record.id,
                    'call_start_time': record.call_start_time.isoformat() if record.call_start_time else None,
                    'caller': record.caller,
                    'called_number': record.called_number,
                    'direction': record.direction,
                    'connected_time': record.connected_time,
                    'is_internal': record.is_internal,
                    'call_id': record.call_id
                })
            
            return jsonify(records_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_dashboard_stats(session):
    """Get dashboard statistics."""
    try:
        # Total records
        total_records = session.query(CallRecord).count()
        
        # Records today
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_records = session.query(CallRecord)\
                              .filter(CallRecord.call_start_time >= today)\
                              .count()
        
        # Inbound vs Outbound today
        inbound_today = session.query(CallRecord)\
                              .filter(and_(CallRecord.call_start_time >= today,
                                         CallRecord.direction == 'I'))\
                              .count()
        
        outbound_today = session.query(CallRecord)\
                               .filter(and_(CallRecord.call_start_time >= today,
                                          CallRecord.direction == 'O'))\
                               .count()
        
        # Internal vs External today
        internal_today = session.query(CallRecord)\
                               .filter(and_(CallRecord.call_start_time >= today,
                                          CallRecord.is_internal == True))\
                               .count()
        
        external_today = session.query(CallRecord)\
                               .filter(and_(CallRecord.call_start_time >= today,
                                          CallRecord.is_internal == False))\
                               .count()
        
        # Average call duration today (for connected calls)
        avg_duration_result = session.query(CallRecord.connected_time)\
                                   .filter(and_(CallRecord.call_start_time >= today,
                                              CallRecord.connected_time > 0))\
                                   .all()
        
        avg_duration = 0
        if avg_duration_result:
            durations = [r.connected_time for r in avg_duration_result if r.connected_time]
            if durations:
                avg_duration = sum(durations) / len(durations)
        
        return {
            'total_records': total_records,
            'today_records': today_records,
            'inbound_today': inbound_today,
            'outbound_today': outbound_today,
            'internal_today': internal_today,
            'external_today': external_today,
            'avg_duration': round(avg_duration, 1) if avg_duration else 0
        }
    
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {}


@app.template_filter('duration')
def duration_filter(seconds):
    """Convert seconds to HH:MM:SS format."""
    if not seconds or seconds == 0:
        return "00:00:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


@app.template_filter('direction_name')
def direction_name_filter(direction):
    """Convert direction code to human readable name."""
    if direction == 'I':
        return 'Inbound'
    elif direction == 'O':
        return 'Outbound'
    else:
        return 'Unknown'


@app.template_filter('call_type')
def call_type_filter(direction, is_internal):
    """Determine call type based on direction and internal flag."""
    if direction == 'I':
        return 'Incoming External' if not is_internal else 'Internal'
    elif direction == 'O':
        return 'Internal' if is_internal else 'Outgoing External'
    else:
        return 'Unknown'


@app.route('/api/stats')
def api_stats():
    """API endpoint for real-time statistics."""
    try:
        db_manager = DatabaseManager()
        stats = db_manager.get_dashboard_stats()
        
        # Add WebSocket server stats
        websocket_manager = get_websocket_manager()
        ws_status = websocket_manager.get_status()
        stats['websocket'] = {
            'connected_clients': ws_status['stats']['active_connections'],
            'total_connections': ws_status['stats']['total_connections'],
            'messages_sent': ws_status['stats']['messages_sent']
        }
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting API stats: {e}")
        return jsonify({'error': 'Failed to get statistics'}), 500


@app.route('/api/websocket/status')
def websocket_status():
    """Get WebSocket server status."""
    try:
        websocket_manager = get_websocket_manager()
        status = websocket_manager.get_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting WebSocket status: {e}")
        return jsonify({'error': 'Failed to get WebSocket status'}), 500


if __name__ == '__main__':
    # Start WebSocket server
    try:
        websocket_port = int(os.getenv('WEBSOCKET_PORT', '8765'))
        start_websocket_server(host='0.0.0.0', port=websocket_port)
        logger.info(f"WebSocket server started on port {websocket_port}")
    except Exception as e:
        logger.error(f"Failed to start WebSocket server: {e}")
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=config.DEBUG)