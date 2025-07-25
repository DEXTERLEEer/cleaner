// DEXTER PC Optimizer - Main JavaScript

// Global variables
let systemStats = {};
let scanResults = [];
let isAdmin = false;
let isAdminRestart = false;
let currentTheme = 'dark';
let currentAccent = 'purple';

// DOM Elements
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initApp();
    
    // Set up event listeners
    setupEventListeners();
    
    // Start system monitoring
    startSystemMonitoring();
    
    // Load user settings
    loadUserSettings();
});

// Initialize application
function initApp() {
    // Show splash screen for 2 seconds
    setTimeout(() => {
        document.getElementById('splash-screen').classList.add('fade-out');
        setTimeout(() => {
            document.getElementById('splash-screen').classList.add('d-none');
            document.getElementById('main-app').classList.remove('d-none');
        }, 500);
    }, 2000);
    
    // Initialize Bootstrap components
    initBootstrapComponents();
}

// Initialize Bootstrap components
function initBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize modals
    const resultsModal = new bootstrap.Modal(document.getElementById('results-modal'));
    const adminModal = new bootstrap.Modal(document.getElementById('admin-modal'));
}

// Set up event listeners
function setupEventListeners() {
    // Tab navigation
    const navTabs = document.querySelectorAll('.nav-tab');
    navTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            navTabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Hide all tab panes
            document.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('active');
            });
            
            // Show the selected tab pane
            const tabId = this.getAttribute('data-tab');
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });
    
    // Select all buttons
    document.querySelectorAll('.select-all-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const parentCategory = this.closest('.cleaning-categories');
            const checkboxes = parentCategory.querySelectorAll('input[type="checkbox"]');
            
            // Check if all are already checked
            const allChecked = Array.from(checkboxes).every(cb => cb.checked);
            
            // Toggle all checkboxes
            checkboxes.forEach(cb => {
                cb.checked = !allChecked;
            });
        });
    });
    
    // Clean buttons
    document.getElementById('clean-all-btn').addEventListener('click', function() {
        cleanSelectedCategories('basic');
    });
    
    document.getElementById('clean-advanced-btn').addEventListener('click', function() {
        cleanSelectedCategories('advanced');
    });
    
    document.getElementById('clean-browser-btn').addEventListener('click', function() {
        cleanSelectedCategories('browser');
    });
    
    document.getElementById('clean-gaming-btn').addEventListener('click', function() {
        cleanSelectedCategories('gaming');
    });
    
    // Admin button
    document.getElementById('admin-btn').addEventListener('click', function() {
        const adminModal = new bootstrap.Modal(document.getElementById('admin-modal'));
        adminModal.show();
    });
    
    // Confirm admin button
    document.getElementById('confirm-admin-btn').addEventListener('click', function() {
        requestAdminPrivileges();
    });
    
    // Find duplicates button
    document.getElementById('find-duplicates-btn').addEventListener('click', function() {
        findDuplicateFiles();
    });
    
    // Theme switcher
    if (document.getElementById('theme-dark')) {
        document.getElementById('theme-dark').addEventListener('click', function() {
            setTheme('dark');
        });
    }
    
    if (document.getElementById('theme-light')) {
        document.getElementById('theme-light').addEventListener('click', function() {
            setTheme('light');
        });
    }
    
    // Accent color switcher
    document.querySelectorAll('.accent-option').forEach(option => {
        option.addEventListener('click', function() {
            const accent = this.getAttribute('data-accent');
            setAccentColor(accent);
        });
    });
    
    // Save settings button
    if (document.getElementById('save-settings-btn')) {
        document.getElementById('save-settings-btn').addEventListener('click', function() {
            saveUserSettings();
        });
    }
    
    // Window control buttons
    document.querySelector('.minimize-btn').addEventListener('click', function() {
        // Minimize window functionality would go here in Electron
        console.log('Minimize window');
    });
    
    document.querySelector('.maximize-btn').addEventListener('click', function() {
        // Maximize window functionality would go here in Electron
        console.log('Maximize window');
    });
    
    document.querySelector('.close-btn').addEventListener('click', function() {
        // Close window functionality would go here in Electron
        console.log('Close window');
    });
}

