// TAK LDAP Admin - Custom JavaScript

// Global variables
let csrfToken = '';

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Get CSRF token
    const csrfMeta = document.querySelector('meta[name=csrf-token]');
    if (csrfMeta) {
        csrfToken = csrfMeta.getAttribute('content');
    }
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize auto-refresh for dashboard
    if (window.location.pathname === '/') {
        startAutoRefresh();
    }
    
    // Add loading states to forms
    initializeFormLoading();
    
    // Initialize keyboard shortcuts
    initializeKeyboardShortcuts();
    
    console.log('TAK LDAP Admin initialized');
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Auto-refresh dashboard stats
function startAutoRefresh() {
    setInterval(function() {
        refreshDashboardStats();
    }, 30000); // Refresh every 30 seconds
}

function refreshDashboardStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            updateStatsCards(data);
        })
        .catch(error => {
            console.error('Error refreshing stats:', error);
        });
}

function updateStatsCards(stats) {
    // Update user count
    const userCard = document.querySelector('.card.bg-primary .card-title');
    if (userCard) {
        userCard.textContent = stats.users;
    }
    
    // Update group count
    const groupCard = document.querySelector('.card.bg-success .card-title');
    if (groupCard) {
        groupCard.textContent = stats.groups;
    }
    
    // Update status
    const statusCard = document.querySelector('.card:nth-child(3) .card-title');
    if (statusCard) {
        const statusIcon = stats.status === 'connected' ? 
            '<i class="fas fa-check-circle"></i> Online' :
            '<i class="fas fa-exclamation-triangle"></i> Offline';
        statusCard.innerHTML = statusIcon;
    }
}

// Add loading states to forms
function initializeFormLoading() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                addLoadingState(submitBtn);
            }
        });
    });
}

function addLoadingState(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    button.disabled = true;
    
    // Store original text for restoration
    button.dataset.originalText = originalText;
}

function removeLoadingState(button) {
    if (button.dataset.originalText) {
        button.innerHTML = button.dataset.originalText;
        button.disabled = false;
        delete button.dataset.originalText;
    }
}

// Keyboard shortcuts
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search (if implemented)
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modal = bootstrap.Modal.getInstance(openModal);
                if (modal) {
                    modal.hide();
                }
            }
        }
    });
}

// Utility functions
function showNotification(message, type = 'info', duration = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        <i class="fas fa-${getIconForType(type)}"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, duration);
    
    return alertDiv;
}

function getIconForType(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle',
        'primary': 'info-circle',
        'secondary': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// API helper functions
function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    };
    
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    return fetch(url, mergedOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

// Table utilities
function sortTable(table, column, direction = 'asc') {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aVal = a.cells[column].textContent.trim();
        const bVal = b.cells[column].textContent.trim();
        
        if (direction === 'asc') {
            return aVal.localeCompare(bVal);
        } else {
            return bVal.localeCompare(aVal);
        }
    });
    
    rows.forEach(row => tbody.appendChild(row));
}

function filterTable(table, searchTerm) {
    const tbody = table.querySelector('tbody');
    const rows = tbody.querySelectorAll('tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const matches = text.includes(searchTerm.toLowerCase());
        row.style.display = matches ? '' : 'none';
    });
}

// Form validation helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    return password.length >= 6;
}

function validateUsername(username) {
    const re = /^[a-zA-Z0-9_-]{3,50}$/;
    return re.test(username);
}

// Export functions for global use
window.TAKAdmin = {
    showNotification,
    confirmAction,
    formatDate,
    debounce,
    apiRequest,
    sortTable,
    filterTable,
    validateEmail,
    validatePassword,
    validateUsername,
    addLoadingState,
    removeLoadingState
};

console.log('TAK LDAP Admin JavaScript loaded');
