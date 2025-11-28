"""
Utility Module - Phase 1

Helper functions used throughout the program.
These are small, reusable functions that don't fit into the main modules.

WHAT IT DOES:
- Checks if a file is a system file (should be ignored)
- Normalizes file paths (expands ~, resolves to absolute paths)

CONTRACTS:
All functions use strict type hints. Path functions return Path objects, predicates return bool.
"""

import os
from pathlib import Path
from typing import Union


def normalize_path(path: Union[str, Path]) -> Path:
    """
    Normalize a path string to an absolute Path object.
    
    This function performs path normalization by:
    1. Expanding ~ (tilde) to the user's home directory
    2. Converting to a Path object
    3. Resolving to an absolute path (handles symlinks, relative paths, etc.)
    
    The resulting path is always absolute and normalized, making it safe for
    file operations and comparisons.
    
    Examples:
        >>> normalize_path("~/Desktop")
        Path("/Users/josephhudak/Desktop")
        
        >>> normalize_path("../Documents")
        Path("/Users/josephhudak/Documents")  # Resolved relative to current directory
        
        >>> normalize_path(Path("~/Downloads"))
        Path("/Users/josephhudak/Downloads")
    
    Args:
        path: A path string or Path object. May include:
            - Tilde (~) for home directory expansion
            - Relative paths (../, ./)
            - Symlinks (will be resolved)
            Example: "~/Desktop" or Path("../Documents")
        
    Returns:
        Path: A fully resolved absolute Path object. The path is normalized
            and all symlinks are resolved.
        
    Note:
        - Always returns an absolute path
        - Expands ~ to home directory using os.expanduser()
        - Resolves symlinks and relative components
        - Works on all platforms (Windows, macOS, Linux)
    """
    # Convert to string if it's a Path object
    path_str = str(path)
    
    # Expand ~ to home directory
    expanded = os.expanduser(path_str)
    
    # Convert to Path and resolve to absolute path
    return Path(expanded).resolve()


def is_system_file(file_path: Union[Path, str]) -> bool:
    """
    Check if a file is a system file that should be ignored during organization.
    
    System files are files that the operating system uses internally for metadata,
    configuration, or caching. These files should not be organized by CleanifyAI
    as they are not user-created content.
    
    Files that are considered system files:
    - Hidden files: Any file whose name starts with '.' (Unix/Linux/macOS convention)
        Examples: .gitignore, .env, .DS_Store, .htaccess
    - macOS metadata files: .DS_Store, .AppleDouble, .LSOverride
    - Windows metadata files: Thumbs.db, desktop.ini
    
    Examples:
        >>> from pathlib import Path
        >>> is_system_file(Path(".DS_Store"))
        True  # macOS system file
        
        >>> is_system_file(Path(".gitignore"))
        True  # Hidden file
        
        >>> is_system_file(Path("Thumbs.db"))
        True  # Windows system file
        
        >>> is_system_file(Path("Screenshot.png"))
        False  # Regular user file
        
        >>> is_system_file(Path("document.pdf"))
        False  # Regular user file
    
    Args:
        file_path: The file path to check. Can be a Path object or string.
            Only the filename is checked, not the full path or file contents.
            Example: Path("Screenshot.png") or ".DS_Store"
        
    Returns:
        bool: True if the file is a system file (should be skipped),
            False if it's a regular user file (should be processed).
        
    Note:
        - Only checks the filename, not the file path or contents
        - Case-sensitive: ".DS_Store" is detected, but "ds_store" is not
        - All files starting with '.' are considered hidden/system files
        - Platform-specific: Detects both macOS and Windows system files
    """
    # Convert to Path object if it's a string
    if not isinstance(file_path, Path):
        file_path = Path(str(file_path))
    
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
