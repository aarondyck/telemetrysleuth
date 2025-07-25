/**
 * WebSocket Client for Real-time Updates
 * Handles WebSocket connections and real-time data updates
 */

class WebSocketClient {
    constructor(options = {}) {
        this.host = options.host || window.location.hostname;
        this.port = options.port || 8765;
        this.reconnectInterval = options.reconnectInterval || 5000;
        this.maxReconnectAttempts = options.maxReconnectAttempts || 10;
        
        this.socket = null;
        this.reconnectAttempts = 0;
        this.isConnected = false;
        this.subscriptions = new Set();
        this.messageHandlers = new Map();
        this.connectionListeners = new Set();
        
        this.setupMessageHandlers();
        this.connect();
    }

    connect() {
        try {
            const wsUrl = `ws://${this.host}:${this.port}`;
            console.log(`Connecting to WebSocket: ${wsUrl}`);
            
            this.socket = new WebSocket(wsUrl);
            this.setupSocketEventHandlers();
            
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.scheduleReconnect();
        }
    }

    setupSocketEventHandlers() {
        this.socket.onopen = (event) => {
            console.log('WebSocket connected');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.notifyConnectionListeners('connected');
            this.showConnectionStatus('Connected', 'success');
            
            // Resubscribe to previous subscriptions
            this.resubscribe();
        };

        this.socket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.handleMessage(message);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };

