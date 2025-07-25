import os
import shutil
import tempfile
import time
import json
import glob
import platform
import subprocess
from pathlib import Path
from typing import List, Dict, Callable, Optional

class PCCleaner:
    """Core PC cleaning functionality"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        
        # Set up platform-specific paths
        if self.platform == 'windows':
            self._setup_windows_paths()
        else:
            self._setup_unix_paths()
        
        # Browser specific cleaning
        self.browser_cleaning = {
            'history': True,
            'cookies': True,
            'passwords': False,  # Disabled by default for safety
            'autofill': True,
            'session_data': True
        }

    def _setup_windows_paths(self):
        """Setup Windows-specific cleaning paths"""
        # Get Windows environment variables
        temp_dir = os.environ.get('TEMP', 'C:\\Windows\\Temp')
        user_profile = os.environ.get('USERPROFILE', 'C:\\Users\\Default')
        appdata = os.environ.get('APPDATA', os.path.join(user_profile, 'AppData\\Roaming'))
        local_appdata = os.environ.get('LOCALAPPDATA', os.path.join(user_profile, 'AppData\\Local'))
        
        self.temp_dirs = [
            temp_dir,
            'C:\\Windows\\Temp',
            os.path.join(user_profile, 'AppData\\Local\\Temp'),
            os.path.join(user_profile, 'Downloads'),
            os.path.join(user_profile, 'AppData\\LocalLow\\Temp'),
            'C:\\Windows\\Prefetch',
            'C:\\Windows\\SoftwareDistribution\\Download',
        ]
        
        self.browser_dirs = {
            'chrome': [
                os.path.join(local_appdata, 'Google\\Chrome\\User Data\\Default\\Cache'),
                os.path.join(local_appdata, 'Google\\Chrome\\User Data\\Default\\Code Cache'),
                os.path.join(local_appdata, 'Google\\Chrome\\User Data\\Default\\GPUCache'),
                os.path.join(local_appdata, 'Google\\Chrome\\User Data\\Default\\Service Worker\\CacheStorage'),
                os.path.join(local_appdata, 'Google\\Chrome\\User Data\\Default\\Application Cache'),
                os.path.join(local_appdata, 'Google\\Chrome\\User Data\\Default\\Storage\\ext'),
            ],
            'firefox': [
                os.path.join(local_appdata, 'Mozilla\\Firefox\\Profiles'),
                os.path.join(appdata, 'Mozilla\\Firefox\\Profiles'),
            ],
            'edge': [
                os.path.join(local_appdata, 'Microsoft\\Edge\\User Data\\Default\\Cache'),
                os.path.join(local_appdata, 'Microsoft\\Edge\\User Data\\Default\\Code Cache'),
                os.path.join(local_appdata, 'Microsoft\\Edge\\User Data\\Default\\GPUCache'),
                os.path.join(local_appdata, 'Microsoft\\Edge\\User Data\\Default\\Service Worker\\CacheStorage'),
            ],
            'brave': [
                os.path.join(local_appdata, 'BraveSoftware\\Brave-Browser\\User Data\\Default\\Cache'),
                os.path.join(local_appdata, 'BraveSoftware\\Brave-Browser\\User Data\\Default\\Code Cache'),
                os.path.join(local_appdata, 'BraveSoftware\\Brave-Browser\\User Data\\Default\\GPUCache'),
            ],
            'opera': [
                os.path.join(appdata, 'Opera Software\\Opera Stable\\Cache'),
                os.path.join(local_appdata, 'Opera Software\\Opera Stable\\Cache'),
                os.path.join(local_appdata, 'Opera Software\\Opera GX Stable\\Cache'),
            ]
        }
        
        self.system_logs = [
            'C:\\Windows\\Logs',
            'C:\\Windows\\debug',
            'C:\\Windows\\Minidump',
            'C:\\Windows\\Memory.dmp',
            os.path.join(user_profile, 'AppData\\Local\\CrashDumps'),
        ]
        
        # Advanced cleaning categories
        self.advanced_dirs = {
            'directx_cache': [
                os.path.join(user_profile, 'AppData\\Local\\D3DSCache'),
                os.path.join(user_profile, 'AppData\\Local\\NVIDIA\\DXCache'),
                os.path.join(user_profile, 'AppData\\Local\\AMD\\DxCache'),
                'C:\\Windows\\DirectX.log',
            ],
            'nvidia_cache': [
                os.path.join(user_profile, 'AppData\\Local\\NVIDIA\\GLCache'),
                os.path.join(user_profile, 'AppData\\Local\\NVIDIA\\DXCache'),
                os.path.join(user_profile, 'AppData\\Local\\NVIDIA\\NvBackend\\ApplicationOntology\\data\\wrappers'),
                os.path.join(local_appdata, 'NVIDIA\\NvBackend\\Packages\\NvTelemetry'),
                os.path.join(local_appdata, 'NVIDIA Corporation\\NvTelemetry'),
            ],
            'thumbnail_cache': [
                os.path.join(local_appdata, 'Microsoft\\Windows\\Explorer\\thumbcache_*.db'),
                os.path.join(local_appdata, 'Microsoft\\Windows\\Explorer\\iconcache_*.db'),
            ],
            'windows_logs': [
                'C:\\Windows\\Logs',
                'C:\\Windows\\debug\\WIA',
                'C:\\Windows\\ServiceProfiles\\LocalService\\AppData\\Local\\Temp',
                'C:\\Windows\\System32\\LogFiles',
            ],
            'crash_dumps': [
                'C:\\Windows\\Minidump',
                'C:\\Windows\\memory.dmp',
                os.path.join(local_appdata, 'CrashDumps'),
                os.path.join(temp_dir, '*.dmp'),
            ],
            'windows_defender': [
                'C:\\ProgramData\\Microsoft\\Windows Defender\\Scans\\History',
                'C:\\ProgramData\\Microsoft\\Windows Defender\\Support',
                'C:\\ProgramData\\Microsoft\\Windows Defender\\Quarantine',
                'C:\\ProgramData\\Microsoft\\Windows Defender\\Support\\MPLog-*.log',
            ],
            'java_cache': [
                os.path.join(local_appdata, 'Sun\\Java\\Deployment\\cache'),
                os.path.join(appdata, 'Sun\\Java\\Deployment\\cache'),
                os.path.join(user_profile, '.java\\deployment\\cache'),
            ],
            'onedrive_cache': [
                os.path.join(local_appdata, 'Microsoft\\OneDrive\\logs'),
                os.path.join(local_appdata, 'Microsoft\\OneDrive\\settings\\Personal\\logs'),
                os.path.join(local_appdata, 'Microsoft\\OneDrive\\setup\\logs'),
            ],
            'event_logs': [
                'C:\\Windows\\System32\\winevt\\Logs',
            ],
            'font_cache': [
                'C:\\Windows\\ServiceProfiles\\LocalService\\AppData\\Local\\FontCache',
                'C:\\Windows\\System32\\FNTCACHE.DAT',
                os.path.join(user_profile, 'AppData\\Local\\Microsoft\\Windows\\INetCache\\IE\\*'),
            ],
            'store_cache': [
                os.path.join(local_appdata, 'Packages\\Microsoft.WindowsStore_*\\LocalCache'),
                os.path.join(local_appdata, 'Packages\\Microsoft.WindowsStore_*\\TempState'),
                os.path.join(local_appdata, 'Microsoft\\Windows\\INetCache\\*'),
            ],
            'update_cache': [
                'C:\\Windows\\SoftwareDistribution\\Download',
                'C:\\Windows\\SoftwareDistribution\\DataStore\\Logs',
                'C:\\$Windows.~BT',
                'C:\\$Windows.~WS',
            ],
            'icon_cache': [
                os.path.join(local_appdata, 'Microsoft\\Windows\\Explorer\\iconcache_*.db'),
                os.path.join(local_appdata, 'Microsoft\\Windows\\Explorer\\thumbcache_*.db'),
                os.path.join(local_appdata, 'IconCache.db'),
            ]
        }
        
        # Gaming platform cache directories
        self.gaming_dirs = {
            'steam_cache': [
                os.path.join(user_profile, 'AppData\\Local\\Steam\\htmlcache'),
                'C:\\Program Files (x86)\\Steam\\appcache',
                'C:\\Program Files (x86)\\Steam\\depotcache',
                'C:\\Program Files (x86)\\Steam\\logs',
                'C:\\Program Files (x86)\\Steam\\steamapps\\temp',
                'C:\\Program Files (x86)\\Steam\\steamapps\\downloading',
            ],
            'epic_games_cache': [
                os.path.join(local_appdata, 'Epic Games\\Launcher\\Derived Data Cache'),
                os.path.join(local_appdata, 'Epic Games\\Launcher\\Intermediate'),
                os.path.join(local_appdata, 'Epic Games\\Launcher\\Saved\\Logs'),
                os.path.join(local_appdata, 'Epic Games\\Launcher\\Saved\\Crashes'),
            ],
            'origin_cache': [
                os.path.join(local_appdata, 'Origin\\ThinSetup'),
                os.path.join(local_appdata, 'Origin\\Logs'),
                os.path.join(appdata, 'Origin\\Telemetry'),
                os.path.join(appdata, 'Origin\\Logs'),
                'C:\\ProgramData\\Origin\\Logs',
            ],
            'adobe_cache': [
                os.path.join(appdata, 'Adobe\\Common\\Media Cache Files'),
                os.path.join(appdata, 'Adobe\\Common\\Media Cache'),
                os.path.join(appdata, 'Adobe\\Acrobat\\Distiller\\Cache'),
                os.path.join(appdata, 'Adobe\\CameraRaw\\Cache'),
            ],
            'spotify_cache': [
                os.path.join(local_appdata, 'Spotify\\Storage'),
                os.path.join(local_appdata, 'Spotify\\Data'),
                os.path.join(appdata, 'Spotify\\Browser\\Cache'),
            ],
            'discord_cache': [
                os.path.join(appdata, 'Discord\\Cache'),
                os.path.join(appdata, 'Discord\\Code Cache'),
                os.path.join(appdata, 'Discord\\GPUCache'),
                os.path.join(appdata, 'Discord\\Crashpad'),
            ],
            'teams_cache': [
                os.path.join(appdata, 'Microsoft\\Teams\\Cache'),
                os.path.join(appdata, 'Microsoft\\Teams\\Code Cache'),
                os.path.join(appdata, 'Microsoft\\Teams\\GPUCache'),
                os.path.join(appdata, 'Microsoft\\Teams\\Logs'),
            ],
            'vscode_cache': [
                os.path.join(appdata, 'Code\\Cache'),
                os.path.join(appdata, 'Code\\CachedData'),
                os.path.join(appdata, 'Code\\GPUCache'),
                os.path.join(appdata, 'Code\\logs'),
                os.path.join(appdata, 'Code\\Crashpad'),
            ],
            'npm_cache': [
                os.path.join(appdata, 'npm-cache'),
                os.path.join(user_profile, '.npm\\_cacache'),
            ]
        }

    def _setup_unix_paths(self):
        """Setup Unix-like system cleaning paths"""
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
            elif category in self.advanced_dirs:
                # Allow direct category access
                files.extend(self._scan_directories(self.advanced_dirs[category], 
                                                  self._get_category_description(category)))
            elif category in self.gaming_dirs:
                # Allow direct category access
                files.extend(self._scan_directories(self.gaming_dirs[category], 
                                                  self._get_category_description(category)))
            
            # Update progress
            if progress_callback:
                for i in range(len(files)):
                    progress_callback((i + 1) / max(1, len(files)) * 100)
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
        
        # Add Windows-specific basic cleaning
        if self.platform == 'windows':
            files.extend(self._scan_windows_basic())
        
        return files
    
    def _scan_windows_basic(self) -> List[Dict]:
        """Windows-specific basic cleaning"""
        files = []
        
        # Windows Recycle Bin
        try:
            user_profile = os.environ.get('USERPROFILE', 'C:\\Users\\Default')
            recycle_bin_paths = [
                'C:\\$Recycle.Bin',
                os.path.join(user_profile, '$Recycle.Bin')
            ]
            
            for path in recycle_bin_paths:
                if os.path.exists(path):
                    files.extend(self._scan_directories([path], 'Recycle Bin'))
        except Exception as e:
            print(f"Error scanning Recycle Bin: {e}")
        
        # Windows Prefetch
        try:
            prefetch_path = 'C:\\Windows\\Prefetch'
            if os.path.exists(prefetch_path):
                files.extend(self._scan_directories([prefetch_path], 'Windows Prefetch Files'))
        except Exception as e:
            print(f"Error scanning Prefetch: {e}")
        
        # Windows Temporary Internet Files
        try:
            user_profile = os.environ.get('USERPROFILE', 'C:\\Users\\Default')
            internet_cache = os.path.join(user_profile, 'AppData\\Local\\Microsoft\\Windows\\INetCache')
            if os.path.exists(internet_cache):
                files.extend(self._scan_directories([internet_cache], 'Temporary Internet Files'))
        except Exception as e:
            print(f"Error scanning Internet Cache: {e}")
        
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
        
        if self.platform == 'windows':
            downloads_path = os.path.join(os.environ.get('USERPROFILE', 'C:\\Users\\Default'), 'Downloads')
        else:
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
        
        if self.platform == 'windows':
            clipboard_paths = [
                os.path.join(os.environ.get('TEMP', 'C:\\Windows\\Temp'), 'clipboard*'),
                os.path.join(os.environ.get('LOCALAPPDATA', 'C:\\Users\\Default\\AppData\\Local'), 'Microsoft\\Windows\\Clipboard'),
            ]
        else:
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
        
        if self.platform == 'windows':
            recent_paths = [
                os.path.join(os.environ.get('APPDATA', 'C:\\Users\\Default\\AppData\\Roaming'), 'Microsoft\\Windows\\Recent'),
                os.path.join(os.environ.get('APPDATA', 'C:\\Users\\Default\\AppData\\Roaming'), 'Microsoft\\Office\\Recent'),
            ]
        else:
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
        
        if self.platform == 'windows':
            local_appdata = os.environ.get('LOCALAPPDATA', 'C:\\Users\\Default\\AppData\\Local')
            appdata = os.environ.get('APPDATA', 'C:\\Users\\Default\\AppData\\Roaming')
            
            history_paths = [
                os.path.join(local_appdata, 'Google\\Chrome\\User Data\\Default\\History'),
                os.path.join(local_appdata, 'Microsoft\\Edge\\User Data\\Default\\History'),
                os.path.join(local_appdata, 'BraveSoftware\\Brave-Browser\\User Data\\Default\\History'),
                os.path.join(appdata, 'Mozilla\\Firefox\\Profiles\\*\\places.sqlite'),
                os.path.join(appdata, 'Opera Software\\Opera Stable\\History'),
            ]
        else:
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
        
        if self.platform == 'windows':
            local_appdata = os.environ.get('LOCALAPPDATA', 'C:\\Users\\Default\\AppData\\Local')
            appdata = os.environ.get('APPDATA', 'C:\\Users\\Default\\AppData\\Roaming')
            
            cookie_paths = [
                os.path.join(local_appdata, 'Google\\Chrome\\User Data\\Default\\Cookies'),
                os.path.join(local_appdata, 'Microsoft\\Edge\\User Data\\Default\\Cookies'),
                os.path.join(local_appdata, 'BraveSoftware\\Brave-Browser\\User Data\\Default\\Cookies'),
                os.path.join(appdata, 'Mozilla\\Firefox\\Profiles\\*\\cookies.sqlite'),
                os.path.join(appdata, 'Opera Software\\Opera Stable\\Cookies'),
            ]
        else:
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
            if self.platform == 'windows':
                # Handle Windows paths
                if '*' in pattern:
                    matching_paths = glob.glob(pattern)
                else:
                    matching_paths = [pattern] if os.path.exists(pattern) else []
            else:
                # Handle Unix paths with ~ expansion
                expanded_pattern = os.path.expanduser(pattern)
                matching_paths = glob.glob(expanded_pattern)
            
            for path in matching_paths:
                try:
                    if os.path.isfile(path):
                        try:
                            stat = os.stat(path)
                            files.append({
                                'path': path,
                                'size': stat.st_size,
                                'description': description
                            })
                        except (OSError, IOError, PermissionError):
                            continue
                    elif os.path.isdir(path):
                        # Scan directory contents
                        for root, dirs, file_list in os.walk(path):
                            # Skip deep nested directories to avoid permission issues
                            depth = root[len(path):].count(os.sep)
                            if depth >= 3:
                                dirs[:] = []
                                continue
                                
                            for file_name in file_list:
                                file_path = os.path.join(root, file_name)
                                try:
                                    stat = os.stat(file_path)
                                    files.append({
                                        'path': file_path,
                                        'size': stat.st_size,
                                        'description': description
                                    })
                                except (OSError, IOError, PermissionError):
                                    continue
                except Exception as e:
                    print(f"Error scanning {path}: {e}")
                    continue
        
        return files

    def _scan_temp_files(self) -> List[Dict]:
        """Scan for temporary files"""
        files = []
        
        for temp_dir in self.temp_dirs:
            if self.platform == 'windows':
                # Handle Windows paths
                if os.path.exists(temp_dir) and os.path.isdir(temp_dir):
                    expanded_dir = temp_dir
                else:
                    continue
            else:
                # Handle Unix paths with ~ expansion
                expanded_dir = os.path.expanduser(temp_dir)
                if not os.path.exists(expanded_dir) or not os.path.isdir(expanded_dir):
                    continue
            
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
                    if self.platform == 'windows':
                        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {
                            'System Volume Information', '$RECYCLE.BIN', 'Windows', 'Program Files', 'Program Files (x86)'
                        }]
                    else:
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
                            if ('/tmp' in root or '\\Temp' in root) and time.time() - stat.st_mtime < 3600:
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
        
        if self.platform == 'windows':
            cache_dirs = [
                os.path.join(os.environ.get('LOCALAPPDATA', 'C:\\Users\\Default\\AppData\\Local'), 'Temp'),
                os.path.join(os.environ.get('LOCALAPPDATA', 'C:\\Users\\Default\\AppData\\Local'), 'Microsoft\\Windows\\INetCache'),
                os.path.join(os.environ.get('LOCALAPPDATA', 'C:\\Users\\Default\\AppData\\Local'), 'Microsoft\\Windows\\WebCache'),
            ]
        else:
            cache_dirs = ['~/.cache']
        
        for cache_dir in cache_dirs:
            if self.platform == 'windows':
                expanded_dir = cache_dir
            else:
                expanded_dir = os.path.expanduser(cache_dir)
                
            if os.path.exists(expanded_dir):
                try:
                    for root, dirs, filenames in os.walk(expanded_dir):
                        # Skip sensitive system caches
                        if self.platform == 'windows':
                            dirs[:] = [d for d in dirs if d not in {
                                'System Volume Information', '$RECYCLE.BIN', 'Windows'
                            }]
                        else:
                            dirs[:] = [d for d in dirs if d not in {
                                'dconf', 'gstreamer-1.0', 'mesa_shader_cache', 
                                'fontconfig', 'thumbnails'
                            }]
                        
                        # Focus on application caches that are safe to clean
                        safe_cache_dirs = {
                            'google-chrome', 'chromium', 'firefox', 'mozilla',
                            'Microsoft', 'microsoft-edge', 'opera', 'vivaldi',
                            'pip', 'yarn', 'npm', 'composer', 'go-build',
                            'Chrome', 'Edge', 'Firefox', 'Opera', 'Brave'
                        }
                        
                        current_dir = os.path.basename(root)
                        if not any(cache_name.lower() in root.lower() for cache_name in safe_cache_dirs):
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
                if self.platform == 'windows':
                    # Handle Windows paths
                    if '*' in browser_dir:
                        matching_dirs = glob.glob(browser_dir)
                    else:
                        matching_dirs = [browser_dir] if os.path.exists(browser_dir) else []
                else:
                    # Handle Unix paths with ~ expansion
                    expanded_dir = os.path.expanduser(browser_dir)
                    
                    # Handle wildcard patterns for Firefox profiles
                    if '*' in expanded_dir:
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
            if self.platform == 'windows':
                # Handle Windows paths
                if '*' in log_pattern:
                    matching_files = glob.glob(log_pattern)
                else:
                    matching_files = [log_pattern] if os.path.exists(log_pattern) else []
            else:
                # Handle Unix paths with ~ expansion
                expanded_pattern = os.path.expanduser(log_pattern)
                
                if '*' in expanded_pattern:
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
                                'last_modified': stat.st_mtime,
                                'description': 'System log file'
                            })
                    except (OSError, PermissionError):
                        continue
        
        return files

    def _scan_old_files(self) -> List[Dict]:
        """Scan for old files in common locations"""
        files = []
        
        if self.platform == 'windows':
            old_file_dirs = [
                os.path.join(os.environ.get('USERPROFILE', 'C:\\Users\\Default'), 'Downloads'),
                os.path.join(os.environ.get('USERPROFILE', 'C:\\Users\\Default'), 'Desktop'),
                os.environ.get('TEMP', 'C:\\Windows\\Temp')
            ]
        else:
            old_file_dirs = ['~/Downloads', '~/Desktop', '/tmp']
        
        for old_dir in old_file_dirs:
            if self.platform == 'windows':
                expanded_dir = old_dir
            else:
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
                                        'last_modified': stat.st_mtime,
                                        'description': 'Old file (30+ days)'
                                    })
                            except (OSError, PermissionError):
                                continue
                except (OSError, PermissionError):
                    continue
        
        return files

    def _scan_gaming_files(self) -> List[Dict]:
        """Scan for gaming-related temporary files"""
        files = []
        
        if self.platform == 'windows':
            gaming_dirs = [
                'C:\\Program Files (x86)\\Steam\\logs',
                'C:\\Program Files (x86)\\Steam\\dumps',
                os.path.join(os.environ.get('LOCALAPPDATA', 'C:\\Users\\Default\\AppData\\Local'), 'Temp\\*game*'),
                os.path.join(os.environ.get('LOCALAPPDATA', 'C:\\Users\\Default\\AppData\\Local'), 'CrashDumps'),
            ]
        else:
            gaming_dirs = [
                '~/.steam/logs',
                '~/.local/share/Steam/logs',
                '~/.cache/steam',
                '~/.wine/drive_c/users/*/Temp'
            ]
        
        for gaming_dir in gaming_dirs:
            if self.platform == 'windows':
                # Handle Windows paths
                if '*' in gaming_dir:
                    matching_dirs = glob.glob(gaming_dir)
                else:
                    matching_dirs = [gaming_dir] if os.path.exists(gaming_dir) else []
            else:
                # Handle Unix paths with ~ expansion
                expanded_dir = os.path.expanduser(gaming_dir)
                
                if '*' in expanded_dir:
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
                                        'last_modified': stat.st_mtime,
                                        'description': 'Gaming temporary file'
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
                    try:
                        file_size = os.path.getsize(file_path)
                    except (OSError, PermissionError):
                        file_size = 0
                    
                    # Remove the file
                    if os.path.isfile(file_path):
                        try:
                            os.remove(file_path)
                            results['cleaned_files'].append(file_path)
                            results['freed_space'] += file_size
                        except (OSError, PermissionError) as e:
                            # Try with admin privileges if available
                            if self.platform == 'windows':
                                try:
                                    # Use Windows command to force delete
                                    subprocess.run(['cmd', '/c', 'del', '/f', '/q', file_path], 
                                                  capture_output=True, 
                                                  text=True)
                                    if not os.path.exists(file_path):
                                        results['cleaned_files'].append(file_path)
                                        results['freed_space'] += file_size
                                    else:
                                        results['errors'].append(f"Permission denied: {file_path}")
                                except Exception as e2:
                                    results['errors'].append(f"Error cleaning {file_path}: {str(e2)}")
                            else:
                                results['errors'].append(f"Permission denied: {file_path}")
                    elif os.path.isdir(file_path):
                        try:
                            shutil.rmtree(file_path)
                            results['cleaned_files'].append(file_path)
                            results['freed_space'] += file_size
                        except (OSError, PermissionError) as e:
                            # Try with admin privileges if available
                            if self.platform == 'windows':
                                try:
                                    # Use Windows command to force delete directory
                                    subprocess.run(['cmd', '/c', 'rmdir', '/s', '/q', file_path], 
                                                  capture_output=True, 
                                                  text=True)
                                    if not os.path.exists(file_path):
                                        results['cleaned_files'].append(file_path)
                                        results['freed_space'] += file_size
                                    else:
                                        results['errors'].append(f"Permission denied: {file_path}")
                                except Exception as e2:
                                    results['errors'].append(f"Error cleaning {file_path}: {str(e2)}")
                            else:
                                results['errors'].append(f"Permission denied: {file_path}")
                    
                else:
                    results['errors'].append(f"File not found: {file_path}")
                    
            except PermissionError:
                results['errors'].append(f"Permission denied: {file_path}")
            except Exception as e:
                results['errors'].append(f"Error cleaning {file_path}: {str(e)}")
        
        # Special Windows-specific cleanups
        if self.platform == 'windows':
            self._perform_windows_specific_cleanups(results)
        
        return results
    
    def _perform_windows_specific_cleanups(self, results: Dict):
        """Perform Windows-specific cleanups that require special handling"""
        try:
            # Clear DNS cache
            try:
                subprocess.run(['ipconfig', '/flushdns'], 
                              capture_output=True, 
                              text=True)
                results['cleaned_files'].append("DNS Cache")
            except Exception as e:
                results['errors'].append(f"Error flushing DNS cache: {str(e)}")
            
            # Clear Windows thumbnail cache
            try:
                subprocess.run(['taskkill', '/f', '/im', 'explorer.exe'], 
                              capture_output=True, 
                              text=True)
                
                local_appdata = os.environ.get('LOCALAPPDATA', 'C:\\Users\\Default\\AppData\\Local')
                thumb_cache_files = glob.glob(os.path.join(local_appdata, 'Microsoft\\Windows\\Explorer\\thumbcache_*.db'))
                
                for file in thumb_cache_files:
                    try:
                        os.remove(file)
                        results['cleaned_files'].append(file)
                    except:
                        pass
                
                # Restart explorer
                subprocess.Popen(['explorer.exe'])
                
            except Exception as e:
                results['errors'].append(f"Error clearing thumbnail cache: {str(e)}")
            
            # Clear Windows icon cache
            try:
                local_appdata = os.environ.get('LOCALAPPDATA', 'C:\\Users\\Default\\AppData\\Local')
                icon_cache_file = os.path.join(local_appdata, 'IconCache.db')
                
                if os.path.exists(icon_cache_file):
                    try:
                        os.remove(icon_cache_file)
                        results['cleaned_files'].append(icon_cache_file)
                    except:
                        pass
            except Exception as e:
                results['errors'].append(f"Error clearing icon cache: {str(e)}")
            
            # Clear clipboard
            try:
                subprocess.run(['cmd', '/c', 'echo off | clip'], 
                              capture_output=True, 
                              text=True)
                results['cleaned_files'].append("Clipboard")
            except Exception as e:
                results['errors'].append(f"Error clearing clipboard: {str(e)}")
                
        except Exception as e:
            results['errors'].append(f"Error in Windows-specific cleanups: {str(e)}")

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
                    if self.platform == 'windows':
                        backup_filename = file_path.replace(':', '_').replace('\\', '_')
                    else:
                        backup_filename = file_path.replace('/', '_')
                        
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