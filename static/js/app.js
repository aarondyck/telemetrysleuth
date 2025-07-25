/**
 * Telemetry Sleuth - Frontend JavaScript
 * Handles dynamic interactions and real-time updates
 */

class TelemetrySleuth {
    constructor() {
        this.init();
        this.setupEventListeners();
        this.startAutoRefresh();
    }

    init() {
        console.log('Telemetry Sleuth initialized');
        this.updateCurrentTime();
        this.initializeTooltips();
    }

    setupEventListeners() {
        // Search form enhancements
        const searchForm = document.querySelector('form[action*="search"]');
        if (searchForm) {
            this.enhanceSearchForm(searchForm);
        }

        // Stats card click handlers
        document.querySelectorAll('.stats-card').forEach(card => {
            card.addEventListener('click', this.handleStatsCardClick.bind(this));
        });

        // Table row hover effects
        document.querySelectorAll('.table tbody tr').forEach(row => {
            row.addEventListener('mouseenter', this.handleRowHover);
            row.addEventListener('mouseleave', this.handleRowLeave);
        });
    }

    enhanceSearchForm(form) {
        // Add loading state to search button
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            form.addEventListener('submit', () => {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Searching...';
            });
        }

        // Auto-submit on filter changes (with debounce)
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            let timeout;
            input.addEventListener('change', () => {
                if (input.type !== 'text') {
                    clearTimeout(timeout);
                    timeout = setTimeout(() => {
                        // Only auto-submit for select elements and date inputs
                        if (input.tagName === 'SELECT' || input.type === 'date') {
                            this.submitFormWithLoading(form);
                        }
                    }, 500);
                }
            });
        });
    }

    handleStatsCardClick(event) {
        const card = event.currentTarget;
        const cardTitle = card.querySelector('p').textContent.toLowerCase();
        
        // Navigate to search with appropriate filters
        let searchParams = new URLSearchParams();
        
        if (cardTitle.includes('inbound')) {
            searchParams.set('direction', 'I');
        } else if (cardTitle.includes('outbound')) {
            searchParams.set('direction', 'O');
        } else if (cardTitle.includes('internal')) {
            searchParams.set('is_internal', '1');
        } else if (cardTitle.includes('external')) {
            searchParams.set('is_internal', '0');
        }

        if (cardTitle.includes('today')) {
            const today = new Date().toISOString().split('T')[0];
            searchParams.set('date_from', today);
            searchParams.set('date_to', today);
        }

        const url = '/search?' + searchParams.toString();
        window.location.href = url;
    }

    handleRowHover(event) {
        event.currentTarget.style.transform = 'scale(1.01)';
        event.currentTarget.style.transition = 'transform 0.2s ease';
    }

    handleRowLeave(event) {
        event.currentTarget.style.transform = 'scale(1)';
    }

    updateCurrentTime() {
        const timeElement = document.getElementById('current-time');
        if (timeElement) {
            const now = new Date();
            const timeString = now.getFullYear() + '-' + 
                             String(now.getMonth() + 1).padStart(2, '0') + '-' + 
                             String(now.getDate()).padStart(2, '0') + ' ' +
                             String(now.getHours()).padStart(2, '0') + ':' + 
                             String(now.getMinutes()).padStart(2, '0') + ':' + 
                             String(now.getSeconds()).padStart(2, '0');
            
            timeElement.textContent = timeString;
        }
    }

    startAutoRefresh() {
        // Update time every second
        setInterval(() => {
            this.updateCurrentTime();
        }, 1000);

        // Auto-refresh dashboard stats every 30 seconds (only on dashboard)
        if (window.location.pathname === '/') {
            setInterval(() => {
                this.refreshDashboardStats();
            }, 30000);
        }

        // Auto-refresh search results every 60 seconds (only on search page)
        if (window.location.pathname === '/search') {
            setInterval(() => {
                this.refreshSearchResults();
            }, 60000);
        }
    }

    async refreshDashboardStats() {
        try {
            const response = await fetch('/api/stats');
            if (response.ok) {
                const data = await response.json();
                this.updateStatsDisplay(data);
            }
        } catch (error) {
            console.error('Error refreshing stats:', error);
        }
    }

    updateStatsDisplay(stats) {
        const statsElements = {
            'total-records': stats.total_records,
            'today-records': stats.today_records,
            'inbound-today': stats.inbound_today,
            'outbound-today': stats.outbound_today,
            'internal-today': stats.internal_today,
            'external-today': stats.external_today,
            'avg-duration': stats.avg_duration.toFixed(1) + 's'
        };

        for (const [id, value] of Object.entries(statsElements)) {
            const element = document.getElementById(id);
            if (element) {
                // Add animation effect
                element.style.transition = 'all 0.3s ease';
                element.style.transform = 'scale(1.1)';
                element.textContent = value;
                
                setTimeout(() => {
                    element.style.transform = 'scale(1)';
                }, 300);
            }
        }
    }

    async refreshSearchResults() {
        const currentUrl = new URL(window.location);
        if (currentUrl.searchParams.toString()) {
            // Only refresh if there are active search parameters
            try {
                const response = await fetch(currentUrl.toString(), {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                
                if (response.ok) {
                    // You could update just the table content here
                    // For now, we'll just show a subtle indicator that data is fresh
                    this.showRefreshIndicator();
                }
            } catch (error) {
                console.error('Error refreshing search results:', error);
            }
        }
    }

    showRefreshIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'alert alert-info alert-dismissible fade show position-fixed';
        indicator.style.top = '20px';
        indicator.style.right = '20px';
        indicator.style.zIndex = '9999';
        indicator.innerHTML = `
            <i class="bi bi-check-circle"></i> Data refreshed
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(indicator);
        
        setTimeout(() => {
            if (indicator.parentNode) {
                indicator.remove();
            }
        }, 3000);
    }

    submitFormWithLoading(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.click();
        }
    }

    initializeTooltips() {
        // Initialize Bootstrap tooltips if available
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
            const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
        }
    }

    // Utility function to format duration
    static formatDuration(seconds) {
        if (!seconds || seconds === 0) return "00:00:00";
        
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    // Utility function to format phone numbers
    static formatPhoneNumber(number) {
        if (!number) return '';
        
        // Simple US phone number formatting
        const cleaned = number.replace(/\D/g, '');
        const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
        
        if (match) {
            return `(${match[1]}) ${match[2]}-${match[3]}`;
        }
        
        return number;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.telemetrySleuth = new TelemetrySleuth();
});

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TelemetrySleuth;
}