// Start system monitoring
function startSystemMonitoring() {
    // Initial check
    checkSystemStatus();
    
    // Set up interval for regular updates
    setInterval(checkSystemStatus, 5000);
}

// Check system status
function checkSystemStatus() {
    fetch('/api/system-status')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateSystemStats(data.data);
            }
        })
        .catch(error => console.error('Error fetching system status:', error));
}

// Update system statistics display
function updateSystemStats(stats) {
    systemStats = stats;
    
    // Update CPU gauge
    const cpuValue = document.getElementById('cpu-value');
    const cpuGauge = document.getElementById('cpu-gauge');
    cpuValue.textContent = `${Math.round(stats.cpu_usage)}%`;
    cpuGauge.style.setProperty('--gauge-value', `${Math.min(100, stats.cpu_usage)}%`);
    
    // Update RAM gauge
    const ramValue = document.getElementById('ram-value');
    const ramGauge = document.getElementById('ram-gauge');
    ramValue.textContent = `${Math.round(stats.memory_usage)}%`;
    ramGauge.style.setProperty('--gauge-value', `${Math.min(100, stats.memory_usage)}%`);
    
    // Update storage bars
    const freeSpaceGB = (stats.free_space / (1024 * 1024 * 1024)).toFixed(1);
    const totalSpaceGB = (stats.total_space / (1024 * 1024 * 1024)).toFixed(1);
    const freeSpacePercent = (stats.free_space / stats.total_space * 100).toFixed(1);
    
    document.getElementById('free-space-bar').style.width = `${freeSpacePercent}%`;
    document.getElementById('free-space-text').textContent = `${freeSpaceGB} GB Free of ${totalSpaceGB} GB`;
    
    // Update admin status
    isAdmin = stats.is_admin;
    isAdminRestart = stats.is_admin_restart || false;
    
    const adminIcon = document.getElementById('admin-icon');
    const adminStatusText = document.getElementById('admin-status-text');
    
    if (isAdmin) {
        adminIcon.className = 'fas fa-shield-alt admin-active';
        adminStatusText.textContent = 'Admin privileges active';
        adminStatusText.className = 'admin-active';
        
        // Hide the "Run as Admin" button since we're already admin
        document.getElementById('admin-btn').style.display = 'none';
    } else {
        adminIcon.className = 'fas fa-shield-alt';
        adminStatusText.textContent = 'Standard privileges';
        adminStatusText.className = '';
    }
    
    // If this is an admin restart, show notification
    if (isAdminRestart) {
        showToast('Admin privileges granted', 'Application is now running with administrator privileges.');
        isAdminRestart = false; // Reset to avoid showing multiple times
    }
}

// Clean selected categories
function cleanSelectedCategories(tabName) {
    // Show progress bar
    const scanProgress = document.getElementById('scan-progress');
    scanProgress.classList.remove('d-none');
    
    // Get selected categories
    const categories = [];
    
    if (tabName === 'basic') {
        document.querySelectorAll('#basic-tab input[type="checkbox"]:checked').forEach(cb => {
            categories.push(cb.id);
        });
    } else if (tabName === 'advanced') {
        document.querySelectorAll('#advanced-tab input[type="checkbox"]:checked').forEach(cb => {
            categories.push(cb.id);
        });
    } else if (tabName === 'browser') {
        document.querySelectorAll('#browser-tab input[type="checkbox"]:checked').forEach(cb => {
            categories.push(cb.id);
        });
    } else if (tabName === 'gaming') {
        document.querySelectorAll('#gaming-tab input[type="checkbox"]:checked').forEach(cb => {
            categories.push(cb.id);
        });
    }
    
    // Check if any categories are selected
    if (categories.length === 0) {
        alert('Please select at least one category to clean.');
        scanProgress.classList.add('d-none');
        return;
    }
    
    // Update progress text
    document.getElementById('progress-text').textContent = 'Scanning... 0%';
    document.getElementById('progress-fill').style.width = '0%';
    
    // Start cleaning
    fetch('/api/clean-all', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ categories })
    })
    .then(response => response.json())
    .then(data => {
        // Hide progress bar
        scanProgress.classList.add('d-none');
        
        if (data.success) {
            // Show results
            showCleaningResults(data.data);
        } else {
            // Show error
            showError(data.error);
        }
        
        // Refresh system status
        checkSystemStatus();
    })
    .catch(error => {
        console.error('Error cleaning files:', error);
        scanProgress.classList.add('d-none');
        showError('An error occurred while cleaning files.');
    });
    
    // Simulate progress updates
    simulateProgressUpdates();
}

