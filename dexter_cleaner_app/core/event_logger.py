import os
import time
from datetime import datetime

class EventLogger:
    """Event logging functionality for the application"""
    
    def __init__(self, log_dir="logs"):
        """Initialize the event logger"""
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.event_log_path = os.path.join(log_dir, "event_log.txt")
        
        # Create the log file if it doesn't exist
        if not os.path.exists(self.event_log_path):
            with open(self.event_log_path, "w", encoding="utf-8") as f:
                f.write(f"=== DexterOptiClean Event Log ===\nCreated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    def log_event(self, event_type, message, details=None):
        """Log an event to the event log file"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(self.event_log_path, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {event_type}: {message}\n")
                
                if details:
                    if isinstance(details, dict):
                        for key, value in details.items():
                            f.write(f"  - {key}: {value}\n")
                    else:
                        f.write(f"  Details: {details}\n")
                
                f.write("\n")
                
            return True
        except Exception as e:
            print(f"Error writing to event log: {e}")
            return False
    
    def log_admin_error(self):
        """Log an admin privileges error"""
        self.log_event(
            "ADMIN_ERROR", 
            "Error: An error occurred while requesting admin privileges.",
            {"source": "admin_utils.py", "severity": "high"}
        )
    
    def log_system_status(self, stats):
        """Log system status check"""
        self.log_event(
            "SYSTEM_STATUS",
            "System status check performed",
            stats
        )
    
    def log_cleanup_attempt(self, categories=None):
        """Log cleanup attempt"""
        self.log_event(
            "CLEANUP_ATTEMPT",
            "Cleanup operation attempted but failed due to admin privileges error",
            {"categories": categories if categories else "all"}
        )
    
    def log_scan_attempt(self, scan_type):
        """Log scan attempt"""
        self.log_event(
            "SCAN_ATTEMPT",
            "System scan attempted but failed due to admin privileges error",
            {"scan_type": scan_type}
        )
    
    def get_recent_events(self, count=10):
        """Get the most recent events from the log"""
        try:
            if not os.path.exists(self.event_log_path):
                return []
                
            with open(self.event_log_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Split by double newline to get event blocks
            events = content.split("\n\n")
            
            # Filter out empty events and return the most recent ones
            valid_events = [e for e in events if e.strip()]
            return valid_events[-count:] if valid_events else []
            
        except Exception as e:
            print(f"Error reading event log: {e}")
            return []