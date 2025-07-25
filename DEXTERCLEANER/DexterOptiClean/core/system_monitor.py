import os
import time
import platform
import subprocess
import psutil
from typing import Dict, Optional

class SystemMonitor:
    """System monitoring and statistics"""
    
    def __init__(self):
        self.platform = platform.system().lower()
    
    def get_system_stats(self) -> Dict:
        """Get comprehensive system statistics"""
        stats = {
            'cpu_usage': self.get_cpu_usage(),
            'memory_usage': self.get_memory_usage(),
            'disk_usage': self.get_disk_usage(),
            'free_space': self.get_free_space(),
            'total_space': self.get_total_space(),
            'temperature': self.get_temperature(),
            'uptime': self.get_uptime(),
            'load_average': self.get_load_average()
        }
        
        return stats
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            return psutil.cpu_percent(interval=0.1)
        except Exception as e:
            print(f"Error getting CPU usage: {e}")
            return 0.0
    
    def get_memory_usage(self) -> float:
        """Get current memory usage percentage"""
        try:
            return psutil.virtual_memory().percent
        except Exception as e:
            print(f"Error getting memory usage: {e}")
            return 0.0
    
    def get_disk_usage(self) -> float:
        """Get disk usage percentage for root partition"""
        try:
            # Use psutil instead of os.statvfs
            return psutil.disk_usage('/').percent
        except Exception as e:
            try:
                # Fallback for Windows
                return psutil.disk_usage('C:\\').percent
            except Exception as e2:
                print(f"Error getting disk usage: {e2}")
                return 0.0
    
    def get_free_space(self) -> int:
        """Get free space in bytes for root partition"""
        try:
            # Use psutil instead of os.statvfs
            return psutil.disk_usage('/').free
        except Exception as e:
            try:
                # Fallback for Windows
                return psutil.disk_usage('C:\\').free
            except Exception as e2:
                print(f"Error getting free space: {e2}")
                return 0
    
    def get_total_space(self) -> int:
        """Get total space in bytes for root partition"""
        try:
            # Use psutil instead of os.statvfs
            return psutil.disk_usage('/').total
        except Exception as e:
            try:
                # Fallback for Windows
                return psutil.disk_usage('C:\\').total
            except Exception as e2:
                print(f"Error getting total space: {e2}")
                return 0
    
    def get_temperature(self) -> Optional[float]:
        """Get system temperature if available"""
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        for entry in entries:
                            return entry.current
            return None
        except Exception as e:
            print(f"Error getting temperature: {e}")
            return None
    
    def get_uptime(self) -> float:
        """Get system uptime in seconds"""
        try:
            return time.time() - psutil.boot_time()
        except Exception as e:
            print(f"Error getting uptime: {e}")
            return 0.0
    
    def get_load_average(self) -> tuple:
        """Get system load average (1min, 5min, 15min)"""
        try:
            if hasattr(psutil, "getloadavg"):
                return psutil.getloadavg()
            else:
                # Fallback for Windows
                return (psutil.cpu_percent() / 100, 0.0, 0.0)
        except Exception as e:
            print(f"Error getting load average: {e}")
            return (0.0, 0.0, 0.0)
    
    def get_network_usage(self) -> Dict:
        """Get network usage statistics"""
        try:
            net_io = psutil.net_io_counters()
            return {
                'bytes_received': net_io.bytes_recv,
                'bytes_sent': net_io.bytes_sent
            }
        except Exception as e:
            print(f"Error getting network usage: {e}")
            return {'bytes_received': 0, 'bytes_sent': 0}
    
    def get_process_count(self) -> int:
        """Get number of running processes"""
        try:
            return len(psutil.pids())
        except Exception as e:
            print(f"Error getting process count: {e}")
            return 0
    
    def get_disk_io_stats(self) -> Dict:
        """Get disk I/O statistics"""
        try:
            disk_io = psutil.disk_io_counters()
            return {
                'bytes_read': disk_io.read_bytes,
                'bytes_written': disk_io.write_bytes
            }
        except Exception as e:
            print(f"Error getting disk I/O stats: {e}")
            return {'bytes_read': 0, 'bytes_written': 0}