// Simulate progress updates
function simulateProgressUpdates() {
    let progress = 0;
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    
    const interval = setInterval(() => {
        progress += Math.random() * 5;
        if (progress > 100) {
            progress = 100;
            clearInterval(interval);
        }
        
        progressFill.style.width = `${progress}%`;
        progressText.textContent = `Scanning... ${Math.round(progress)}%`;
    }, 200);
}

// Show cleaning results
function showCleaningResults(results) {
    // Update results modal
    document.getElementById('files-cleaned').textContent = results.cleaned_files.length;
    
    // Format freed space
    const freedSpace = formatBytes(results.freed_space);
    document.getElementById('space-freed').textContent = freedSpace;
    
    // Show errors if any
    const errorCount = results.errors.length;
    document.getElementById('error-count').textContent = errorCount;
    
    if (errorCount > 0) {
        const errorList = document.getElementById('error-list');
        errorList.innerHTML = '';
        
        results.errors.forEach(error => {
            const li = document.createElement('li');
            li.textContent = error;
            errorList.appendChild(li);
        });
        
        document.getElementById('error-details').classList.remove('d-none');
    } else {
        document.getElementById('error-details').classList.add('d-none');
    }
    
    // Show modal
    const resultsModal = new bootstrap.Modal(document.getElementById('results-modal'));
    resultsModal.show();
    
    // Update recovery bar
    const recoveryBar = document.getElementById('recovery-bar');
    const recoveryText = document.getElementById('recovery-text');
    
    const freedSpaceGB = results.freed_space / (1024 * 1024 * 1024);
    const totalSpaceGB = systemStats.total_space / (1024 * 1024 * 1024);
    const recoveryPercent = (freedSpaceGB / totalSpaceGB) * 100;
    
    recoveryBar.style.width = `${Math.min(100, recoveryPercent)}%`;
    recoveryText.textContent = `+${freedSpaceGB.toFixed(1)} GB Recovered`;
}

// Show error
function showError(message) {
    alert(`Error: ${message}`);
}

// Format bytes to human-readable format
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Request admin privileges
function requestAdminPrivileges() {
    fetch('/api/request-admin')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Close the modal
                const adminModal = bootstrap.Modal.getInstance(document.getElementById('admin-modal'));
                adminModal.hide();
                
                // Show message
                if (data.data.elevated) {
                    showToast('Admin Request Sent', 'Application is restarting with administrator privileges...');
                } else {
                    showError('Failed to elevate privileges. Please try running the application as administrator manually.');
                }
            } else {
                showError(data.error || 'Failed to request admin privileges');
            }
        })
        .catch(error => {
            console.error('Error requesting admin privileges:', error);
            showError('An error occurred while requesting admin privileges.');
        });
}

