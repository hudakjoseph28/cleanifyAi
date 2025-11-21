"""
Scanner Module - Phase 1

This module is responsible for finding files on your Desktop.
It looks through a directory and returns a list of all files that should be processed.

WHAT IT DOES:
- Scans a directory (like ~/Desktop)
- Finds all files in that directory (only top-level, not in subfolders)
- Filters out system files and hidden files (like .DS_Store)
- Returns a list of files ready to be organized
"""

from pathlib import Path
from typing import List

from utils import is_system_file


def scan_directory(directory_path: str) -> List[Path]:
    """
    Scan a directory and return a list of files that should be processed.
    
    HOW IT WORKS:
    1. Takes a directory path (like "~/Desktop")
    2. Looks at every item in that directory
    3. Keeps only files (not folders)
    4. Skips system files and hidden files
    5. Returns a list of Path objects
    
    Example:
        Input: "~/Desktop"
        Output: [Path("Screenshot.png"), Path("document.pdf"), ...]
    
    Args:
        directory_path: The folder to scan (as a string)
        
    Returns:
        A list of Path objects, one for each file found
    """
    # Convert the string path to a Path object (easier to work with)
    base_path = Path(directory_path)
    
    # Safety check: make sure the path exists and is actually a directory
    if not base_path.exists() or not base_path.is_dir():
        return []  # Return empty list if invalid
    
    # This list will hold all the files we find
    files = []
    
    try:
        # Loop through every item in the directory
        # iterdir() gives us all items (files and folders) in the directory
        for item in base_path.iterdir():
            # Only process files, not directories
            # Also skip system files (like .DS_Store)
            if item.is_file() and not should_skip_file(item):
                files.append(item)
    except PermissionError:
        # If we don't have permission to read the directory, just skip it
        pass
    
    # Return the list of files we found
    return files


def should_skip_file(file_path: Path) -> bool:
    """
    Determine if a file should be skipped (not processed).
    
    We skip files that are:
    - Hidden files (names starting with '.', like .gitignore)
    - System files (like .DS_Store on macOS)
    
    Args:
        file_path: The file to check
        
    Returns:
        True if we should skip this file, False if we should process it
    """
    # Use the utility function to check if it's a system file
    return is_system_file(file_path)