        this.socket.onclose = (event) => {
            console.log('WebSocket disconnected:', event.code, event.reason);
            this.isConnected = false;
            this.notifyConnectionListeners('disconnected');
            this.showConnectionStatus('Disconnected', 'danger');
            
            if (!event.wasClean) {
                this.scheduleReconnect();
            }
        };

        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showConnectionStatus('Connection Error', 'warning');
        };
    }

    setupMessageHandlers() {
        // Handle welcome messages
        this.onMessage('welcome', (data) => {
            console.log('Received welcome message:', data.message);
        });

        // Handle new call records
        this.onMessage('new_record', (data) => {
            this.handleNewRecord(data.data);
        });

        // Handle statistics updates
        this.onMessage('stats_update', (data) => {
            this.handleStatsUpdate(data.data);
        });

        // Handle subscription confirmations
        this.onMessage('subscription_confirmed', (data) => {
            console.log('Subscription confirmed:', data.filters);
        });

        // Handle pong responses
        this.onMessage('pong', (data) => {
            console.log('Received pong:', data.timestamp);
        });

        // Handle errors
        this.onMessage('error', (data) => {
            console.error('WebSocket error message:', data.message);
            this.showNotification('WebSocket Error: ' + data.message, 'error');
        });
    }

    handleMessage(message) {
        const handler = this.messageHandlers.get(message.type);
        if (handler) {
            handler(message);
        } else {
            console.log('Unhandled message type:', message.type, message);
        }
    }

    handleNewRecord(recordData) {
        console.log('New call record received:', recordData);
        
        // Update dashboard if we're on the dashboard page
        if (window.location.pathname === '/') {
            this.updateDashboardWithNewRecord(recordData);
        }
        
        // Update search results if we're on the search page
        if (window.location.pathname === '/search') {
            this.updateSearchResultsWithNewRecord(recordData);
        }
        
        // Show notification for new record
        this.showNewRecordNotification(recordData);
    }

    handleStatsUpdate(statsData) {
        console.log('Statistics update received:', statsData);
        
        // Update dashboard statistics
        if (window.location.pathname === '/') {
            this.updateDashboardStats(statsData);
        }
    }

    updateDashboardWithNewRecord(record) {
        // Add new record to the top of the recent records table
        const tableBody = document.querySelector('.table tbody');
        if (tableBody) {
            const newRow = this.createRecordRow(record);
            tableBody.insertBefore(newRow, tableBody.firstChild);
            
            // Remove the last row if we have too many
            const rows = tableBody.querySelectorAll('tr');
            if (rows.length > 20) {
                tableBody.removeChild(rows[rows.length - 1]);
            }
            
            // Highlight the new row
            newRow.classList.add('table-success');
            setTimeout(() => {
                newRow.classList.remove('table-success');
            }, 3000);
        }
    }

    updateSearchResultsWithNewRecord(record) {
        // Only add if the record matches current search filters
        const currentFilters = this.getCurrentSearchFilters();
        if (this.recordMatchesFilters(record, currentFilters)) {
            const tableBody = document.querySelector('.table tbody');
            if (tableBody) {
                const newRow = this.createRecordRow(record);
                tableBody.insertBefore(newRow, tableBody.firstChild);
                
                // Highlight the new row
                newRow.classList.add('table-info');
                setTimeout(() => {
                    newRow.classList.remove('table-info');
                }, 3000);
            }
        }
    }

    updateDashboardStats(stats) {
        // Update statistics cards
        const statsElements = {
            'total-records': stats.total_records,
            'today-records': stats.today_records,
            'inbound-today': stats.inbound_today,
            'outbound-today': stats.outbound_today,
            'internal-today': stats.internal_today,
            'external-today': stats.external_today,
            'avg-duration': (stats.avg_duration || 0).toFixed(1) + 's'
        };

        for (const [id, value] of Object.entries(statsElements)) {
            const element = document.getElementById(id);
            if (element && element.textContent !== value.toString()) {
                // Add animation effect
                element.style.transition = 'all 0.3s ease';
                element.style.transform = 'scale(1.1)';
                element.style.color = '#28a745';
                element.textContent = value;
                
                setTimeout(() => {
                    element.style.transform = 'scale(1)';
                    element.style.color = '';
                }, 300);
            }
        }
    }

    createRecordRow(record) {
        const row = document.createElement('tr');
        row.className = record.is_internal ? 'call-internal' : 'call-external';
        
        const callTime = record.call_start_time ? new Date(record.call_start_time) : null;
        const duration = this.formatDuration(record.connected_time || 0);
        
        row.innerHTML = `
            <td>
                ${callTime ? `
                    <small>${callTime.toLocaleDateString()}</small><br>
                    <strong>${callTime.toLocaleTimeString()}</strong>
                ` : '<span class="text-muted">N/A</span>'}
            </td>
            <td>
                ${record.caller ? `<strong>${record.caller}</strong>` : '<span class="text-muted">Unknown</span>'}
            </td>
            <td>
                ${record.called_number ? `<strong>${record.called_number}</strong>` : '<span class="text-muted">Unknown</span>'}
            </td>
            <td>
                <span class="badge bg-${record.direction === 'I' ? 'success' : 'primary'}">
                    <i class="bi bi-arrow-${record.direction === 'I' ? 'down' : 'up'}-circle"></i>
                    ${record.direction === 'I' ? 'Inbound' : 'Outbound'}
                </span>
            </td>
            <td>
                <small class="text-muted">${this.getCallType(record)}</small>
            </td>
            <td>
                ${record.connected_time > 0 ? 
                    `<span class="${record.connected_time > 300 ? 'duration-long' : ''}">${duration}</span>` :
                    '<span class="text-muted">00:00:00</span>'
                }
            </td>
            <td>
                ${record.party1_device ? `<code>${record.party1_device}</code>` : '<span class="text-muted">N/A</span>'}
            </td>
            <td>
                <a href="/record/${record.id}" class="btn btn-sm btn-outline-primary" title="View Details">
                    <i class="bi bi-eye"></i>
                </a>
            </td>
        `;
        
        return row;
    }

    formatDuration(seconds) {
        if (!seconds || seconds === 0) return "00:00:00";
        
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    getCallType(record) {
        if (record.direction === 'I') {
            return record.is_internal ? 'Internal Inbound' : 'External Inbound';
        } else {
            return record.is_internal ? 'Internal Outbound' : 'External Outbound';
        }
    }

    getCurrentSearchFilters() {
        const urlParams = new URLSearchParams(window.location.search);
        return {
            direction: urlParams.get('direction'),
            is_internal: urlParams.get('is_internal'),
            date_from: urlParams.get('date_from'),
            date_to: urlParams.get('date_to'),
            caller: urlParams.get('caller'),
            called: urlParams.get('called')
        };
    }

    recordMatchesFilters(record, filters) {
        // Simple filter matching logic
        if (filters.direction && record.direction !== filters.direction) {
            return false;
        }
        
        if (filters.is_internal !== null && record.is_internal !== (filters.is_internal === '1')) {
            return false;
        }
        
        if (filters.caller && !record.caller?.includes(filters.caller)) {
            return false;
        }
        
        if (filters.called && !record.called_number?.includes(filters.called)) {
            return false;
        }
        
        // Date filtering would require more complex logic
        
        return true;
    }

    showNewRecordNotification(record) {
        const direction = record.direction === 'I' ? 'Inbound' : 'Outbound';
        const type = record.is_internal ? 'Internal' : 'External';
        const caller = record.caller || 'Unknown';
        const called = record.called_number || 'Unknown';
        
        this.showNotification(
            `New ${type} ${direction} Call: ${caller} → ${called}`,
            'info',
            5000
        );
    }

    showConnectionStatus(message, type) {
        const statusElement = document.getElementById('websocket-status');
        if (statusElement) {
            statusElement.className = `badge bg-${type}`;
            statusElement.textContent = message;
        }
    }

    showNotification(message, type = 'info', duration = 3000) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
        
        notification.innerHTML = `
            <i class="bi bi-${type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
    }

    // Public API methods
    onMessage(type, handler) {
        this.messageHandlers.set(type, handler);
    }

    onConnection(listener) {
        this.connectionListeners.add(listener);
    }

    subscribe(filters = {}) {
        if (this.isConnected) {
            this.send({
                type: 'subscribe',
                filters: filters
            });
        }
        this.subscriptions.add(filters);
    }

    unsubscribe() {
        if (this.isConnected) {
            this.send({
                type: 'unsubscribe'
            });
        }
        this.subscriptions.clear();
    }

    send(message) {
        if (this.isConnected && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
        } else {
            console.warn('Cannot send message: WebSocket not connected');
        }
    }

    ping() {
        this.send({
            type: 'ping',
            timestamp: new Date().toISOString()
        });
    }

    getStats() {
        this.send({
            type: 'get_stats'
        });
    }

    // Private methods
    resubscribe() {
        for (const filters of this.subscriptions) {
            this.subscribe(filters);
        }
    }

    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Scheduling reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${this.reconnectInterval}ms`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectInterval);
        } else {
            console.error('Max reconnection attempts reached');
            this.showNotification('WebSocket connection failed. Please refresh the page.', 'error', 10000);
        }
    }

    notifyConnectionListeners(status) {
        for (const listener of this.connectionListeners) {
            try {
                listener(status);
            } catch (error) {
                console.error('Error in connection listener:', error);
            }
        }
    }

    disconnect() {
        if (this.socket) {
            this.socket.close();
        }
    }
}

// Global WebSocket client instance
let wsClient = null;

// Initialize WebSocket client when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if WebSocket is supported
    if (typeof WebSocket !== 'undefined') {
        wsClient = new WebSocketClient();
        
        // Make it globally accessible
        window.wsClient = wsClient;
        
        // Subscribe to updates based on current page
        if (window.location.pathname === '/') {
            // Dashboard - subscribe to all updates
            wsClient.subscribe();
        } else if (window.location.pathname === '/search') {
            // Search page - subscribe with current filters
            const filters = wsClient.getCurrentSearchFilters();
            wsClient.subscribe(filters);
        }
    } else {
        console.warn('WebSocket not supported by this browser');
    }
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (wsClient) {
        wsClient.disconnect();
    }
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebSocketClient;
}