// Find duplicate files
function findDuplicateFiles() {
    const directoryInput = document.getElementById('directory-input');
    const directory = directoryInput.value.trim();
    
    if (!directory) {
        showError('Please enter a directory to scan.');
        return;
    }
    
    // Show progress
    const findDuplicatesBtn = document.getElementById('find-duplicates-btn');
    findDuplicatesBtn.disabled = true;
    findDuplicatesBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scanning...';
    
    // Start scan
    fetch('/api/find-duplicates', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ directory })
    })
    .then(response => response.json())
    .then(data => {
        findDuplicatesBtn.disabled = false;
        findDuplicatesBtn.innerHTML = '<i class="fas fa-search"></i> Find Duplicate Files';
        
        if (data.success) {
            showDuplicateResults(data.data);
        } else {
            showError(data.error);
        }
    })
    .catch(error => {
        console.error('Error finding duplicates:', error);
        findDuplicatesBtn.disabled = false;
        findDuplicatesBtn.innerHTML = '<i class="fas fa-search"></i> Find Duplicate Files';
        showError('An error occurred while scanning for duplicates.');
    });
}

// Show duplicate results
function showDuplicateResults(results) {
    const duplicateResults = document.getElementById('duplicate-results');
    duplicateResults.classList.remove('d-none');
    
    // Update summary
    document.getElementById('duplicate-groups').textContent = results.total_groups;
    
    let totalFiles = 0;
    results.duplicates.forEach(group => {
        totalFiles += group.files.length;
    });
    
    document.getElementById('duplicate-files').textContent = totalFiles;
    document.getElementById('potential-savings').textContent = formatBytes(results.potential_savings);
    
    // Generate duplicate list
    const duplicateList = document.getElementById('duplicate-list');
    duplicateList.innerHTML = '';
    
    results.duplicates.forEach((group, index) => {
        const groupDiv = document.createElement('div');
        groupDiv.className = 'duplicate-group';
        
        const groupHeader = document.createElement('div');
        groupHeader.className = 'group-header';
        groupHeader.innerHTML = `
            <div class="group-title">Group #${index + 1} - ${formatBytes(group.size)} × ${group.files.length} files</div>
            <div class="group-actions">
                <button class="btn btn-sm btn-outline-primary toggle-group">
                    <i class="fas fa-chevron-down"></i>
                </button>
            </div>
        `;
        
        const groupFiles = document.createElement('div');
        groupFiles.className = 'group-files';
        
        group.files.forEach((file, fileIndex) => {
            const fileDiv = document.createElement('div');
            fileDiv.className = 'duplicate-file';
            
            const isFirst = fileIndex === 0;
            
            fileDiv.innerHTML = `
                <div class="file-select">
                    <input type="checkbox" id="file-${index}-${fileIndex}" ${isFirst ? '' : 'checked'}>
                </div>
                <div class="file-info">
                    <div class="file-path">${file.path}</div>
                    <div class="file-details">
                        <span class="file-size">${formatBytes(file.size)}</span>
                        <span class="file-date">${new Date(file.last_modified * 1000).toLocaleString()}</span>
                    </div>
                </div>
            `;
            
            groupFiles.appendChild(fileDiv);
        });
        
        groupDiv.appendChild(groupHeader);
        groupDiv.appendChild(groupFiles);
        duplicateList.appendChild(groupDiv);
        
        // Add toggle functionality
        groupHeader.querySelector('.toggle-group').addEventListener('click', function() {
            const icon = this.querySelector('i');
            if (icon.classList.contains('fa-chevron-down')) {
                icon.classList.replace('fa-chevron-down', 'fa-chevron-up');
                groupFiles.style.display = 'block';
            } else {
                icon.classList.replace('fa-chevron-up', 'fa-chevron-down');
                groupFiles.style.display = 'none';
            }
        });
    });
}

