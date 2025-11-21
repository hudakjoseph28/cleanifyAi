"""
Utility Module - Phase 1

Helper functions used throughout the program.
These are small, reusable functions that don't fit into the main modules.

WHAT IT DOES:
- Checks if a file is a system file (should be ignored)
- Normalizes file paths
"""

import os
from pathlib import Path


def normalize_path(path: str) -> Path:
    """
    Convert a path string to a normalized Path object.
    
    This function:
    - Expands ~ to the user's home directory
    - Converts to a Path object
    - Resolves to an absolute path
    
    Example:
        Input: "~/Desktop"
        Output: Path("/Users/josephhudak/Desktop")
    
    Args:
        path: A path string (may include ~)
        
    Returns:
        A normalized Path object
    """
    # Expand ~ to home directory
    expanded = os.expanduser(path)
    # Convert to Path and resolve to absolute path
    return Path(expanded).resolve()


def is_system_file(file_path: Path) -> bool:
    """
    Check if a file is a system file that should be ignored.
    
    System files are files that the operating system uses internally.
    We don't want to organize these files, so we skip them.
    
    Examples of system files:
    - Hidden files (starting with '.', like .gitignore, .DS_Store)
    - macOS metadata files (.DS_Store, .AppleDouble)
    - Windows metadata files (Thumbs.db, desktop.ini)
    
    Args:
        file_path: The file to check
        
    Returns:
        True if it's a system file (should be skipped), False otherwise
    """
    filename = file_path.name
    
    # Check for hidden files (names starting with '.')
    # These are typically system or configuration files
    if filename.startswith('.'):
        return True
    
    # macOS system files that should be ignored
    macos_system_files = {'.DS_Store', '.AppleDouble', '.LSOverride'}
    if filename in macos_system_files:
        return True
    
    # Windows system files that should be ignored
    windows_system_files = {'Thumbs.db', 'desktop.ini'}
    if filename in windows_system_files:
        return True
    
    # Not a system file, so we should process it
    return False
