from flask import Flask, render_template, jsonify, request, send_file
import os
import json
import threading
import time
import sys
from datetime import datetime
from core.cleaner import PCCleaner
from core.system_monitor import SystemMonitor
from core.admin_utils import AdminUtils
from core.duplicate_finder import DuplicateFinder

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dexter_pc_optimizer_secret_key')

# Global variables for state management
scan_progress = {'progress': 0, 'status': 'idle', 'files': []}
system_stats = {}
cleaner = PCCleaner()
monitor = SystemMonitor()
admin_utils = AdminUtils()
duplicate_finder = DuplicateFinder()

# Flag to track if this is an admin restart
is_admin_restart = "--admin-restart" in sys.argv

@app.route('/')
def index():
    """Main application page"""
    # Check if this is an admin restart
    admin_restart = request.args.get('admin_restart', 'false')
    return render_template('index.html', admin_restart=admin_restart)

@app.route('/api/system-status')
def get_system_status():
    """Get current system status and statistics"""
    try:
        stats = monitor.get_system_stats()
        admin_status = admin_utils.check_admin_privileges()
        
        return jsonify({
            'success': True,
            'data': {
                'cpu_usage': stats['cpu_usage'],
                'memory_usage': stats['memory_usage'],
                'disk_usage': stats['disk_usage'],
                'free_space': stats['free_space'],
                'total_space': stats['total_space'],
                'is_admin': admin_status,
                'temperature': stats.get('temperature', None),
                'is_admin_restart': is_admin_restart
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/start-scan', methods=['POST'])
def start_scan():
    """Start system scan for cleanup candidates"""
    global scan_progress
    
    try:
        scan_type = request.json.get('scan_type', 'basic')
        
        if scan_progress['status'] == 'scanning':
            return jsonify({'success': False, 'error': 'Scan already in progress'})
        
        # Reset scan progress
        scan_progress = {'progress': 0, 'status': 'scanning', 'files': []}
        
        # Start scan in background thread
        scan_thread = threading.Thread(target=perform_scan, args=(scan_type,))
        scan_thread.daemon = True
        scan_thread.start()
        
        return jsonify({'success': True, 'message': 'Scan started'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/clean-all', methods=['POST'])
def clean_all():
    """Clean all files from selected categories"""
    try:
        categories = request.json.get('categories', [])
        
        if not categories:
            return jsonify({'success': False, 'error': 'No categories selected'})
        
        all_files = []
        category_map = {
            # Basic cleaning
            'temp-files': 'basic',
            'temp-folder': 'basic',
            'browser-cache': 'browser',
            'downloads-folder': 'basic',
            'dns-cache': 'basic',
            'clipboard': 'basic',
            'recent-docs': 'basic',
            
            # Advanced cleaning
            'directx-cache': 'advanced',
            'nvidia-cache': 'advanced',
            'thumbnail-cache': 'advanced',
            'windows-logs': 'advanced',
            'crash-dumps': 'advanced',
            'windows-defender': 'advanced',
            'java-cache': 'advanced',
            'onedrive-cache': 'advanced',
            'event-logs': 'advanced',
            'font-cache': 'advanced',
            'store-cache': 'advanced',
            'update-cache': 'advanced',
            'icon-cache': 'advanced',
            
            # Browser cleaning
            'browser-history': 'browser',
            'browser-cookies': 'browser',
            'saved-passwords': 'browser',
            'autofill-data': 'browser',
            'session-data': 'browser',
            'chrome-cookies': 'browser',
            'firefox-cookies': 'browser',
            'edge-cookies': 'browser',
            'opera-cookies': 'browser',
            'brave-cookies': 'browser',
            
            # Gaming cleaning
            'steam-cache': 'gaming',
            'epic-games-cache': 'gaming',
            'origin-cache': 'gaming',
            'adobe-cache': 'gaming',
            'spotify-cache': 'gaming',
            'discord-cache': 'gaming',
            'teams-cache': 'gaming',
            'vscode-cache': 'gaming',
            'npm-cache': 'gaming'
        }
        
        # Map checkbox IDs to cleaning categories
        cleaning_categories = set()
        for category in categories:
            if category in category_map:
                cleaning_categories.add(category_map[category])
            else:
                # If it's a direct category name, add it
                cleaning_categories.add(category)
        
        # Scan all selected categories
        for category in cleaning_categories:
            files = cleaner.scan_category(category)
            all_files.extend(files)
        
        if not all_files:
            return jsonify({'success': False, 'error': 'No files found to clean'})
        
        # Clean all files
        results = cleaner.clean_files([file['path'] for file in all_files])
        
        # Log cleanup results
        log_cleanup_results(results)
        
        # Refresh GPU drivers if nvidia-cache was selected
        if 'nvidia-cache' in categories:
            refresh_gpu_drivers()
        
        return jsonify({
            'success': True,
            'data': {
                'cleaned_files': results['cleaned_files'],
                'freed_space': results['freed_space'],
                'errors': results['errors']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def refresh_gpu_drivers():
    """Refresh GPU drivers after cleaning cache"""
    try:
        platform_system = os.name
        
        if platform_system == 'nt':  # Windows
            # For NVIDIA GPUs
            try:
                import subprocess
                subprocess.run(['powershell', '-Command', 'Get-Process | Where-Object {$_.Name -like "*nvidia*"} | Restart-Process'], 
                              capture_output=True, 
                              text=True)
            except Exception as e:
                print(f"Error refreshing NVIDIA drivers: {e}")
                
            # For AMD GPUs
            try:
                subprocess.run(['powershell', '-Command', 'Get-Process | Where-Object {$_.Name -like "*amd*"} | Restart-Process'], 
                              capture_output=True, 
                              text=True)
            except Exception as e:
                print(f"Error refreshing AMD drivers: {e}")
                
        else:  # Linux
            try:
                # Restart graphics services
                subprocess.run(['sudo', 'systemctl', 'restart', 'display-manager'], 
                              capture_output=True, 
                              text=True)
            except Exception as e:
                print(f"Error refreshing GPU drivers on Linux: {e}")
                
    except Exception as e:
        print(f"Error in refresh_gpu_drivers: {e}")

def perform_scan(scan_type):
    """Perform the actual system scan"""
    global scan_progress
    
    try:
        # Perform real file scanning
        def progress_callback(percent):
            scan_progress['progress'] = min(100, max(0, int(percent)))
        
        # Scan files based on category
        files = cleaner.scan_category(scan_type, progress_callback=progress_callback)
        
        # Update progress to 100% when complete
        scan_progress['progress'] = 100
        scan_progress['files'] = files
        scan_progress['status'] = 'completed'
        
        # Log scan results
        print(f"Scan completed: Found {len(files)} files for category '{scan_type}'")
        
    except Exception as e:
        scan_progress['status'] = 'error'
        scan_progress['error'] = str(e)
        print(f"Scan error: {e}")

@app.route('/api/scan-progress')
def get_scan_progress():
    """Get current scan progress"""
    return jsonify({
        'success': True,
        'data': scan_progress
    })

@app.route('/api/clean-files', methods=['POST'])
def clean_files():
    """Clean selected files"""
    try:
        file_paths = request.json.get('files', [])
        
        if not file_paths:
            return jsonify({'success': False, 'error': 'No files selected'})
        
        # Perform cleanup
        results = cleaner.clean_files(file_paths)
        
        # Log cleanup results
        log_cleanup_results(results)
        
        return jsonify({
            'success': True,
            'data': {
                'cleaned_files': results['cleaned_files'],
                'freed_space': results['freed_space'],
                'errors': results['errors']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/find-duplicates', methods=['POST'])
def find_duplicates():
    """Find duplicate files"""
    try:
        directory = request.json.get('directory', '/')
        
        duplicates = duplicate_finder.find_duplicates(directory)
        
        return jsonify({
            'success': True,
            'data': {
                'duplicates': duplicates,
                'total_groups': len(duplicates),
                'potential_savings': duplicate_finder.calculate_savings(duplicates)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/request-admin')
def request_admin():
    """Request admin privileges"""
    try:
        result = admin_utils.request_elevation()
        if result:
            return jsonify({
                'success': True,
                'data': {
                    'elevated': result,
                    'message': 'Admin privileges granted'
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to elevate privileges. Please try running the application as administrator manually.'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error requesting admin privileges: {str(e)}'
        })

@app.route('/api/download-log')
def download_log():
    """Download cleanup log"""
    try:
        log_file = os.path.join('logs', 'cleanup_log.txt')
        if os.path.exists(log_file):
            return send_file(log_file, as_attachment=True)
        else:
            return jsonify({'success': False, 'error': 'No log file found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/save-settings', methods=['POST'])
def save_settings():
    """Save user settings"""
    try:
        settings = request.json.get('settings', {})
        
        # Create settings directory if it doesn't exist
        os.makedirs('settings', exist_ok=True)
        
        # Save settings to file
        with open('settings/user_settings.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Settings saved successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/load-settings')
def load_settings():
    """Load user settings"""
    try:
        settings_file = 'settings/user_settings.json'
        
        # Default settings
        default_settings = {
            'theme': 'dark',
            'accent_color': 'purple',
            'start_with_windows': False,
            'run_as_admin': False,
            'minimize_to_tray': True,
            'create_backup': True,
            'show_confirmation': True,
            'schedule_cleaning': 'never'
        }
        
        # Check if settings file exists
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            # Merge with default settings to ensure all keys exist
            for key, value in default_settings.items():
                if key not in settings:
                    settings[key] = value
        else:
            settings = default_settings
            
            # Save default settings
            os.makedirs('settings', exist_ok=True)
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
        
        return jsonify({
            'success': True,
            'data': settings
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def log_cleanup_results(results):
    """Log cleanup results to file"""
    try:
        os.makedirs('logs', exist_ok=True)
        log_file = os.path.join('logs', 'cleanup_log.txt')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n--- Cleanup Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            f.write(f"Files Cleaned: {len(results['cleaned_files'])}\n")
            f.write(f"Space Freed: {results['freed_space']} bytes\n")
            
            for file_path in results['cleaned_files']:
                f.write(f"Cleaned: {file_path}\n")
            
            for error in results['errors']:
                f.write(f"Error: {error}\n")
            
            f.write("-" * 50 + "\n")
    except Exception as e:
        print(f"Failed to log results: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)