"""
Mover Module

Handles file moving operations and destination management.
This module safely moves files to their destination folders,
creating directories as needed and handling edge cases.
"""

import shutil
from pathlib import Path
from typing import Optional


def move_file(file_path: Path, destination: Path, dry_run: bool = False, display_dest: Optional[str] = None) -> bool:
    """
    Move a file to its destination folder.
    
    This function:
    - Creates the destination directory if it doesn't exist
    - Handles file name conflicts (auto-renames with (1), (2), etc.)
    - Uses shutil.move() for atomic file operations
    - Returns success status
    
    Args:
        file_path: Path object of the file to move
        destination: Path object of the destination directory
        dry_run: If True, only log what would be done without moving
        display_dest: Optional string for display purposes (relative destination path)
        
    Returns:
        True if move was successful (or would be successful in dry-run),
        False otherwise
        
    Raises:
        OSError: If file system operations fail
    """
    # Convert destination to Path if needed
    if not isinstance(destination, Path):
        destination = Path(destination)
    
    # Ensure destination directory exists
    if not ensure_destination(destination):
        print(f"[ERROR] Could not create destination directory: {destination}")
        return False
    
    # Resolve the final destination file path with conflict handling
    final_dest_file = _resolve_conflict(file_path, destination)
    
    # If dry_run, just log and return
    if dry_run:
        # Use display_dest if provided, otherwise use destination name
        dest_display = display_dest if display_dest else destination.name
        if final_dest_file != destination / file_path.name:
            # File will be renamed due to conflict
            conflict_name = final_dest_file.name
            print(f"[DRY RUN] Would move: {file_path.name} → {dest_display}/{conflict_name}")
        else:
            print(f"[DRY RUN] Would move: {file_path.name} → {dest_display}/")
        return True
    
    # Perform the actual move
    try:
        shutil.move(str(file_path), str(final_dest_file))
        return True
    except (OSError, shutil.Error) as e:
        print(f"[ERROR] Failed to move {file_path.name}: {e}")
        return False


def ensure_destination(destination_path: Path) -> bool:
    """
    Ensure that a destination directory exists, creating it if necessary.
    
    This function:
    - Checks if the destination path exists
    - Creates all parent directories if needed (mkdir -p behavior)
    - Handles permission errors gracefully
    
    Args:
        destination_path: Path object of the destination directory
        
    Returns:
        True if directory exists or was created successfully, False otherwise
    """
    try:
        # Create directory and all parent directories if needed
        destination_path.mkdir(parents=True, exist_ok=True)
        return True
    except (PermissionError, OSError) as e:
        print(f"[ERROR] Could not create directory {destination_path}: {e}")
        return False


def resolve_destination(base_path: Path, destination: str) -> Path:
    """
    Resolve a destination path relative to the base scanning directory.
    
    This function:
    - If destination is absolute → use as-is (but ensure it's within base_path for security)
    - If destination is relative → join with base_path
    - Returns a resolved Path object
    
    Args:
        base_path: Base directory path (e.g., ~/Desktop)
        destination: Destination path (relative or absolute string)
        
    Returns:
        Resolved Path object (absolute, within base_path)
    """
    dest_path = Path(destination)
    
    # If destination is absolute, check if it's within base_path
    if dest_path.is_absolute():
        try:
            # Resolve both paths to handle symlinks
            resolved_base = base_path.resolve()
            resolved_dest = dest_path.resolve()
            # Check if destination is within base_path
            if resolved_dest.is_relative_to(resolved_base):
                return resolved_dest
            else:
                # Security: if absolute path tries to escape, treat as relative
                # Join with base_path instead
                return (base_path / destination).resolve()
        except (AttributeError, ValueError):
            # Python < 3.9 doesn't have is_relative_to, use string comparison
            resolved_base = str(base_path.resolve())
            resolved_dest = str(dest_path.resolve())
            if resolved_dest.startswith(resolved_base):
                return dest_path.resolve()
            else:
                # Security: treat as relative
                return (base_path / destination).resolve()
    else:
        # Relative path: join with base_path
        return (base_path / destination).resolve()


def _resolve_conflict(file_path: Path, destination_dir: Path) -> Path:
    """
    Resolve filename conflicts by appending (1), (2), etc. until a free name is found.
    
    Args:
        file_path: Path object of the source file
        destination_dir: Path object of the destination directory
        
    Returns:
        Path object of the final destination file (with conflict resolution if needed)
    """
    dest_file = destination_dir / file_path.name
    
    # If the file doesn't exist, return the original path
    if not dest_file.exists():
        return dest_file
    
    # Extract name and extension
    stem = file_path.stem
    suffix = file_path.suffix
    
    # Try appending (1), (2), etc.
    counter = 1
    while True:
        new_name = f"{stem}({counter}){suffix}"
        new_path = destination_dir / new_name
        if not new_path.exists():
            return new_path
        counter += 1

