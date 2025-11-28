"""
Mover Module - Phase 1

This module handles the actual file moving operations.
It safely moves files to their destination folders, creating directories as needed.

WHAT IT DOES:
- Creates destination folders if they don't exist
- Handles filename conflicts (renames duplicates)
- Moves files from one location to another
- Supports dry-run mode (preview without actually moving)

CONTRACTS:
All functions use strict type hints to ensure type safety and readability.
Functions return bool for success/failure, Path objects for paths, and None for optional values.
"""

import shutil
from pathlib import Path
from typing import Optional, Union


def move_file(
    file_path: Path,
    destination: Union[Path, str],
    dry_run: bool = False,
    display_dest: Optional[str] = None
) -> bool:
    """
    Move a file to its destination folder with conflict resolution.
    
    This is the main function that actually moves files. It performs the following steps:
    1. Creates the destination folder if it doesn't exist
    2. Checks for filename conflicts (if file already exists)
    3. Renames the file if there's a conflict (e.g., Screenshot(1).png)
    4. Moves the file (or just shows what would happen in dry-run mode)
    
    The function handles both relative and absolute paths, and automatically creates
    parent directories as needed. In dry-run mode, it only prints what would happen
    without actually moving any files.
    
    Examples:
        >>> from pathlib import Path
        >>> move_file(Path("Screenshot.png"), Path("~/Desktop/Screenshots"), dry_run=False)
        True  # File moved successfully
        
        >>> move_file(Path("doc.pdf"), Path("/Users/john/Desktop/Documents"), dry_run=True)
        [DRY RUN] Would move: doc.pdf → Documents/
        True  # Preview only, no actual move
    
    Args:
        file_path: The file to move. Must be a Path object pointing to an existing file.
            Example: Path("Screenshot.png")
        destination: Where to move the file. Can be a Path object or string.
            If it's a directory path, the file will be moved into that directory.
            Example: Path("~/Desktop/Screenshots") or "~/Desktop/Screenshots"
        dry_run: If True, only show what would happen without actually moving files.
            Defaults to False.
        display_dest: Optional display name for output messages. If provided, this
            name will be used in log messages instead of the actual destination path.
            Defaults to None (uses destination.name).
        
    Returns:
        bool: True if the operation was successful (or would be successful in dry-run),
            False if there was an error (e.g., permission denied, invalid path).
        
    Raises:
        No exceptions are raised. All errors are caught and False is returned.
        Error messages are printed to stdout.
        
    Note:
        - The function automatically handles filename conflicts by appending (1), (2), etc.
        - Parent directories are created automatically if they don't exist.
        - The operation is atomic (uses shutil.move() which is safe).
    """
    # Convert destination to Path object if it's a string
    if not isinstance(destination, Path):
        destination = Path(str(destination))
    
    # Step 1: Make sure the destination folder exists
    # If it doesn't exist, create it (and any parent folders needed)
    if not ensure_destination(destination):
        print(f"[ERROR] Could not create destination directory: {destination}")
        return False
    
    # Step 2: Check for filename conflicts
    # If a file with the same name already exists, we need to rename it
    # Example: If "Screenshot.png" exists, rename to "Screenshot(1).png"
    final_dest_file = _resolve_conflict(file_path, destination)
    
    # Step 3: Handle dry-run mode (preview mode)
    if dry_run:
        # In dry-run mode, we just print what we would do
        dest_display = display_dest if display_dest else destination.name
        
        if final_dest_file != destination / file_path.name:
            # File would be renamed due to conflict
            conflict_name = final_dest_file.name
            print(f"[DRY RUN] Would move: {file_path.name} → {dest_display}/{conflict_name}")
        else:
            # File would be moved normally
            print(f"[DRY RUN] Would move: {file_path.name} → {dest_display}/")
        return True
    
    # Step 4: Actually move the file
    try:
        # shutil.move() is Python's built-in function for moving files
        # It's atomic (safe) and handles cross-device moves
        shutil.move(str(file_path), str(final_dest_file))
        return True
    except (OSError, shutil.Error) as e:
        # If something goes wrong, print an error and return False
        print(f"[ERROR] Failed to move {file_path.name}: {e}")
        return False


def ensure_destination(destination_path: Union[Path, str]) -> bool:
    """
    Ensure a destination directory exists, creating it if necessary.
    
    This function creates folders if they don't exist, including all parent directories.
    It's equivalent to running "mkdir -p" in the terminal. If the directory already
    exists, the function does nothing and returns True.
    
    Examples:
        >>> from pathlib import Path
        >>> ensure_destination(Path("~/Desktop/Screenshots"))
        True  # Directory created or already exists
        
        >>> ensure_destination("/Users/john/Documents/Projects")
        True  # Directory created with all parent directories
    
    Args:
        destination_path: The folder path that should exist. Can be a Path object
            or string. Parent directories will be created automatically if needed.
            Example: Path("~/Desktop/Screenshots") or "~/Desktop/Screenshots"
        
    Returns:
        bool: True if the folder exists or was successfully created,
            False if there was an error (e.g., permission denied, invalid path).
        
    Raises:
        No exceptions are raised. All errors are caught and False is returned.
        Error messages are printed to stdout.
        
    Note:
        - Uses Path.mkdir(parents=True, exist_ok=True) internally.
        - Handles PermissionError and OSError gracefully.
    """
    # Convert to Path object if it's a string
    if not isinstance(destination_path, Path):
        destination_path = Path(str(destination_path))
    
    try:
        # mkdir(parents=True) creates the folder and all parent folders
        # exist_ok=True means "don't error if it already exists"
        destination_path.mkdir(parents=True, exist_ok=True)
        return True
    except (PermissionError, OSError) as e:
        # If we don't have permission or something else goes wrong, return False
        print(f"[ERROR] Could not create directory {destination_path}: {e}")
        return False


