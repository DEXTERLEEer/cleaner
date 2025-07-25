import os
import time
import platform
import subprocess
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
            if self.platform == 'linux':
                # Read from /proc/stat
                with open('/proc/stat', 'r') as f:
                    line = f.readline()
                    cpu_times = [int(x) for x in line.split()[1:]]
                    
                # Calculate CPU usage
                idle_time = cpu_times[3]
                total_time = sum(cpu_times)
                
                # Store previous values for delta calculation
                if not hasattr(self, '_prev_idle'):
                    self._prev_idle = idle_time
                    self._prev_total = total_time
                    return 0.0
                
                idle_delta = idle_time - self._prev_idle
                total_delta = total_time - self._prev_total
                
                self._prev_idle = idle_time
                self._prev_total = total_time
                
                if total_delta == 0:
                    return 0.0
                
                cpu_usage = ((total_delta - idle_delta) / total_delta) * 100
                return max(0.0, min(100.0, cpu_usage))
                
            else:
                # Fallback for other platforms
                return self._get_cpu_usage_fallback()
                
        except Exception as e:
            print(f"Error getting CPU usage: {e}")
            return 0.0
    
    def _get_cpu_usage_fallback(self) -> float:
        """Fallback CPU usage calculation"""
        try:
            # Use uptime command if available
            result = subprocess.run(['uptime'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                output = result.stdout
                # Parse load average (rough approximation)
                if 'load average:' in output:
                    load_str = output.split('load average:')[1].strip()
                    load_1min = float(load_str.split(',')[0].strip())
                    # Convert to percentage (approximate)
                    cpu_count = os.cpu_count() or 1
                    return min(100.0, (load_1min / cpu_count) * 100)
        except Exception:
            pass
        
        return 0.0
    
    def get_memory_usage(self) -> float:
        """Get current memory usage percentage"""
        try:
            if self.platform == 'linux':
                with open('/proc/meminfo', 'r') as f:
                    meminfo = {}
                    for line in f:
                        parts = line.split(':')
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = int(parts[1].strip().split()[0])  # Remove 'kB' unit
                            meminfo[key] = value
                
                total_mem = meminfo.get('MemTotal', 0)
                free_mem = meminfo.get('MemFree', 0)
                buffers = meminfo.get('Buffers', 0)
                cached = meminfo.get('Cached', 0)
                
                if total_mem == 0:
                    return 0.0
                
                used_mem = total_mem - free_mem - buffers - cached
                usage_percent = (used_mem / total_mem) * 100
                
                return max(0.0, min(100.0, usage_percent))
            else:
                return self._get_memory_usage_fallback()
                
        except Exception as e:
            print(f"Error getting memory usage: {e}")
            return 0.0
    
    def _get_memory_usage_fallback(self) -> float:
        """Fallback memory usage calculation"""
        try:
            # Use free command if available
            result = subprocess.run(['free', '-m'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    memory_line = lines[1].split()
                    if len(memory_line) >= 3:
                        total = int(memory_line[1])
                        used = int(memory_line[2])
                        return (used / total) * 100 if total > 0 else 0.0
        except Exception:
            pass
        
        return 0.0
    
    def get_disk_usage(self) -> float:
        """Get disk usage percentage for root partition"""
        try:
            statvfs = os.statvfs('/')
            total_space = statvfs.f_frsize * statvfs.f_blocks
            # Use f_bavail if f_available is not available
            if hasattr(statvfs, 'f_available'):
                free_space = statvfs.f_frsize * statvfs.f_available
            else:
                free_space = statvfs.f_frsize * statvfs.f_bavail
            used_space = total_space - free_space
            
            if total_space == 0:
                return 0.0
            
            usage_percent = (used_space / total_space) * 100
            return max(0.0, min(100.0, usage_percent))
            
        except Exception as e:
            print(f"Error getting disk usage: {e}")
            return 0.0
    
    def get_free_space(self) -> int:
        """Get free space in bytes for root partition"""
        try:
            statvfs = os.statvfs('/')
            # Use f_bavail if f_available is not available
            if hasattr(statvfs, 'f_available'):
                free_space = statvfs.f_frsize * statvfs.f_available
            else:
                free_space = statvfs.f_frsize * statvfs.f_bavail
            return free_space
        except Exception as e:
            print(f"Error getting free space: {e}")
            return 0
    
    def get_total_space(self) -> int:
        """Get total space in bytes for root partition"""
        try:
            statvfs = os.statvfs('/')
            total_space = statvfs.f_frsize * statvfs.f_blocks
            return total_space
        except Exception as e:
            print(f"Error getting total space: {e}")
            return 0
    
    def get_temperature(self) -> Optional[float]:
        """Get system temperature if available"""
        try:
            if self.platform == 'linux':
                # Try to read from thermal zones
                thermal_paths = [
                    '/sys/class/thermal/thermal_zone0/temp',
                    '/sys/class/thermal/thermal_zone1/temp'
                ]
                
                for path in thermal_paths:
                    if os.path.exists(path):
                        with open(path, 'r') as f:
                            temp_millicelsius = int(f.read().strip())
                            return temp_millicelsius / 1000.0
                
                # Try sensors command
                result = subprocess.run(['sensors'], capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    output = result.stdout
                    # Parse temperature from sensors output (basic parsing)
                    for line in output.split('\n'):
                        if '°C' in line and ('Core' in line or 'temp' in line.lower()):
                            temp_str = line.split('°C')[0].split()[-1]
                            try:
                                return float(temp_str.replace('+', ''))
                            except ValueError:
                                continue
            
        except Exception as e:
            print(f"Error getting temperature: {e}")
        
        return None
    
    def get_uptime(self) -> float:
        """Get system uptime in seconds"""
        try:
            if self.platform == 'linux':
                with open('/proc/uptime', 'r') as f:
                    uptime_seconds = float(f.read().split()[0])
                    return uptime_seconds
            else:
                # Fallback using uptime command
                result = subprocess.run(['uptime', '-s'], capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    # Parse boot time and calculate uptime
                    boot_time_str = result.stdout.strip()
                    # This would need proper datetime parsing
                    return 3600.0  # Placeholder
                    
        except Exception as e:
            print(f"Error getting uptime: {e}")
        
        return 0.0
    
    def get_load_average(self) -> tuple:
        """Get system load average (1min, 5min, 15min)"""
        try:
            if self.platform == 'linux':
                with open('/proc/loadavg', 'r') as f:
                    load_avg = f.read().split()[:3]
                    return tuple(float(x) for x in load_avg)
            else:
                # Fallback using uptime command
                result = subprocess.run(['uptime'], capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    output = result.stdout
                    if 'load average:' in output:
                        load_str = output.split('load average:')[1].strip()
                        loads = [float(x.strip()) for x in load_str.split(',')]
                        return tuple(loads)
        except Exception as e:
            print(f"Error getting load average: {e}")
        
        return (0.0, 0.0, 0.0)
    
    def get_network_usage(self) -> Dict:
        """Get network usage statistics"""
        try:
            if self.platform == 'linux':
                with open('/proc/net/dev', 'r') as f:
                    lines = f.readlines()[2:]  # Skip header lines
                    
                total_rx_bytes = 0
                total_tx_bytes = 0
                
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 10:
                        # Interface stats: rx_bytes is at index 1, tx_bytes at index 9
                        rx_bytes = int(parts[1])
                        tx_bytes = int(parts[9])
                        
                        total_rx_bytes += rx_bytes
                        total_tx_bytes += tx_bytes
                
                return {
                    'bytes_received': total_rx_bytes,
                    'bytes_sent': total_tx_bytes
                }
        except Exception as e:
            print(f"Error getting network usage: {e}")
        
        return {'bytes_received': 0, 'bytes_sent': 0}
    
    def get_process_count(self) -> int:
        """Get number of running processes"""
        try:
            if self.platform == 'linux':
                proc_count = len([name for name in os.listdir('/proc') if name.isdigit()])
                return proc_count
            else:
                # Fallback using ps command
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    # Count lines (excluding header)
                    return len(result.stdout.strip().split('\n')) - 1
        except Exception as e:
            print(f"Error getting process count: {e}")
        
        return 0
    
    def get_disk_io_stats(self) -> Dict:
        """Get disk I/O statistics"""
        try:
            if self.platform == 'linux':
                with open('/proc/diskstats', 'r') as f:
                    total_read_bytes = 0
                    total_write_bytes = 0
                    
                    for line in f:
                        parts = line.split()
                        if len(parts) >= 14:
                            # Read sectors (index 5) and write sectors (index 9)
                            # Each sector is typically 512 bytes
                            read_sectors = int(parts[5])
                            write_sectors = int(parts[9])
                            
                            total_read_bytes += read_sectors * 512
                            total_write_bytes += write_sectors * 512
                    
                    return {
                        'bytes_read': total_read_bytes,
                        'bytes_written': total_write_bytes
                    }
        except Exception as e:
            print(f"Error getting disk I/O stats: {e}")
        
        return {'bytes_read': 0, 'bytes_written': 0}
