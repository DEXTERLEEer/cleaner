import os
import hashlib
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class DuplicateFinder:
    """Find and manage duplicate files based on content comparison"""
    
    def __init__(self):
        self.hash_cache = {}
        self.scan_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp',  # Images
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',   # Videos
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma',          # Audio
            '.pdf', '.doc', '.docx', '.txt', '.rtf',                  # Documents
            '.zip', '.rar', '.7z', '.tar', '.gz',                     # Archives
            '.exe', '.msi', '.deb', '.rpm',                           # Executables
            '.iso', '.img'                                            # Disk images
        }
    
    def find_duplicates(self, directory: str, min_file_size: int = 1024) -> List[Dict]:
        """
        Find duplicate files in the specified directory
        
        Args:
            directory: Directory path to scan
            min_file_size: Minimum file size in bytes to consider
            
        Returns:
            List of duplicate groups with file information
        """
        try:
            expanded_dir = os.path.expanduser(directory)
            if not os.path.exists(expanded_dir):
                return []
            
            # First pass: Group files by size
            size_groups = self._group_files_by_size(expanded_dir, min_file_size)
            
            # Second pass: Hash files with same size
            duplicate_groups = []
            
            for size, file_paths in size_groups.items():
                if len(file_paths) > 1:  # Only process groups with multiple files
                    hash_groups = self._group_files_by_hash(file_paths)
                    
                    for file_hash, files in hash_groups.items():
                        if len(files) > 1:  # Found duplicates
                            duplicate_group = {
                                'hash': file_hash,
                                'size': size,
                                'files': []
                            }
                            
                            for file_path in files:
                                try:
                                    stat = os.stat(file_path)
                                    duplicate_group['files'].append({
                                        'path': file_path,
                                        'size': stat.st_size,
                                        'last_modified': stat.st_mtime,
                                        'last_accessed': stat.st_atime,
                                        'directory': os.path.dirname(file_path),
                                        'filename': os.path.basename(file_path),
                                        'extension': os.path.splitext(file_path)[1].lower()
                                    })
                                except (OSError, PermissionError):
                                    continue
                            
                            if len(duplicate_group['files']) > 1:
                                duplicate_groups.append(duplicate_group)
            
            # Sort by potential space savings (largest first)
            duplicate_groups.sort(key=lambda g: g['size'] * (len(g['files']) - 1), reverse=True)
            
            return duplicate_groups
            
        except Exception as e:
            print(f"Error finding duplicates: {e}")
            return []
    
    def _group_files_by_size(self, directory: str, min_file_size: int) -> Dict[int, List[str]]:
        """Group files by their size"""
        size_groups = defaultdict(list)
        
        try:
            for root, dirs, files in os.walk(directory):
                # Skip hidden directories and common system directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {
                    '__pycache__', 'node_modules', '.git', '.svn', 'venv', 'env'
                }]
                
                for filename in files:
                    # Skip hidden files and temporary files
                    if filename.startswith('.') or filename.endswith(('.tmp', '.temp', '.swp')):
                        continue
                    
                    file_path = os.path.join(root, filename)
                    
                    try:
                        stat = os.stat(file_path)
                        file_size = stat.st_size
                        
                        # Skip files smaller than minimum size
                        if file_size < min_file_size:
                            continue
                        
                        # Skip empty files
                        if file_size == 0:
                            continue
                        
                        # Check if file extension should be processed
                        file_ext = os.path.splitext(filename)[1].lower()
                        if file_ext and file_ext not in self.scan_extensions:
                            continue
                        
                        size_groups[file_size].append(file_path)
                        
                    except (OSError, PermissionError):
                        continue
        
        except Exception as e:
            print(f"Error grouping files by size: {e}")
        
        return size_groups
    
    def _group_files_by_hash(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """Group files by their MD5 hash"""
        hash_groups = defaultdict(list)
        
        for file_path in file_paths:
            try:
                file_hash = self._get_file_hash(file_path)
                if file_hash:
                    hash_groups[file_hash].append(file_path)
            except Exception as e:
                print(f"Error hashing file {file_path}: {e}")
                continue
        
        return hash_groups
    
    def _get_file_hash(self, file_path: str, chunk_size: int = 8192) -> Optional[str]:
        """
        Calculate MD5 hash of a file
        
        Args:
            file_path: Path to the file
            chunk_size: Size of chunks to read at a time
            
        Returns:
            MD5 hash string or None if error
        """
        # Check cache first
        try:
            stat = os.stat(file_path)
            cache_key = f"{file_path}:{stat.st_size}:{stat.st_mtime}"
            
            if cache_key in self.hash_cache:
                return self.hash_cache[cache_key]
        except (OSError, PermissionError):
            return None
        
        try:
            hash_md5 = hashlib.md5()
            
            with open(file_path, 'rb') as f:
                # For large files, use a progressive hashing approach
                file_size = stat.st_size
                
                if file_size > 100 * 1024 * 1024:  # Files larger than 100MB
                    # Sample-based hashing for very large files
                    # Hash beginning, middle, and end chunks
                    chunks_to_hash = [
                        (0, min(chunk_size * 10, file_size // 3)),  # Beginning
                        (file_size // 2 - chunk_size * 5, chunk_size * 10),  # Middle
                        (max(0, file_size - chunk_size * 10), chunk_size * 10)  # End
                    ]
                    
                    for start_pos, read_size in chunks_to_hash:
                        f.seek(start_pos)
                        chunk = f.read(read_size)
                        if chunk:
                            hash_md5.update(chunk)
                else:
                    # Full file hashing for smaller files
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        hash_md5.update(chunk)
            
            file_hash = hash_md5.hexdigest()
            
            # Cache the result
            self.hash_cache[cache_key] = file_hash
            
            return file_hash
            
        except (OSError, PermissionError, IOError) as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def calculate_savings(self, duplicate_groups: List[Dict]) -> int:
        """
        Calculate potential space savings from removing duplicates
        
        Args:
            duplicate_groups: List of duplicate groups
            
        Returns:
            Total bytes that could be saved
        """
        total_savings = 0
        
        for group in duplicate_groups:
            # Keep one file, remove the rest
            files_to_remove = len(group['files']) - 1
            file_size = group['size']
            total_savings += files_to_remove * file_size
        
        return total_savings
    
    def get_duplicate_tree(self, duplicate_groups: List[Dict]) -> Dict:
        """
        Create a directory tree structure showing duplicates
        
        Args:
            duplicate_groups: List of duplicate groups
            
        Returns:
            Nested dictionary representing directory tree
        """
        tree = {}
        
        for group_idx, group in enumerate(duplicate_groups):
            for file_info in group['files']:
                path_parts = Path(file_info['path']).parts
                current_node = tree
                
                # Build tree structure
                for part in path_parts[:-1]:  # Exclude filename
                    if part not in current_node:
                        current_node[part] = {}
                    current_node = current_node[part]
                
                # Add file info
                filename = path_parts[-1]
                if filename not in current_node:
                    current_node[filename] = []
                
                current_node[filename].append({
                    'group_id': group_idx,
                    'hash': group['hash'],
                    'size': file_info['size'],
                    'last_modified': file_info['last_modified'],
                    'full_path': file_info['path']
                })
        
        return tree
    
    def suggest_files_to_keep(self, duplicate_group: Dict) -> str:
        """
        Suggest which file to keep from a duplicate group
        
        Args:
            duplicate_group: Single duplicate group
            
        Returns:
            Path of suggested file to keep
        """
        files = duplicate_group['files']
        
        if not files:
            return ""
        
        # Scoring criteria (higher score = better to keep)
        scored_files = []
        
        for file_info in files:
            score = 0
            path = file_info['path']
            
            # Prefer files in non-temporary locations
            if '/tmp/' not in path and '/temp/' not in path:
                score += 10
            
            # Prefer files in user directories over system directories
            if '/home/' in path or '/Users/' in path:
                score += 5
            
            # Prefer files with shorter paths (likely in more organized locations)
            score += max(0, 20 - path.count('/'))
            
            # Prefer more recently modified files
            days_old = (time.time() - file_info['last_modified']) / (24 * 3600)
            score += max(0, 10 - days_old / 30)  # Reduce score as file gets older
            
            # Prefer files with common names (less likely to be renamed)
            filename = file_info['filename']
            if not any(char in filename for char in ['_copy', '_duplicate', '(1)', '(2)']):
                score += 5
            
            scored_files.append((score, path, file_info))
        
        # Sort by score (highest first) and return the best file
        scored_files.sort(key=lambda x: x[0], reverse=True)
        
        return scored_files[0][1] if scored_files else files[0]['path']
    
    def get_files_to_remove(self, duplicate_group: Dict) -> List[str]:
        """
        Get list of files that should be removed from a duplicate group
        
        Args:
            duplicate_group: Single duplicate group
            
        Returns:
            List of file paths to remove
        """
        keep_file = self.suggest_files_to_keep(duplicate_group)
        
        files_to_remove = []
        for file_info in duplicate_group['files']:
            if file_info['path'] != keep_file:
                files_to_remove.append(file_info['path'])
        
        return files_to_remove
    
    def remove_duplicates(self, duplicate_groups: List[Dict], 
                         confirm_callback: Optional[callable] = None) -> Dict:
        """
        Remove duplicate files, keeping the best candidate from each group
        
        Args:
            duplicate_groups: List of duplicate groups
            confirm_callback: Optional callback for user confirmation
            
        Returns:
            Results dictionary with removed files and errors
        """
        results = {
            'removed_files': [],
            'kept_files': [],
            'errors': [],
            'space_freed': 0
        }
        
        for group in duplicate_groups:
            try:
                keep_file = self.suggest_files_to_keep(group)
                files_to_remove = self.get_files_to_remove(group)
                
                # Confirm removal if callback provided
                if confirm_callback:
                    if not confirm_callback(group, keep_file, files_to_remove):
                        continue
                
                results['kept_files'].append(keep_file)
                
                # Remove duplicate files
                for file_path in files_to_remove:
                    try:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        
                        results['removed_files'].append(file_path)
                        results['space_freed'] += file_size
                        
                    except (OSError, PermissionError) as e:
                        results['errors'].append(f"Failed to remove {file_path}: {e}")
                        
            except Exception as e:
                results['errors'].append(f"Error processing duplicate group: {e}")
        
        return results
    
    def export_duplicate_report(self, duplicate_groups: List[Dict], 
                              output_path: str = "duplicate_report.txt") -> bool:
        """
        Export duplicate file report to text file
        
        Args:
            duplicate_groups: List of duplicate groups
            output_path: Path for output file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("DEXTER PC Optimizer - Duplicate Files Report\n")
                f.write("=" * 50 + "\n")
                f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total duplicate groups: {len(duplicate_groups)}\n")
                f.write(f"Potential space savings: {self._format_bytes(self.calculate_savings(duplicate_groups))}\n\n")
                
                for idx, group in enumerate(duplicate_groups, 1):
                    f.write(f"Duplicate Group #{idx}\n")
                    f.write(f"File size: {self._format_bytes(group['size'])}\n")
                    f.write(f"Hash: {group['hash']}\n")
                    f.write(f"Files ({len(group['files'])}):\n")
                    
                    for file_info in group['files']:
                        modified_time = time.strftime('%Y-%m-%d %H:%M:%S', 
                                                    time.localtime(file_info['last_modified']))
                        f.write(f"  - {file_info['path']} (modified: {modified_time})\n")
                    
                    # Suggest which file to keep
                    suggested_keep = self.suggest_files_to_keep(group)
                    f.write(f"Suggested to keep: {suggested_keep}\n")
                    f.write("-" * 30 + "\n\n")
            
            return True
            
        except Exception as e:
            print(f"Error exporting report: {e}")
            return False
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes into human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    def clear_cache(self):
        """Clear the hash cache"""
        self.hash_cache.clear()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'cached_files': len(self.hash_cache),
            'cache_size_mb': sum(len(k) + len(v) for k, v in self.hash_cache.items()) / (1024 * 1024)
        }
