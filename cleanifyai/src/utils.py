"""
Utility Module (Phase 1)

Contains minimal helper functions used across CleanifyAI during Phase 1.

Important:
- This module intentionally includes only path normalization and 
  system-file detection.
- Logging utilities and file-size formatting will be added in Phase 3.
"""

import os
from pathlib import Path


def normalize_path(path: str) -> Path:
    """
    Normalize a path string to a Path object.
    
    This function:
    - Expands `~` to user home directory
    - Converts the string to a Path object
    - Uses `.resolve()` to canonicalize the path (resolve symlinks, make absolute)
    - Does NOT check if the path exists (that is the CLI's responsibility)
    
    Args:
        path: Path string (may include ~ for home directory)
        
    Returns:
        Normalized Path object (absolute, resolved)
    """
    # Expand ~ to user home directory
    expanded = os.path.expanduser(path)
    # Convert to Path and resolve to absolute path
    return Path(expanded).resolve()


def is_system_file(file_path: Path) -> bool:
    """
    Check if a file is a system file that should be ignored during scanning.
    
    This function identifies:
    - Hidden files: Files whose name starts with '.' (e.g., .gitignore, .hidden)
    - macOS system metadata files:
      * .DS_Store
      * .AppleDouble
      * .LSOverride
    - Windows system metadata files:
      * Thumbs.db
      * desktop.ini
    
    Args:
        file_path: Path object of the file to check
        
    Returns:
        True if file is a system file and should be ignored, False otherwise
    """
    filename = file_path.name
    
    # Check for hidden files (starting with '.')
    if filename.startswith('.'):
        return True
    
    # macOS system files
    macos_system_files = {'.DS_Store', '.AppleDouble', '.LSOverride'}
    if filename in macos_system_files:
        return True
    
    # Windows system files
    windows_system_files = {'Thumbs.db', 'desktop.ini'}
    if filename in windows_system_files:
        return True
    
    return False
