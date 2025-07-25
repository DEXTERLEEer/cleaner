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
from core.event_logger import EventLogger

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dexter_pc_optimizer_secret_key')

# Global variables for state management
scan_progress = {'progress': 0, 'status': 'idle', 'files': []}
system_stats = {}
cleaner = PCCleaner()
monitor = SystemMonitor()
admin_utils = AdminUtils()
duplicate_finder = DuplicateFinder()
event_logger = EventLogger()

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
        # Always set admin_status to False to trigger error messages
        admin_status = False
        
        # Print the error message to console
        print("Error: An error occurred while requesting admin privileges.")
        
        # Log the event
        event_logger.log_admin_error()
        event_logger.log_system_status(stats)
        
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
                'is_admin_restart': is_admin_restart,
                'admin_error': "Error: An error occurred while requesting admin privileges."
            }
        })
    except Exception as e:
        event_logger.log_event("ERROR", f"System status error: {str(e)}")
        return jsonify({'success': False, 'error': "Error: An error occurred while requesting admin privileges."})

@app.route('/api/start-scan', methods=['POST'])
def start_scan():
    """Start system scan for cleanup candidates"""
    global scan_progress
    
    try:
        scan_type = request.json.get('scan_type', 'basic')
        
        # Print the error message to console
        print("Error: An error occurred while requesting admin privileges.")
        
        # Log the scan attempt
        event_logger.log_scan_attempt(scan_type)
        event_logger.log_admin_error()
        
        # Always return admin error
        return jsonify({
            'success': False,
            'error': "Error: An error occurred while requesting admin privileges."
        })
    except Exception as e:
        event_logger.log_event("ERROR", f"Scan error: {str(e)}")
        return jsonify({
            'success': False,
            'error': "Error: An error occurred while requesting admin privileges."
        })

@app.route('/api/clean-all', methods=['POST'])
def clean_all():
    """Clean all files from selected categories"""
    try:
        categories = request.json.get('categories', [])
        
        # Print the error message to console
        print("Error: An error occurred while requesting admin privileges.")
        
        # Log the cleanup attempt
        event_logger.log_cleanup_attempt(categories)
        event_logger.log_admin_error()
        
        # Always return admin error
        return jsonify({
            'success': False,
            'error': "Error: An error occurred while requesting admin privileges."
        })
    except Exception as e:
        event_logger.log_event("ERROR", f"Clean all error: {str(e)}")
        return jsonify({
            'success': False,
            'error': "Error: An error occurred while requesting admin privileges."
        })

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
        # Print the error message to console
        print("Error: An error occurred while requesting admin privileges.")
        
        # Always return admin error
        return jsonify({
            'success': False,
            'error': "Error: An error occurred while requesting admin privileges."
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': "Error: An error occurred while requesting admin privileges."
        })

@app.route('/api/find-duplicates', methods=['POST'])
def find_duplicates():
    """Find duplicate files"""
    try:
        # Print the error message to console
        print("Error: An error occurred while requesting admin privileges.")
        
        # Always return admin error
        return jsonify({
            'success': False,
            'error': "Error: An error occurred while requesting admin privileges."
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': "Error: An error occurred while requesting admin privileges."
        })

@app.route('/api/request-admin')
def request_admin():
    """Request admin privileges"""
    try:
        # Call request_elevation but ignore the result
        admin_utils.request_elevation()
        
        # Log the admin error event
        event_logger.log_admin_error()
        
        # Always return the specific error message
        return jsonify({
            'success': False,
            'error': 'Error: An error occurred while requesting admin privileges.'
        })
    except Exception as e:
        event_logger.log_event("ERROR", f"Admin request error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error: An error occurred while requesting admin privileges.'
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

@app.route('/api/event-log')
def get_event_log():
    """Get event log entries"""
    try:
        events = event_logger.get_recent_events(50)  # Get the 50 most recent events
        
        return jsonify({
            'success': True,
            'data': {
                'events': events,
                'count': len(events)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/download-event-log')
def download_event_log():
    """Download event log"""
    try:
        log_file = os.path.join('logs', 'event_log.txt')
        if os.path.exists(log_file):
            return send_file(log_file, as_attachment=True)
        else:
            return jsonify({'success': False, 'error': 'No event log file found'})
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
    app.run(host='0.0.0.0', port=3001, debug=True)