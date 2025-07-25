import os
import shutil
import tempfile
import time
import json
import glob
from pathlib import Path
from typing import List, Dict, Callable, Optional

class PCCleaner:
    """Core PC cleaning functionality"""
    
    def __init__(self):
        self.temp_dirs = [
            '/tmp',
            '/var/tmp', 
            '~/.cache',
            '~/.local/share/Trash',
            '~/Downloads',  # Only scan for old files
            '~/.thumbnails',
            '~/.local/share/recently-used.xbel'
        ]
        
        self.browser_dirs = {
            'chrome': [
                '~/.config/google-chrome/Default/Cache',
                '~/.config/google-chrome/Default/Code Cache',
                '~/.config/google-chrome/Default/GPUCache',
                '~/.config/google-chrome/Default/Service Worker/CacheStorage',
                '~/.cache/google-chrome'
            ],
            'firefox': [
                '~/.mozilla/firefox/*/cache2',
                '~/.cache/mozilla/firefox',
                '~/.mozilla/firefox/*/startupCache',
                '~/.mozilla/firefox/*/OfflineCache'
            ],
            'edge': [
                '~/.config/microsoft-edge/Default/Cache',
                '~/.config/microsoft-edge/Default/Code Cache', 
                '~/.cache/microsoft-edge'
            ],
            'chromium': [
                '~/.config/chromium/Default/Cache',
                '~/.config/chromium/Default/Code Cache',
                '~/.cache/chromium'
            ]
        }
        
        self.system_logs = [
            '/var/log/*.log',
            '/var/log/*/*.log',
            '~/.xsession-errors',
            '~/.local/share/xorg'
        ]
        
        # Advanced cleaning categories
        self.advanced_dirs = {
            'directx_cache': [
                '~/.cache/mesa_shader_cache',
                '~/.cache/radv_cache'
            ],
            'nvidia_cache': [
                '~/.nv',
                '~/.cache/nvidia'
            ],
            'thumbnail_cache': [
                '~/.cache/thumbnails',
                '~/.thumbnails'
            ],
            'windows_logs': [
                '/var/log/syslog*',
                '/var/log/auth.log*',
                '/var/log/kern.log*'
            ],
            'crash_dumps': [
                '/var/crash',
                '~/core',
                '/tmp/core*'
            ],
            'java_cache': [
                '~/.cache/icedtea-web',
                '~/.java/.userPrefs'
            ],
            'onedrive_cache': [
                '~/.cache/onedrive',
                '~/OneDrive/.849C9593-D756-4E56-8D6E-42412F2A707B'
            ],
            'font_cache': [
                '~/.cache/fontconfig',
                '/var/cache/fontconfig'
            ],
            'update_cache': [
                '/var/cache/apt',
                '/var/cache/yum',
                '~/.cache/pip'
            ],
            'icon_cache': [
                '~/.cache/icon-cache.kcache',
                '~/.cache/ksycoca*'
            ]
        }
        
        # Gaming platform cache directories
        self.gaming_dirs = {
            'steam_cache': [
                '~/.steam/cached',
                '~/.steam/appcache',
                '~/.local/share/Steam/cached',
                '~/.local/share/Steam/appcache'
            ],
            'epic_games_cache': [
                '~/.cache/Epic',
                '~/.config/Epic/UnrealEngine/Engine/Config/UserSettings.ini'
            ],
            'origin_cache': [
                '~/.cache/origin',
                '~/.wine/drive_c/ProgramData/Origin/Logs'
            ],
            'adobe_cache': [
                '~/.cache/Adobe',
                '~/.adobe'
            ],
            'spotify_cache': [
                '~/.cache/spotify',
                '~/.config/spotify/storage'
            ],
            'discord_cache': [
                '~/.cache/discord',
                '~/.config/discord/Cache'
            ],
            'teams_cache': [
                '~/.cache/Microsoft Teams',
                '~/.config/Microsoft/Microsoft Teams'
            ],
            'vscode_cache': [
                '~/.cache/vscode-cpptools',
                '~/.vscode/logs'
            ],
            'npm_cache': [
                '~/.npm/_cache',
                '~/.cache/npm'
            ]
        }
        
        # Browser specific cleaning
        self.browser_cleaning = {
            'history': True,
            'cookies': True,
            'passwords': False,  # Disabled by default for safety
            'autofill': True,
            'session_data': True
        }

    def scan_category(self, category: str, progress_callback: Optional[Callable] = None) -> List[Dict]:
        """Scan for files in a specific category"""
        files = []
        
        try:
            if category == 'basic':
                files.extend(self._scan_basic_cleaning())
            elif category == 'advanced':
                files.extend(self._scan_advanced_cleaning())
            elif category == 'browser':
                files.extend(self._scan_browser_cleaning())
            elif category == 'gaming':
                files.extend(self._scan_gaming_cleaning())
            
            # Update progress
            if progress_callback:
                for i in range(len(files)):
                    progress_callback((i + 1) / len(files) * 100)
                    time.sleep(0.001)  # Small delay to show progress
                    
        except Exception as e:
            print(f"Error scanning {category}: {e}")
        
        return files

    def _scan_basic_cleaning(self) -> List[Dict]:
        """Scan basic cleaning categories"""
        files = []
        files.extend(self._scan_temp_files())
        files.extend(self._scan_cache_files())
        files.extend(self._scan_downloads_folder())
        files.extend(self._scan_clipboard_data())
        files.extend(self._scan_recent_documents())
        return files
    
    def _scan_advanced_cleaning(self) -> List[Dict]:
        """Scan advanced cleaning categories"""
        files = []
        for category, dirs in self.advanced_dirs.items():
            files.extend(self._scan_directories(dirs, self._get_category_description(category)))
        return files
    
    def _scan_browser_cleaning(self) -> List[Dict]:
        """Scan browser-specific cleaning categories"""
        files = []
        files.extend(self._scan_browser_files())
        files.extend(self._scan_browser_history())
        files.extend(self._scan_browser_cookies())
        return files
    
    def _scan_gaming_cleaning(self) -> List[Dict]:
        """Scan gaming platform cleaning categories"""
        files = []
        for category, dirs in self.gaming_dirs.items():
            files.extend(self._scan_directories(dirs, self._get_category_description(category)))
        return files
    
    def _get_category_description(self, category: str) -> str:
        """Get description for category"""
        descriptions = {
            'directx_cache': 'DirectX shader cache files',
            'nvidia_cache': 'NVIDIA graphics cache files',
            'thumbnail_cache': 'Image thumbnail cache files',
            'windows_logs': 'System log files',
            'crash_dumps': 'Application crash dump files',
            'java_cache': 'Java application cache',
            'onedrive_cache': 'OneDrive synchronization cache',
            'font_cache': 'Font rendering cache files',
            'update_cache': 'System update cache files',
            'icon_cache': 'Desktop icon cache files',
            'steam_cache': 'Steam platform cache files',
            'epic_games_cache': 'Epic Games launcher cache',
            'origin_cache': 'Origin platform cache files',
            'adobe_cache': 'Adobe applications cache',
            'spotify_cache': 'Spotify music cache files',
            'discord_cache': 'Discord application cache',
            'teams_cache': 'Microsoft Teams cache files',
            'vscode_cache': 'Visual Studio Code cache',
            'npm_cache': 'Node.js package manager cache'
        }
        return descriptions.get(category, 'Temporary cache files')
    
    def _scan_downloads_folder(self) -> List[Dict]:
        """Scan downloads folder for old files"""
        files = []
        downloads_path = os.path.expanduser('~/Downloads')
        
        if os.path.exists(downloads_path):
            cutoff_date = time.time() - (30 * 24 * 3600)  # 30 days ago
            
            for file_path in glob.glob(os.path.join(downloads_path, '*')):
                if os.path.isfile(file_path):
                    try:
                        stat = os.stat(file_path)
                        if stat.st_mtime < cutoff_date:
                            files.append({
                                'path': file_path,
                                'size': stat.st_size,
                                'description': 'Old download file (30+ days)'
                            })
                    except (OSError, IOError):
                        continue
        
        return files
    
    def _scan_clipboard_data(self) -> List[Dict]:
        """Scan clipboard cache files"""
        files = []
        clipboard_paths = [
            '~/.cache/clipboard',
            '~/.local/share/clipit',
            '/tmp/clipboard*'
        ]
        
        for path_pattern in clipboard_paths:
            files.extend(self._scan_directories([path_pattern], 'Clipboard cache data'))
        
        return files
    
    def _scan_recent_documents(self) -> List[Dict]:
        """Scan recent documents cache"""
        files = []
        recent_paths = [
            '~/.local/share/recently-used.xbel',
            '~/.recently-used',
            '~/.cache/recent-files'
        ]
        
        for path_pattern in recent_paths:
            files.extend(self._scan_directories([path_pattern], 'Recent documents cache'))
        
        return files
    
    def _scan_browser_history(self) -> List[Dict]:
        """Scan browser history files"""
        files = []
        history_paths = [
            '~/.config/google-chrome/Default/History',
            '~/.mozilla/firefox/*/places.sqlite',
            '~/.config/microsoft-edge/Default/History'
        ]
        
        for path_pattern in history_paths:
            files.extend(self._scan_directories([path_pattern], 'Browser history'))
        
        return files
    
    def _scan_browser_cookies(self) -> List[Dict]:
        """Scan browser cookie files"""
        files = []
        cookie_paths = [
            '~/.config/google-chrome/Default/Cookies',
            '~/.mozilla/firefox/*/cookies.sqlite',
            '~/.config/microsoft-edge/Default/Cookies'
        ]
        
        for path_pattern in cookie_paths:
            files.extend(self._scan_directories([path_pattern], 'Browser cookies'))
        
        return files
    
    def _scan_directories(self, dir_patterns: List[str], description: str) -> List[Dict]:
        """Generic directory scanner"""
        files = []
        
        for pattern in dir_patterns:
            expanded_pattern = os.path.expanduser(pattern)
            
            try:
                for path in glob.glob(expanded_pattern):
                    if os.path.isfile(path):
                        try:
                            stat = os.stat(path)
                            files.append({
                                'path': path,
                                'size': stat.st_size,
                                'description': description
                            })
                        except (OSError, IOError):
                            continue
                    elif os.path.isdir(path):
                        # Scan directory contents
                        for root, dirs, file_list in os.walk(path):
                            for file_name in file_list:
                                file_path = os.path.join(root, file_name)
                                try:
                                    stat = os.stat(file_path)
                                    files.append({
                                        'path': file_path,
                                        'size': stat.st_size,
                                        'description': description
                                    })
                                except (OSError, IOError):
                                    continue
            except Exception as e:
                print(f"Error scanning {pattern}: {e}")
                continue
        
        return files

    def _scan_temp_files(self) -> List[Dict]:
        """Scan for temporary files"""
        files = []
        
        for temp_dir in self.temp_dirs:
            expanded_dir = os.path.expanduser(temp_dir)
            if os.path.exists(expanded_dir) and os.path.isdir(expanded_dir):
                try:
                    # Special handling for Downloads - only old files
                    if 'Downloads' in temp_dir:
                        files.extend(self._scan_old_downloads(expanded_dir))
                        continue
                    
                    # Special handling for single files
                    if os.path.isfile(expanded_dir):
                        try:
                            stat = os.stat(expanded_dir)
                            files.append({
                                'path': expanded_dir,
                                'size': stat.st_size,
                                'category': 'temp',
                                'last_modified': stat.st_mtime,
                                'description': 'Recently used files list'
                            })
                        except (OSError, PermissionError):
                            pass
                        continue
                    
                    # Regular directory scanning
                    for root, dirs, filenames in os.walk(expanded_dir):
                        # Skip deep nested directories to avoid permission issues
                        depth = root[len(expanded_dir):].count(os.sep)
                        if depth >= 3:
                            dirs[:] = []
                            continue
                            
                        # Skip system and protected directories
                        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {
                            'systemd', 'dbus', 'fontconfig', 'pulse'
                        }]
                        
                        for filename in filenames:
                            # Skip system files and currently used files
                            if (filename.startswith('.') or 
                                filename.endswith(('.lock', '.pid', '.socket')) or
                                filename in {'core', 'lost+found'}):
                                continue
                                
                            file_path = os.path.join(root, filename)
                            try:
                                stat = os.stat(file_path)
                                
                                # Only include files older than 1 hour for temp directories
                                if '/tmp' in root and time.time() - stat.st_mtime < 3600:
                                    continue
                                
                                files.append({
                                    'path': file_path,
                                    'size': stat.st_size,
                                    'category': 'temp',
                                    'last_modified': stat.st_mtime,
                                    'description': f'Temporary file in {os.path.basename(root)}'
                                })
                            except (OSError, PermissionError):
                                continue
                        
                        # Limit number of files to avoid overwhelming the UI
                        if len(files) > 500:
                            break
                            
                except (OSError, PermissionError):
                    continue
        
        return files

    def _scan_old_downloads(self, downloads_dir: str) -> List[Dict]:
        """Scan Downloads folder for old files (30+ days)"""
        files = []
        
        try:
            for filename in os.listdir(downloads_dir):
                file_path = os.path.join(downloads_dir, filename)
                if os.path.isfile(file_path):
                    try:
                        stat = os.stat(file_path)
                        # Only include files older than 30 days
                        if time.time() - stat.st_mtime > 30 * 24 * 3600:
                            files.append({
                                'path': file_path,
                                'size': stat.st_size,
                                'category': 'old_downloads',
                                'last_modified': stat.st_mtime,
                                'description': f'Old download: {filename}'
                            })
                    except (OSError, PermissionError):
                        continue
        except (OSError, PermissionError):
            pass
            
        return files

    def _scan_cache_files(self) -> List[Dict]:
        """Scan for cache files"""
        files = []
        cache_dirs = ['~/.cache']
        
        for cache_dir in cache_dirs:
            expanded_dir = os.path.expanduser(cache_dir)
            if os.path.exists(expanded_dir):
                try:
                    for root, dirs, filenames in os.walk(expanded_dir):
                        # Skip sensitive system caches
                        dirs[:] = [d for d in dirs if d not in {
                            'dconf', 'gstreamer-1.0', 'mesa_shader_cache', 
                            'fontconfig', 'thumbnails'
                        }]
                        
                        # Focus on application caches that are safe to clean
                        safe_cache_dirs = {
                            'google-chrome', 'chromium', 'firefox', 'mozilla',
                            'Microsoft', 'microsoft-edge', 'opera', 'vivaldi',
                            'pip', 'yarn', 'npm', 'composer', 'go-build'
                        }
                        
                        current_dir = os.path.basename(root)
                        if not any(cache_name in root.lower() for cache_name in safe_cache_dirs):
                            continue
                            
                        for filename in filenames:
                            if (filename.startswith('.') or 
                                filename.endswith(('.lock', '.pid', '.log'))):
                                continue
                                
                            file_path = os.path.join(root, filename)
                            try:
                                stat = os.stat(file_path)
                                # Focus on larger cache files (>1KB)
                                if stat.st_size > 1024:
                                    files.append({
                                        'path': file_path,
                                        'size': stat.st_size,
                                        'category': 'cache',
                                        'last_modified': stat.st_mtime,
                                        'description': f'Cache file from {current_dir}'
                                    })
                            except (OSError, PermissionError):
                                continue
                        
                        if len(files) > 300:
                            break
                            
                except (OSError, PermissionError):
                    continue
        
        return files

    def _scan_browser_files(self) -> List[Dict]:
        """Scan for browser cache and temporary files"""
        files = []
        
        for browser, dirs in self.browser_dirs.items():
            for browser_dir in dirs:
                expanded_dir = os.path.expanduser(browser_dir)
                
                # Handle wildcard patterns for Firefox profiles
                if '*' in expanded_dir:
                    import glob
                    matching_dirs = glob.glob(expanded_dir)
                else:
                    matching_dirs = [expanded_dir] if os.path.exists(expanded_dir) else []
                
                for dir_path in matching_dirs:
                    if os.path.exists(dir_path) and os.path.isdir(dir_path):
                        try:
                            for root, dirs_list, filenames in os.walk(dir_path):
                                # Skip subdirectories to avoid going too deep
                                if root != dir_path:
                                    depth = root[len(dir_path):].count(os.sep)
                                    if depth >= 2:
                                        dirs_list[:] = []
                                        continue
                                
                                for filename in filenames:
                                    # Focus on cache files that are safe to delete
                                    if (filename.startswith('.') or 
                                        filename.endswith(('.lock', '.db-wal', '.db-shm')) or
                                        filename in {'LOCK', 'index', 'data_0', 'data_1', 'data_2', 'data_3'}):
                                        continue
                                        
                                    file_path = os.path.join(root, filename)
                                    try:
                                        stat = os.stat(file_path)
                                        # Only include files larger than 1KB
                                        if stat.st_size > 1024:
                                            files.append({
                                                'path': file_path,
                                                'size': stat.st_size,
                                                'category': f'browser_{browser}',
                                                'last_modified': stat.st_mtime,
                                                'description': f'{browser.title()} cache file'
                                            })
                                    except (OSError, PermissionError):
                                        continue
                                
                                if len(files) > 150:
                                    break
                                    
                        except (OSError, PermissionError):
                            continue
        
        return files

    def _scan_system_logs(self) -> List[Dict]:
        """Scan for system log files"""
        files = []
        
        for log_pattern in self.system_logs:
            expanded_pattern = os.path.expanduser(log_pattern)
            
            if '*' in expanded_pattern:
                import glob
                matching_files = glob.glob(expanded_pattern)
            else:
                matching_files = [expanded_pattern] if os.path.exists(expanded_pattern) else []
            
            for file_path in matching_files:
                if os.path.isfile(file_path):
                    try:
                        stat = os.stat(file_path)
                        # Only include logs older than 7 days
                        if time.time() - stat.st_mtime > 7 * 24 * 3600:
                            files.append({
                                'path': file_path,
                                'size': stat.st_size,
                                'category': 'logs',
                                'last_modified': stat.st_mtime
                            })
                    except (OSError, PermissionError):
                        continue
        
        return files

    def _scan_old_files(self) -> List[Dict]:
        """Scan for old files in common locations"""
        files = []
        old_file_dirs = ['~/Downloads', '~/Desktop', '/tmp']
        
        for old_dir in old_file_dirs:
            expanded_dir = os.path.expanduser(old_dir)
            if os.path.exists(expanded_dir):
                try:
                    for filename in os.listdir(expanded_dir):
                        file_path = os.path.join(expanded_dir, filename)
                        if os.path.isfile(file_path):
                            try:
                                stat = os.stat(file_path)
                                # Only include files older than 30 days
                                if time.time() - stat.st_mtime > 30 * 24 * 3600:
                                    files.append({
                                        'path': file_path,
                                        'size': stat.st_size,
                                        'category': 'old_files',
                                        'last_modified': stat.st_mtime
                                    })
                            except (OSError, PermissionError):
                                continue
                except (OSError, PermissionError):
                    continue
        
        return files

    def _scan_gaming_files(self) -> List[Dict]:
        """Scan for gaming-related temporary files"""
        files = []
        gaming_dirs = [
            '~/.steam/logs',
            '~/.local/share/Steam/logs',
            '~/.cache/steam',
            '~/.wine/drive_c/users/*/Temp'
        ]
        
        for gaming_dir in gaming_dirs:
            expanded_dir = os.path.expanduser(gaming_dir)
            
            if '*' in expanded_dir:
                import glob
                matching_dirs = glob.glob(expanded_dir)
            else:
                matching_dirs = [expanded_dir] if os.path.exists(expanded_dir) else []
            
            for dir_path in matching_dirs:
                if os.path.exists(dir_path):
                    try:
                        for root, dirs_list, filenames in os.walk(dir_path):
                            for filename in filenames:
                                file_path = os.path.join(root, filename)
                                try:
                                    stat = os.stat(file_path)
                                    files.append({
                                        'path': file_path,
                                        'size': stat.st_size,
                                        'category': 'gaming',
                                        'last_modified': stat.st_mtime
                                    })
                                except (OSError, PermissionError):
                                    continue
                            
                            if len(files) > 100:
                                break
                                
                    except (OSError, PermissionError):
                        continue
        
        return files

    def clean_files(self, file_paths: List[str]) -> Dict:
        """Clean the specified files"""
        results = {
            'cleaned_files': [],
            'errors': [],
            'freed_space': 0
        }
        
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    # Get file size before deletion
                    file_size = os.path.getsize(file_path)
                    
                    # Remove the file
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    
                    results['cleaned_files'].append(file_path)
                    results['freed_space'] += file_size
                    
                else:
                    results['errors'].append(f"File not found: {file_path}")
                    
            except PermissionError:
                results['errors'].append(f"Permission denied: {file_path}")
            except Exception as e:
                results['errors'].append(f"Error cleaning {file_path}: {str(e)}")
        
        return results

    def create_backup(self, file_paths: List[str]) -> str:
        """Create a backup of files before deletion"""
        backup_dir = os.path.join(tempfile.gettempdir(), 'dexter_backup')
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_info = {
            'timestamp': time.time(),
            'files': []
        }
        
        for file_path in file_paths:
            if os.path.exists(file_path):
                try:
                    # Create backup filename
                    backup_filename = file_path.replace('/', '_').replace('\\', '_')
                    backup_path = os.path.join(backup_dir, backup_filename)
                    
                    # Copy file to backup location
                    shutil.copy2(file_path, backup_path)
                    
                    backup_info['files'].append({
                        'original': file_path,
                        'backup': backup_path
                    })
                    
                except Exception as e:
                    print(f"Failed to backup {file_path}: {e}")
        
        # Save backup info
        backup_info_path = os.path.join(backup_dir, 'backup_info.json')
        with open(backup_info_path, 'w') as f:
            json.dump(backup_info, f, indent=2)
        
        return backup_dir

    def restore_backup(self, backup_dir: str) -> Dict:
        """Restore files from backup"""
        results = {
            'restored_files': [],
            'errors': []
        }
        
        backup_info_path = os.path.join(backup_dir, 'backup_info.json')
        
        if not os.path.exists(backup_info_path):
            results['errors'].append("Backup info file not found")
            return results
        
        try:
            with open(backup_info_path, 'r') as f:
                backup_info = json.load(f)
            
            for file_info in backup_info['files']:
                original_path = file_info['original']
                backup_path = file_info['backup']
                
                if os.path.exists(backup_path):
                    try:
                        # Create parent directories if they don't exist
                        os.makedirs(os.path.dirname(original_path), exist_ok=True)
                        
                        # Restore the file
                        shutil.copy2(backup_path, original_path)
                        results['restored_files'].append(original_path)
                        
                    except Exception as e:
                        results['errors'].append(f"Failed to restore {original_path}: {e}")
                else:
                    results['errors'].append(f"Backup file not found: {backup_path}")
                    
        except Exception as e:
            results['errors'].append(f"Failed to read backup info: {e}")
        
        return results
