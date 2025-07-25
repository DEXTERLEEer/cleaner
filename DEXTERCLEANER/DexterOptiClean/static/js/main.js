// DEXTER PC Optimizer - Main JavaScript

class DexterOptimizer {
    constructor() {
        this.isScanning = false;
        this.selectedFiles = new Set();
        this.systemStats = {};
        this.soundEnabled = true;
        
        this.init();
    }

    init() {
        this.showSplashScreen();
        this.setupEventListeners();
        this.startSystemMonitoring();
        this.checkAdminStatus();
        this.initializeCleaningCategories();
    }

    showSplashScreen() {
        setTimeout(() => {
            document.getElementById('splash-screen').classList.add('fade-out');
            setTimeout(() => {
                document.getElementById('splash-screen').classList.add('d-none');
                document.getElementById('main-app').classList.remove('d-none');
                document.getElementById('main-app').classList.add('show');
            }, 500);
        }, 3000);
    }

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });

        // Scan button
        document.getElementById('clean-all-btn').addEventListener('click', () => this.cleanAllCategories());

        // Admin button
        document.getElementById('admin-btn').addEventListener('click', () => this.requestAdmin());

        // Clean button
        document.getElementById('clean-btn').addEventListener('click', () => this.cleanSelectedFiles());

        // File selection
        document.getElementById('select-all').addEventListener('click', () => this.selectAllFiles());
        document.getElementById('select-none').addEventListener('click', () => this.selectNoFiles());

        // Duplicate finder
        document.getElementById('find-duplicates-btn').addEventListener('click', () => this.findDuplicates());

        // Settings
        document.getElementById('sound-toggle').addEventListener('change', (e) => {
            this.soundEnabled = e.target.checked;
        });

        // Modal buttons
        document.getElementById('download-log-btn').addEventListener('click', () => this.downloadLog());

        // Window controls
        document.querySelector('.minimize-btn').addEventListener('click', () => this.minimizeWindow());
        document.querySelector('.maximize-btn').addEventListener('click', () => this.maximizeWindow());
        document.querySelector('.close-btn').addEventListener('click', () => this.closeWindow());

        // Sound effects
        document.addEventListener('click', (e) => {
            if (this.soundEnabled && (e.target.tagName === 'BUTTON' || e.target.closest('button'))) {
                this.playSound('click');
            }
        });

        // Additional scan buttons for new categories
        const scanAdvancedBtn = document.getElementById('scan-advanced-btn');
        if (scanAdvancedBtn) {
            scanAdvancedBtn.addEventListener('click', () => this.startScan('advanced'));
        }

        const scanBrowserBtn = document.getElementById('scan-browser-btn');
        if (scanBrowserBtn) {
            scanBrowserBtn.addEventListener('click', () => this.startScan('browser'));
        }

        const scanGamingBtn = document.getElementById('scan-gaming-btn');
        if (scanGamingBtn) {
            scanGamingBtn.addEventListener('click', () => this.startScan('gaming'));
        }
    }

    initializeCleaningCategories() {
        // Initialize select all buttons
        document.querySelectorAll('.select-all-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const categoryContainer = e.target.closest('.cleaning-categories');
                const checkboxes = categoryContainer.querySelectorAll('input[type="checkbox"]:not(:disabled)');
                checkboxes.forEach(checkbox => {
                    checkbox.checked = true;
                });
            });
        });

        // Add hover effects and interactive feedback
        document.querySelectorAll('.cleaning-item').forEach(item => {
            const checkbox = item.querySelector('input[type="checkbox"]');
            const label = item.querySelector('label');
            
            if (checkbox && label) {
                label.addEventListener('click', (e) => {
                    if (!checkbox.disabled) {
                        checkbox.checked = !checkbox.checked;
                    }
                    e.preventDefault();
                });
            }
        });
    }

    switchTab(tabName) {
        // Hide all tabs
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });

        // Remove active class from all nav tabs
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
        });

        // Show selected tab
        document.getElementById(`${tabName}-tab`).classList.add('active');
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        this.playSound('tab');
    }

    async startScan(category = 'basic') {
        if (this.isScanning) return;

        this.isScanning = true;
        
        // Disable all scan buttons
        const scanButtons = ['clean-all-btn', 'scan-advanced-btn', 'scan-browser-btn', 'scan-gaming-btn'];
        scanButtons.forEach(btnId => {
            const btn = document.getElementById(btnId);
            if (btn) btn.disabled = true;
        });
        
        document.getElementById('scan-progress').classList.remove('d-none');
        document.getElementById('files-list').classList.add('d-none');

        try {
            const response = await fetch('/api/start-scan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    scan_type: category
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.monitorScanProgress();
                this.playSound('scan-start');
            } else {
                this.showError('Failed to start scan: ' + result.error);
                this.resetScanUI();
            }
        } catch (error) {
            this.showError('Network error: ' + error.message);
            this.resetScanUI();
        }
    }

    async monitorScanProgress() {
        const progressInterval = setInterval(async () => {
            try {
                const response = await fetch('/api/scan-progress');
                const result = await response.json();

                if (result.success) {
                    const data = result.data;
                    
                    // Update progress bar
                    document.getElementById('progress-fill').style.width = `${data.progress}%`;
                    document.getElementById('progress-percent').textContent = `${data.progress}%`;

                    if (data.status === 'completed') {
                        clearInterval(progressInterval);
                        this.displayScanResults(data.files);
                        this.playSound('scan-complete');
                    } else if (data.status === 'error') {
                        clearInterval(progressInterval);
                        this.showError('Scan failed: ' + (data.error || 'Unknown error'));
                        this.resetScanUI();
                    }
                }
            } catch (error) {
                clearInterval(progressInterval);
                this.showError('Failed to get scan progress: ' + error.message);
                this.resetScanUI();
            }
        }, 500);
    }

    displayScanResults(files) {
        this.isScanning = false;
        document.getElementById('clean-all-btn').disabled = false;
        document.getElementById('scan-progress').classList.add('d-none');
        document.getElementById('files-list').classList.remove('d-none');

        const container = document.getElementById('files-container');
        container.innerHTML = '';

        if (files.length === 0) {
            container.innerHTML = '<p class="text-center text-muted">No files found for cleanup.</p>';
            return;
        }

        files.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <input type="checkbox" id="file-${index}" data-path="${file.path}" checked>
                <div class="file-info">
                    <div class="file-details">
                        <div class="file-path">${file.path}</div>
                        <div class="file-description">${file.description || 'Temporary file'}</div>
                    </div>
                    <div class="file-size">${this.formatFileSize(file.size)}</div>
                </div>
            `;
            container.appendChild(fileItem);

            // Add event listener for checkbox
            fileItem.querySelector('input').addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.selectedFiles.add(file.path);
                } else {
                    this.selectedFiles.delete(file.path);
                }
            });

            // Initially select all files
            this.selectedFiles.add(file.path);
        });

        // Update recovery estimate
        this.updateRecoveryEstimate();
    }

    resetScanUI() {
        this.isScanning = false;
        
        // Re-enable all scan buttons
        const scanButtons = ['clean-all-btn', 'scan-advanced-btn', 'scan-browser-btn', 'scan-gaming-btn'];
        scanButtons.forEach(btnId => {
            const btn = document.getElementById(btnId);
            if (btn) btn.disabled = false;
        });
        
        document.getElementById('scan-progress').classList.add('d-none');
        document.getElementById('progress-fill').style.width = '0%';
        document.getElementById('progress-percent').textContent = '0%';
    }

    selectAllFiles() {
        document.querySelectorAll('#files-container input[type="checkbox"]').forEach(checkbox => {
            checkbox.checked = true;
            this.selectedFiles.add(checkbox.dataset.path);
        });
        this.updateRecoveryEstimate();
    }

    selectNoFiles() {
        document.querySelectorAll('#files-container input[type="checkbox"]').forEach(checkbox => {
            checkbox.checked = false;
            this.selectedFiles.delete(checkbox.dataset.path);
        });
        this.updateRecoveryEstimate();
    }

    async cleanSelectedFiles() {
        if (this.selectedFiles.size === 0) {
            this.showError('No files selected for cleaning.');
            return;
        }

        const confirmClean = confirm(`Are you sure you want to delete ${this.selectedFiles.size} files?`);
        if (!confirmClean) return;

        document.getElementById('clean-btn').disabled = true;
        document.getElementById('clean-btn').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cleaning...';

        try {
            const response = await fetch('/api/clean-files', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    files: Array.from(this.selectedFiles)
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showCleanupResults(result.data);
                this.selectedFiles.clear();
                document.getElementById('files-list').classList.add('d-none');
                this.playSound('cleanup-complete');
            } else {
                this.showError('Cleanup failed: ' + result.error);
            }
        } catch (error) {
            this.showError('Network error: ' + error.message);
        } finally {
            document.getElementById('clean-btn').disabled = false;
            document.getElementById('clean-btn').innerHTML = '<i class="fas fa-trash-alt"></i> Clean Selected Files';
        }
    }

    async cleanAllCategories() {
        // Define all available cleaning categories
        const categories = [
            'basic',
            'browser',
            'advanced',
            'gaming',
            'temp',
            'logs',
            'cache'
        ];

        const confirmClean = confirm(`Are you sure you want to clean all categories? This will remove temporary files, browser cache, and system logs.`);
        if (!confirmClean) return;

        document.getElementById('clean-all-btn').disabled = true;
        document.getElementById('clean-all-btn').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cleaning...';
        document.getElementById('scan-progress').classList.remove('d-none');
        document.getElementById('progress-fill').style.width = '0%';
        document.getElementById('progress-percent').textContent = '0%';
        document.getElementById('progress-status').textContent = 'Cleaning all categories...';

        try {
            // Start progress animation
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += 1;
                if (progress > 95) clearInterval(progressInterval);
                document.getElementById('progress-fill').style.width = `${progress}%`;
                document.getElementById('progress-percent').textContent = `${progress}%`;
            }, 100);

            const response = await fetch('/api/clean-all', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    categories: categories
                })
            });

            const result = await response.json();
            clearInterval(progressInterval);
            
            if (result.success) {
                document.getElementById('progress-fill').style.width = '100%';
                document.getElementById('progress-percent').textContent = '100%';
                document.getElementById('progress-status').textContent = 'Cleaning complete!';
                
                setTimeout(() => {
                    document.getElementById('scan-progress').classList.add('d-none');
                    this.showCleanupResults(result.data);
                    this.playSound('cleanup-complete');
                }, 1000);
            } else {
                this.showError('Cleanup failed: ' + result.error);
                document.getElementById('scan-progress').classList.add('d-none');
            }
        } catch (error) {
            this.showError('Cleanup failed: ' + error.message);
            document.getElementById('scan-progress').classList.add('d-none');
        } finally {
            document.getElementById('clean-all-btn').disabled = false;
            document.getElementById('clean-all-btn').innerHTML = '<i class="fas fa-broom"></i> Clean All';
        }
    }

    showCleanupResults(data) {
        document.getElementById('freed-space').textContent = this.formatFileSize(data.freed_space);
        document.getElementById('files-cleaned').textContent = data.cleaned_files.length;
        
        const modal = new bootstrap.Modal(document.getElementById('resultsModal'));
        modal.show();

        // Update system stats
        this.updateSystemStats();
    }

    async requestAdmin() {
        try {
            const response = await fetch('/api/request-admin');
            const result = await response.json();

            if (result.success) {
                this.updateAdminStatus(result.data.elevated);
                this.showNotification(result.data.message);
            } else {
                this.showError('Failed to request admin privileges: ' + result.error);
            }
        } catch (error) {
            this.showError('Network error: ' + error.message);
        }
    }

    async findDuplicates() {
        const directory = document.getElementById('scan-directory').value || '/';
        document.getElementById('find-duplicates-btn').disabled = true;
        document.getElementById('find-duplicates-btn').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scanning...';

        try {
            const response = await fetch('/api/find-duplicates', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    directory: directory
                })
            });

            const result = await response.json();

            if (result.success) {
                this.displayDuplicateResults(result.data);
            } else {
                this.showError('Duplicate scan failed: ' + result.error);
            }
        } catch (error) {
            this.showError('Network error: ' + error.message);
        } finally {
            document.getElementById('find-duplicates-btn').disabled = false;
            document.getElementById('find-duplicates-btn').innerHTML = '<i class="fas fa-search"></i> Find Duplicates';
        }
    }

    displayDuplicateResults(data) {
        const container = document.getElementById('duplicates-results');
        container.classList.remove('d-none');
        
        if (data.duplicates.length === 0) {
            container.innerHTML = '<p class="text-center text-muted">No duplicate files found.</p>';
            return;
        }

        let html = `<h5>Found ${data.total_groups} duplicate groups</h5>`;
        html += `<p>Potential space savings: ${this.formatFileSize(data.potential_savings)}</p>`;
        html += '<div class="duplicate-groups">';

        data.duplicates.forEach((group, index) => {
            html += `<div class="duplicate-group">
                <h6>Group ${index + 1} (${group.files.length} files)</h6>
                <ul>`;
            
            group.files.forEach(file => {
                html += `<li>${file.path} (${this.formatFileSize(file.size)})</li>`;
            });
            
            html += '</ul></div>';
        });

        html += '</div>';
        container.innerHTML = html;
    }

    async checkAdminStatus() {
        try {
            const response = await fetch('/api/system-status');
            const result = await response.json();

            if (result.success) {
                this.updateAdminStatus(result.data.is_admin);
                this.systemStats = result.data;
                this.updateSystemDashboard();
            }
        } catch (error) {
            console.error('Failed to check admin status:', error);
        }
    }

    updateAdminStatus(isAdmin) {
        const icon = document.getElementById('admin-icon');
        const text = document.getElementById('admin-status-text');
        const indicator = document.querySelector('.status-indicator');

        if (isAdmin) {
            indicator.classList.add('admin');
            text.textContent = 'Administrator privileges';
            icon.className = 'fas fa-shield-alt';
        } else {
            indicator.classList.add('no-admin');
            text.textContent = 'Standard user privileges';
            icon.className = 'fas fa-shield-alt';
        }
    }

    startSystemMonitoring() {
        // Update system stats every 5 seconds
        setInterval(() => {
            this.updateSystemStats();
        }, 5000);

        // Initial update
        this.updateSystemStats();
    }

    async updateSystemStats() {
        try {
            const response = await fetch('/api/system-status');
            const result = await response.json();

            if (result.success) {
                this.systemStats = result.data;
                this.updateSystemDashboard();
            }
        } catch (error) {
            console.error('Failed to update system stats:', error);
        }
    }

    updateSystemDashboard() {
        const stats = this.systemStats;

        // Update CPU gauge
        this.updateCircularGauge('cpu-gauge', stats.cpu_usage || 0);
        document.getElementById('cpu-value').textContent = `${Math.round(stats.cpu_usage || 0)}%`;

        // Update RAM gauge
        this.updateCircularGauge('ram-gauge', stats.memory_usage || 0);
        document.getElementById('ram-value').textContent = `${Math.round(stats.memory_usage || 0)}%`;

        // Update storage bars
        const freeSpacePercent = ((stats.free_space || 0) / (stats.total_space || 1)) * 100;
        document.getElementById('free-space-bar').style.width = `${freeSpacePercent}%`;
        document.getElementById('free-space-text').textContent = `${this.formatFileSize(stats.free_space || 0)} Free`;
    }

    updateCircularGauge(gaugeId, percentage) {
        const gauge = document.getElementById(gaugeId);
        const degrees = (percentage / 100) * 360;
        
        if (percentage <= 50) {
            gauge.style.background = `conic-gradient(var(--accent-purple) ${degrees}deg, var(--border-color) ${degrees}deg)`;
        } else {
            gauge.style.background = `conic-gradient(var(--accent-purple) ${degrees}deg, var(--border-color) ${degrees}deg)`;
        }
    }

    updateRecoveryEstimate() {
        // Calculate potential recovery space based on selected files
        let totalSize = 0;
        document.querySelectorAll('#files-container input[type="checkbox"]:checked').forEach(checkbox => {
            // This would need actual file size data
            totalSize += 1024 * 1024; // Placeholder: 1MB per file
        });

        const recoveryPercent = Math.min((totalSize / (this.systemStats.total_space || 1)) * 100, 20);
        document.getElementById('recovery-bar').style.width = `${recoveryPercent}%`;
        document.getElementById('recovery-text').textContent = `+${this.formatFileSize(totalSize)} Recoverable`;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    showError(message) {
        // Create error notification
        const notification = document.createElement('div');
        notification.className = 'alert alert-danger position-fixed';
        notification.style.cssText = 'top: 80px; right: 20px; z-index: 9999; max-width: 400px;';
        notification.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            ${message}
            <button type="button" class="btn-close ms-2" onclick="this.parentElement.remove()"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);

        this.playSound('error');
    }

    showNotification(message) {
        // Create success notification
        const notification = document.createElement('div');
        notification.className = 'alert alert-success position-fixed';
        notification.style.cssText = 'top: 80px; right: 20px; z-index: 9999; max-width: 400px;';
        notification.innerHTML = `
            <i class="fas fa-check-circle"></i>
            ${message}
            <button type="button" class="btn-close ms-2" onclick="this.parentElement.remove()"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 3000);

        this.playSound('success');
    }

    playSound(type) {
        if (!this.soundEnabled) return;
        
        // Create audio context for sound effects
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        const sounds = {
            click: { frequency: 800, duration: 0.1 },
            tab: { frequency: 600, duration: 0.15 },
            'scan-start': { frequency: 440, duration: 0.3 },
            'scan-complete': { frequency: 880, duration: 0.5 },
            'cleanup-complete': { frequency: 1000, duration: 0.7 },
            success: { frequency: 800, duration: 0.4 },
            error: { frequency: 200, duration: 0.6 }
        };

        const sound = sounds[type];
        if (!sound) return;

        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.setValueAtTime(sound.frequency, audioContext.currentTime);
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + sound.duration);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + sound.duration);
    }

    async downloadLog() {
        try {
            const response = await fetch('/api/download-log');
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'dexter_cleanup_log.txt';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else {
                this.showError('No log file available for download.');
            }
        } catch (error) {
            this.showError('Failed to download log: ' + error.message);
        }
    }

    minimizeWindow() {
        // Simulate minimize animation
        document.querySelector('.main-app').style.transform = 'scale(0.8)';
        setTimeout(() => {
            document.querySelector('.main-app').style.transform = 'scale(1)';
        }, 200);
        this.showNotification('Window minimized (simulated)');
    }

    maximizeWindow() {
        // Toggle fullscreen-like behavior
        if (document.body.style.overflow === 'hidden') {
            document.body.style.overflow = '';
            this.showNotification('Window restored');
        } else {
            document.body.style.overflow = 'hidden';
            this.showNotification('Window maximized');
        }
    }

    closeWindow() {
        const confirmClose = confirm('Are you sure you want to exit DEXTER PC Optimizer?');
        if (confirmClose) {
            // Simulate close with fade out
            document.querySelector('.main-app').style.opacity = '0';
            setTimeout(() => {
                document.body.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100vh; background: #121212; color: white;"><h2>DEXTER PC Optimizer Closed</h2></div>';
            }, 500);
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dexterApp = new DexterOptimizer();
});

// Handle window resize for responsive design
window.addEventListener('resize', () => {
    // Update layout if needed
    if (window.dexterApp) {
        window.dexterApp.updateSystemDashboard();
    }
});

// Handle beforeunload to save state
window.addEventListener('beforeunload', (e) => {
    if (window.dexterApp && window.dexterApp.isScanning) {
        e.preventDefault();
        e.returnValue = 'A scan is currently in progress. Are you sure you want to leave?';
    }
});