// Show toast notification
function showToast(title, message) {
    // Create toast element
    const toastEl = document.createElement('div');
    toastEl.className = 'toast-notification';
    toastEl.innerHTML = `
        <div class="toast-header">
            <i class="fas fa-info-circle me-2"></i>
            <strong>${title}</strong>
            <button type="button" class="btn-close ms-auto"></button>
        </div>
        <div class="toast-body">${message}</div>
    `;
    
    // Add to document
    document.body.appendChild(toastEl);
    
    // Show toast
    setTimeout(() => {
        toastEl.classList.add('show');
        
        // Auto hide after 5 seconds
        setTimeout(() => {
            toastEl.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(toastEl);
            }, 300);
        }, 5000);
    }, 100);
    
    // Close button functionality
    const closeBtn = toastEl.querySelector('.btn-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            toastEl.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(toastEl);
            }, 300);
        });
    }
}

// Set theme
function setTheme(theme) {
    currentTheme = theme;
    
    // Update body class
    if (theme === 'light') {
        document.body.classList.add('light-theme');
    } else {
        document.body.classList.remove('light-theme');
    }
    
    // Update theme selector
    document.querySelectorAll('.theme-option').forEach(option => {
        option.classList.remove('active');
    });
    
    const selectedTheme = document.getElementById(`theme-${theme}`);
    if (selectedTheme) {
        selectedTheme.classList.add('active');
    }
    
    // Save settings
    saveUserSettings();
}

// Set accent color
function setAccentColor(accent) {
    currentAccent = accent;
    
    // Update accent color
    document.documentElement.style.setProperty('--primary-color', getAccentColorValue(accent));
    
    // Update accent selector
    document.querySelectorAll('.accent-option').forEach(option => {
        option.classList.remove('active');
    });
    
    const selectedAccent = document.querySelector(`.accent-${accent}`);
    if (selectedAccent) {
        selectedAccent.classList.add('active');
    }
    
    // Save settings
    saveUserSettings();
}

// Get accent color value
function getAccentColorValue(accent) {
    const accentColors = {
        'purple': '#9c27b0',
        'blue': '#4a6cf7',
        'green': '#28a745',
        'orange': '#fd7e14',
        'red': '#dc3545'
    };
    
    return accentColors[accent] || accentColors['purple'];
}

// Load user settings
function loadUserSettings() {
    fetch('/api/load-settings')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const settings = data.data;
                
                // Apply theme
                setTheme(settings.theme);
                
                // Apply accent color
                setAccentColor(settings.accent_color);
                
                // Apply other settings
                if (document.getElementById('start-with-windows')) {
                    document.getElementById('start-with-windows').checked = settings.start_with_windows;
                }
                
                if (document.getElementById('run-as-admin')) {
                    document.getElementById('run-as-admin').checked = settings.run_as_admin;
                }
                
                if (document.getElementById('minimize-to-tray')) {
                    document.getElementById('minimize-to-tray').checked = settings.minimize_to_tray;
                }
                
                if (document.getElementById('create-backup')) {
                    document.getElementById('create-backup').checked = settings.create_backup;
                }
                
                if (document.getElementById('show-confirmation')) {
                    document.getElementById('show-confirmation').checked = settings.show_confirmation;
                }
                
                if (document.getElementById('schedule-cleaning')) {
                    document.getElementById('schedule-cleaning').value = settings.schedule_cleaning;
                }
            }
        })
        .catch(error => {
            console.error('Error loading settings:', error);
        });
}

// Save user settings
function saveUserSettings() {
    const settings = {
        theme: currentTheme,
        accent_color: currentAccent,
        start_with_windows: document.getElementById('start-with-windows')?.checked || false,
        run_as_admin: document.getElementById('run-as-admin')?.checked || false,
        minimize_to_tray: document.getElementById('minimize-to-tray')?.checked || true,
        create_backup: document.getElementById('create-backup')?.checked || true,
        show_confirmation: document.getElementById('show-confirmation')?.checked || true,
        schedule_cleaning: document.getElementById('schedule-cleaning')?.value || 'never'
    };
    
    fetch('/api/save-settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ settings })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Settings Saved', 'Your settings have been saved successfully.');
        } else {
            showError(data.error || 'Failed to save settings.');
        }
    })
    .catch(error => {
        console.error('Error saving settings:', error);
        showError('An error occurred while saving settings.');
    });
}