def resolve_destination(base_path: Union[Path, str], destination: Union[str, Path]) -> Path:
    """
    Resolve a destination path relative to a base path with security checks.
    
    This function takes a destination path (relative or absolute) and resolves it
    relative to a base path. It includes security checks to prevent path traversal
    attacks (e.g., "../../etc/passwd").
    
    If the destination is an absolute path, it checks if it's within the base_path.
    If not, it treats it as a relative path for security.
    
    Examples:
        >>> from pathlib import Path
        >>> base = Path("/Users/john/Desktop")
        >>> resolve_destination(base, "Screenshots")
        Path("/Users/john/Desktop/Screenshots")
        
        >>> resolve_destination(base, "../Documents")
        Path("/Users/john/Documents")  # Resolved relative to base
        
        >>> resolve_destination(base, "/Users/john/Desktop/Projects")
        Path("/Users/john/Desktop/Projects")  # Absolute path within base
    
    Args:
        base_path: The base directory path. Can be a Path object or string.
            This is the root directory that all destinations should be relative to.
            Example: Path("~/Desktop") or "/Users/john/Desktop"
        destination: The destination folder path. Can be relative or absolute.
            If absolute, must be within base_path for security.
            Example: "Screenshots" or "/Users/john/Desktop/Screenshots"
        
    Returns:
        Path: A fully resolved absolute Path object pointing to the destination.
            The path is normalized and symlinks are resolved.
        
    Note:
        - Includes security checks to prevent directory traversal attacks.
        - Handles both Python 3.9+ (is_relative_to) and older versions.
        - All paths are resolved to absolute paths.
    """
    # Convert to Path objects
    if not isinstance(base_path, Path):
        base_path = Path(str(base_path))
    dest_path = Path(str(destination))
    
    # If destination is an absolute path, check if it's within base_path (security)
    if dest_path.is_absolute():
        try:
            # Resolve both paths to handle symlinks
            resolved_base = base_path.resolve()
            resolved_dest = dest_path.resolve()
            
            # Check if destination is within base_path (security check)
            if resolved_dest.is_relative_to(resolved_base):
                return resolved_dest
            else:
                # Security: if absolute path tries to escape, treat as relative
                return (base_path / destination).resolve()
        except (AttributeError, ValueError):
            # Python < 3.9 compatibility: use string comparison
            resolved_base = str(base_path.resolve())
            resolved_dest = str(dest_path.resolve())
            if resolved_dest.startswith(resolved_base):
                return dest_path.resolve()
            else:
                # Security: treat as relative
                return (base_path / destination).resolve()
    else:
        # Relative path: combine with base_path
        # Example: "Screenshots" + "~/Desktop" = "~/Desktop/Screenshots"
        return (base_path / destination).resolve()


def _resolve_conflict(file_path: Union[Path, str], destination_dir: Union[Path, str]) -> Path:
    """
    Resolve filename conflicts by generating a unique filename.
    
    If a file with the same name already exists in the destination directory,
    this function finds a new name by appending (1), (2), (3), etc. to the
    filename stem (before the extension) until a free name is found.
    
    The function preserves the original file extension and only modifies the
    filename stem. It will keep incrementing the number until it finds a
    filename that doesn't exist.
    
    Examples:
        >>> from pathlib import Path
        >>> file = Path("Screenshot.png")
        >>> dest = Path("/Users/john/Desktop/Screenshots")
        >>> # If "Screenshot.png" exists in dest:
        >>> _resolve_conflict(file, dest)
        Path("/Users/john/Desktop/Screenshots/Screenshot(1).png")
        
        >>> # If both "Screenshot.png" and "Screenshot(1).png" exist:
        >>> _resolve_conflict(file, dest)
        Path("/Users/john/Desktop/Screenshots/Screenshot(2).png")
    
    Args:
        file_path: The file we want to move. Can be a Path object or string.
            The filename from this path will be used to generate the new name.
            Example: Path("Screenshot.png")
        destination_dir: The destination directory where the file will be moved.
            Can be a Path object or string. The function checks for existing
            files in this directory.
            Example: Path("/Users/john/Desktop/Screenshots")
        
    Returns:
        Path: A Path object pointing to a conflict-free filename in the
            destination directory. If no conflict exists, returns the original
            filename. Otherwise, returns a filename with (N) appended.
        
    Note:
        - The function will loop indefinitely if all possible names are taken
          (unlikely in practice, but theoretically possible).
        - Only modifies the filename stem, preserves the extension.
        - Case-sensitive: "File.png" and "file.png" are considered different.
    """
    # Convert to Path objects
    if not isinstance(file_path, Path):
        file_path = Path(str(file_path))
    if not isinstance(destination_dir, Path):
        destination_dir = Path(str(destination_dir))
    
    # First, try the original filename
    dest_file = destination_dir / file_path.name
    
    # If that file doesn't exist, we're good!
    if not dest_file.exists():
        return dest_file
    
    # There's a conflict! We need to rename it
    # Extract the name and extension separately
    # Example: "Screenshot.png" -> stem="Screenshot", suffix=".png"
    stem = file_path.stem
    suffix = file_path.suffix
    
    # Try appending (1), (2), (3), etc. until we find a free name
    counter = 1
    while True:
        # Create new name: "Screenshot(1).png", "Screenshot(2).png", etc.
        new_name = f"{stem}({counter}){suffix}"
        new_path = destination_dir / new_name
        
        # If this name is free, use it!
        if not new_path.exists():
            return new_path
        
        # This name is taken too, try the next number
        counter += 1
