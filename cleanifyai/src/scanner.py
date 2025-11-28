"""
Scanner Module - Phase 1

This module is responsible for finding files in a directory.
It looks through a directory and returns a list of all files that should be processed.

WHAT IT DOES:
- Scans a directory (like ~/Desktop)
- Finds all files in that directory (only top-level, not in subfolders)
- Filters out system files and hidden files (like .DS_Store)
- Returns a list of files ready to be organized

CONTRACTS:
All functions use strict type hints. Returns List[Path] for file lists and bool for predicates.
"""

from pathlib import Path
from typing import List, Union

from utils import is_system_file


def scan_directory(directory_path: Union[str, Path]) -> List[Path]:
    """
    Scan a directory and return a list of files that should be processed.
    
    This function scans a directory for files, filtering out directories, system files,
    and hidden files. It only scans the top-level directory (not subdirectories).
    
    The scanning process:
    1. Validates that the directory exists and is accessible
    2. Iterates through all items in the directory
    3. Filters to keep only regular files (not directories or symlinks)
    4. Skips system files and hidden files using should_skip_file()
    5. Returns a list of Path objects for all valid files
    
    Examples:
        >>> from pathlib import Path
        >>> files = scan_directory("~/Desktop")
        >>> # Returns: [Path("Screenshot.png"), Path("document.pdf"), ...]
        
        >>> files = scan_directory(Path("/Users/john/Documents"))
        >>> # Returns: [Path("report.pdf"), Path("notes.txt"), ...]
        
        >>> files = scan_directory("/nonexistent/path")
        >>> # Returns: []  # Empty list if path doesn't exist
    
    Args:
        directory_path: The directory to scan. Can be a string or Path object.
            The path will be expanded if it contains ~ (home directory).
            Example: "~/Desktop" or Path("/Users/john/Desktop")
        
    Returns:
        List[Path]: A list of Path objects, one for each file found in the directory.
            Returns an empty list if:
            - The directory doesn't exist
            - The path is not a directory
            - Permission is denied
            - No files are found
    
    Note:
        - Only scans top-level files, not subdirectories (non-recursive)
        - Automatically filters out system files (.DS_Store, Thumbs.db, etc.)
        - Filters out hidden files (files starting with '.')
        - Handles PermissionError gracefully (returns empty list)
    """
    # Convert to Path object if it's a string
    if not isinstance(directory_path, Path):
        base_path = Path(str(directory_path))
    else:
        base_path = directory_path
    
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


def should_skip_file(file_path: Union[Path, str]) -> bool:
    """
    Determine if a file should be skipped during scanning.
    
    This function checks if a file is a system file or hidden file that should
    not be processed by CleanifyAI. System files are operating system metadata
    files that users typically don't want to organize.
    
    Files that are skipped:
    - Hidden files: Files whose names start with '.' (e.g., .gitignore, .env)
    - macOS system files: .DS_Store, .AppleDouble, .LSOverride
    - Windows system files: Thumbs.db, desktop.ini
    
    Examples:
        >>> from pathlib import Path
        >>> should_skip_file(Path(".DS_Store"))
        True  # macOS system file
        
        >>> should_skip_file(Path(".gitignore"))
        True  # Hidden file
        
        >>> should_skip_file(Path("Screenshot.png"))
        False  # Regular file, should process
        
        >>> should_skip_file(Path("Thumbs.db"))
        True  # Windows system file
    
    Args:
        file_path: The file path to check. Can be a Path object or string.
            Only the filename is checked, not the full path.
            Example: Path("Screenshot.png") or ".DS_Store"
        
    Returns:
        bool: True if the file should be skipped (is a system/hidden file),
            False if the file should be processed (is a regular user file).
        
    Note:
        - Only checks the filename, not the file contents or metadata
        - Case-sensitive: ".DS_Store" is skipped, but "ds_store" is not
        - Uses the is_system_file() utility function internally
    """
    # Convert to Path object if it's a string
    if not isinstance(file_path, Path):
        file_path = Path(str(file_path))
    
    # Use the utility function to check if it's a system file
    return is_system_file(file_path)
