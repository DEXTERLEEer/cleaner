import os
import sys
import subprocess
import platform
import psutil
import time

class AdminUtils:
    """Admin privilege management utilities"""
    
    def __init__(self):
        self.platform = platform.system().lower()
    
    def check_admin_privileges(self) -> bool:
        """Check if the application is running with admin/root privileges"""
        try:
            if self.platform == 'windows':
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                # Unix-like systems
                return os.getuid() == 0
        except Exception as e:
            print(f"Error checking admin privileges: {e}")
            return False
    
    def request_elevation(self) -> bool:
        """Request admin privileges elevation and restart application"""
        try:
            # For demonstration purposes, always display the error message
            # and return False to simulate failure
            print("Error: An error occurred while requesting admin privileges.")
            return False
                
        except Exception as e:
            print("Error: An error occurred while requesting admin privileges.")
            # Return False instead of raising an exception
            return False
    
    def _request_windows_elevation(self, current_pid) -> bool:
        """Request elevation on Windows using UAC and terminate original process"""
        try:
            # Check if we're running in a Python environment where ctypes is available
            try:
                import ctypes
                from ctypes import wintypes
            except ImportError:
                print("Windows elevation requires ctypes module")
                return False
            
            # Prepare command to restart the application with admin rights
            # Add a special flag to indicate this is a restart with admin rights
            script_path = os.path.abspath(sys.argv[0])
            args = sys.argv[1:] if len(sys.argv) > 1 else []
            args.append("--admin-restart")  # Add flag to indicate admin restart
            
            # Show UAC prompt
            try:
                result = ctypes.windll.shell32.ShellExecuteW(
                    None,
                    "runas",
                    sys.executable,
                    " ".join([script_path] + args),
                    None,
                    1  # SW_SHOWNORMAL
                )
                
                # If ShellExecuteW returns > 32, it was successful
                if result > 32:
                    # Wait a moment to ensure the new process starts
                    time.sleep(1)
                    
                    # Terminate the current process
                    try:
                        # Use psutil to get the process and terminate it
                        process = psutil.Process(current_pid)
                        process.terminate()
                    except Exception as e:
                        print(f"Error terminating original process: {e}")
                    
                    # Exit the current process
                    sys.exit(0)
                    
                return result > 32
            except Exception as e:
                print(f"ShellExecuteW failed: {e}")
                return False
            
        except Exception as e:
            print(f"Windows elevation error: {e}")
            return False
    
    def _request_unix_elevation(self, current_pid) -> bool:
        """Request elevation on Unix-like systems using sudo and terminate original process"""
        try:
            # Check if sudo is available
            result = subprocess.run(['which', 'sudo'], 
                                  capture_output=True, 
                                  text=True)
            
            if result.returncode != 0:
                print("sudo not available")
                return False
            
            # Try to run a simple command with sudo to test privileges
            test_result = subprocess.run(['sudo', '-n', 'true'], 
                                       capture_output=True, 
                                       text=True)
            
            if test_result.returncode == 0:
                # Already have sudo privileges
                return True
            
            # Prepare command to restart the application with admin rights
            script_path = os.path.abspath(sys.argv[0])
            args = sys.argv[1:] if len(sys.argv) > 1 else []
            args.append("--admin-restart")  # Add flag to indicate admin restart
            
            # Request sudo privileges and restart the application
            print("Requesting administrator privileges...")
            
            try:
                # Build the command to execute with sudo
                sudo_command = ['sudo', sys.executable, script_path] + args
                
                # Start the new process with sudo
                subprocess.Popen(sudo_command)
                
                # Wait a moment to ensure the new process starts
                time.sleep(1)
                
                # Terminate the current process
                try:
                    # Use psutil to get the process and terminate it
                    process = psutil.Process(current_pid)
                    process.terminate()
                except Exception as e:
                    print(f"Error terminating original process: {e}")
                
                # Exit the current process
                sys.exit(0)
                
                return True
            except Exception as e:
                print(f"Failed to start sudo process: {e}")
                return False
            
        except Exception as e:
            print(f"Unix elevation error: {e}")
            return False
    
    def run_as_admin(self, command: list) -> subprocess.CompletedProcess:
        """Run a command with admin privileges"""
        try:
            if self.platform == 'windows':
                return self._run_windows_admin(command)
            else:
                return self._run_unix_admin(command)
        except Exception as e:
            print(f"Error running command as admin: {e}")
            return subprocess.CompletedProcess(command, 1, '', str(e))
    
    def _run_windows_admin(self, command: list) -> subprocess.CompletedProcess:
        """Run command as admin on Windows"""
        try:
            # Use PowerShell with Start-Process -Verb RunAs
            ps_command = [
                'powershell', '-Command',
                f'Start-Process -FilePath "{command[0]}" -ArgumentList "{" ".join(command[1:])}" -Verb RunAs -Wait'
            ]
            
            return subprocess.run(ps_command, 
                                capture_output=True, 
                                text=True, 
                                timeout=30)
        except Exception as e:
            return subprocess.CompletedProcess(command, 1, '', str(e))
    
    def _run_unix_admin(self, command: list) -> subprocess.CompletedProcess:
        """Run command as admin on Unix-like systems"""
        try:
            sudo_command = ['sudo'] + command
            return subprocess.run(sudo_command, 
                                capture_output=True, 
                                text=True, 
                                timeout=30)
        except Exception as e:
            return subprocess.CompletedProcess(command, 1, '', str(e))
    
    def get_user_info(self) -> dict:
        """Get current user information"""
        try:
            user_info = {
                'username': os.getlogin() if hasattr(os, 'getlogin') else os.environ.get('USER', 'unknown'),
                'is_admin': self.check_admin_privileges(),
                'uid': os.getuid() if hasattr(os, 'getuid') else None,
                'gid': os.getgid() if hasattr(os, 'getgid') else None,
                'home_dir': os.path.expanduser('~'),
                'platform': self.platform
            }
            
            return user_info
        except Exception as e:
            print(f"Error getting user info: {e}")
            return {'error': str(e)}
    
    def can_access_path(self, path: str) -> bool:
        """Check if current user can access a specific path"""
        try:
            return os.access(path, os.R_OK | os.W_OK)
        except Exception:
            return False
    
    def get_restricted_paths(self) -> list:
        """Get list of paths that typically require admin access"""
        if self.platform == 'windows':
            return [
                'C:\\Windows\\System32',
                'C:\\Program Files',
                'C:\\Program Files (x86)',
                'C:\\ProgramData',
                'C:\\Windows\\Temp'
            ]
        else:
            return [
                '/root',
                '/etc',
                '/usr/bin',
                '/usr/sbin',
                '/var/log',
                '/sys',
                '/proc'
            ]
    
    def elevate_file_operation(self, operation: str, source: str, destination: str = None) -> bool:
        """Perform file operation with elevated privileges"""
        try:
            if operation == 'delete':
                if self.platform == 'windows':
                    command = ['del', '/f', '/q', source]
                else:
                    command = ['rm', '-f', source]
            elif operation == 'move' and destination:
                if self.platform == 'windows':
                    command = ['move', source, destination]
                else:
                    command = ['mv', source, destination]
            elif operation == 'copy' and destination:
                if self.platform == 'windows':
                    command = ['copy', source, destination]
                else:
                    command = ['cp', source, destination]
            else:
                return False
            
            result = self.run_as_admin(command)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error in elevated file operation: {e}")
            return False
    
    def create_scheduled_task(self, task_name: str, command: str, schedule: str = 'daily') -> bool:
        """Create a scheduled task (Windows) or cron job (Unix)"""
        try:
            if self.platform == 'windows':
                return self._create_windows_task(task_name, command, schedule)
            else:
                return self._create_unix_cronjob(task_name, command, schedule)
        except Exception as e:
            print(f"Error creating scheduled task: {e}")
            return False
    
    def _create_windows_task(self, task_name: str, command: str, schedule: str) -> bool:
        """Create Windows scheduled task"""
        try:
            schtasks_command = [
                'schtasks', '/create',
                '/tn', task_name,
                '/tr', command,
                '/sc', schedule,
                '/f'  # Force creation
            ]
            
            result = self.run_as_admin(schtasks_command)
            return result.returncode == 0
        except Exception as e:
            print(f"Windows task creation error: {e}")
            return False
    
    def _create_unix_cronjob(self, task_name: str, command: str, schedule: str) -> bool:
        """Create Unix cron job"""
        try:
            # Define cron schedule patterns
            cron_schedules = {
                'daily': '0 2 * * *',  # 2 AM daily
                'weekly': '0 2 * * 0',  # 2 AM on Sunday
                'monthly': '0 2 1 * *'  # 2 AM on 1st of month
            }
            
            cron_time = cron_schedules.get(schedule, '0 2 * * *')
            cron_entry = f"{cron_time} {command} # {task_name}\n"
            
            # Add to crontab
            result = subprocess.run(['crontab', '-l'], 
                                  capture_output=True, 
                                  text=True)
            
            current_crontab = result.stdout if result.returncode == 0 else ""
            
            # Check if task already exists
            if task_name not in current_crontab:
                new_crontab = current_crontab + cron_entry
                
                # Install new crontab
                process = subprocess.Popen(['crontab', '-'], 
                                         stdin=subprocess.PIPE, 
                                         text=True)
                process.communicate(input=new_crontab)
                
                return process.returncode == 0
            
            return True  # Task already exists
            
        except Exception as e:
            print(f"Unix cron job creation error: {e}")
            return False