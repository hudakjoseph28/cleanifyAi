"""
Mover Module - Phase 1

This module handles the actual file moving operations.
It safely moves files to their destination folders, creating directories as needed.

WHAT IT DOES:
- Creates destination folders if they don't exist
- Handles filename conflicts (renames duplicates)
- Moves files from one location to another
- Supports dry-run mode (preview without actually moving)
"""

import shutil
from pathlib import Path
from typing import Optional


def move_file(file_path: Path, destination: Path, dry_run: bool = False, display_dest: Optional[str] = None) -> bool:
    """
    Move a file to its destination folder.
    
    This is the main function that actually moves files. It:
    1. Creates the destination folder if it doesn't exist
    2. Checks for filename conflicts (if file already exists)
    3. Renames the file if there's a conflict (e.g., Screenshot(1).png)
    4. Moves the file (or just shows what would happen in dry-run mode)
    
    Example:
        move_file(Path("Screenshot.png"), Path("~/Desktop/Screenshots"), dry_run=False)
        Result: File is moved to ~/Desktop/Screenshots/Screenshot.png
    
    Args:
        file_path: The file to move (e.g., Path("Screenshot.png"))
        destination: Where to move it (e.g., Path("~/Desktop/Screenshots"))
        dry_run: If True, only show what would happen (don't actually move)
        display_dest: Optional display name for output messages
        
    Returns:
        True if successful, False if there was an error
    """
    # Make sure destination is a Path object
    if not isinstance(destination, Path):
        destination = Path(destination)
    
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


def ensure_destination(destination_path: Path) -> bool:
    """
    Make sure a destination directory exists, creating it if necessary.
    
    This function creates folders if they don't exist.
    It's like running "mkdir -p" in the terminal.
    
    Example:
        ensure_destination(Path("~/Desktop/Screenshots"))
        Result: Creates ~/Desktop/Screenshots if it doesn't exist
    
    Args:
        destination_path: The folder that should exist
        
    Returns:
        True if the folder exists or was created, False if there was an error
    """
    try:
        # mkdir(parents=True) creates the folder and all parent folders
        # exist_ok=True means "don't error if it already exists"
        destination_path.mkdir(parents=True, exist_ok=True)
        return True
    except (PermissionError, OSError) as e:
        # If we don't have permission or something else goes wrong, return False
        print(f"[ERROR] Could not create directory {destination_path}: {e}")
        return False


def resolve_destination(base_path: Path, destination: str) -> Path:
    """
    Convert a destination string to a full Path object.
    
    This function takes a relative path (like "Screenshots") and combines it
    with the base path (like "~/Desktop") to get a full path.
    
    Example:
        base_path: Path("~/Desktop")
        destination: "Screenshots"
        Result: Path("~/Desktop/Screenshots")
    
    It also has security checks to prevent moving files outside the base directory.
    
    Args:
        base_path: The base directory (e.g., ~/Desktop)
        destination: The destination folder (relative or absolute)
        
    Returns:
        A full Path object pointing to the destination
    """
    dest_path = Path(destination)
    
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


def _resolve_conflict(file_path: Path, destination_dir: Path) -> Path:
    """
    Handle filename conflicts by renaming the file.
    
    If a file with the same name already exists in the destination,
    this function finds a new name by appending (1), (2), etc.
    
    Example:
        File: "Screenshot.png"
        Destination already has: "Screenshot.png"
        Result: "Screenshot(1).png"
        
        If that exists too: "Screenshot(2).png"
        And so on...
    
    Args:
        file_path: The file we want to move
        destination_dir: The folder we're moving it to
        
    Returns:
        A Path object with a conflict-free filename
    """
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
