from flask import Flask, render_template, jsonify, request, send_file
import os
import json
import threading
import time
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

@app.route('/')
def index():
    """Main application page"""
    return render_template('index.html')

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
                'temperature': stats.get('temperature', None)
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
        
        # Scan all selected categories
        for category in categories:
            files = cleaner.scan_category(category)
            all_files.extend(files)
        
        if not all_files:
            return jsonify({'success': False, 'error': 'No files found to clean'})
        
        # Clean all files
        results = cleaner.clean_files([file['path'] for file in all_files])
        
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
        return jsonify({
            'success': True,
            'data': {
                'elevated': result,
                'message': 'Admin privileges granted' if result else 'Failed to elevate privileges'
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

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
    app.run(host='0.0.0.0', port=7000, debug=True)