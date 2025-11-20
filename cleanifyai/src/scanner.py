"""
Scanner Module

Handles directory scanning and file discovery.
This module will walk through directories and collect files that need
to be organized, while filtering out system files and hidden files.
"""

from pathlib import Path
from typing import List

from utils import is_system_file


def scan_directory(directory_path: str) -> List[Path]:
    """
    Scan a directory and return a list of files that should be processed.
    
    This function:
    - Scans only the top-level directory (not subdirectories) for Phase 1
    - Collects all files (not directories)
    - Filters out hidden files (starting with '.')
    - Filters out system files (e.g., .DS_Store, .gitignore)
    - Returns a list of Path objects for each file
    
    Args:
        directory_path: Path to the directory to scan (string or Path)
        
    Returns:
        List of Path objects representing files to be processed
        
    Note:
        Phase 1 only scans top-level files. Recursive scanning will be
        added in a future phase if needed.
    """
    # Convert input to Path object
    base_path = Path(directory_path)
    
    if not base_path.exists() or not base_path.is_dir():
        return []
    
    # Collect files from the base directory only (top-level)
    # Phase 1: We only organize files directly in the target directory,
    # not files in subdirectories
    files = []
    
    try:
        for item in base_path.iterdir():
            if item.is_file() and not should_skip_file(item):
                files.append(item)
    except PermissionError:
        # Skip directories we don't have permission to read
        pass
    
    return files


def should_skip_file(file_path: Path) -> bool:
    """
    Determine if a file should be skipped during scanning.
    
    Files are skipped if they:
    - Are hidden (name starts with '.')
    - Are system files (.DS_Store, .gitignore, etc.)
    
    Args:
        file_path: Path object of the file to check
        
    Returns:
        True if file should be skipped, False otherwise
    """
    # Use the utility function to check for system files
    return is_system_file(file_path)
