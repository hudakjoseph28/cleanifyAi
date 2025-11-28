#!/usr/bin/env python3
"""
CleanifyAI - Phase 1: Screenshot Organizer

A simple command-line tool that automatically organizes screenshots on your Desktop.
This is Phase 1, focused specifically on moving screenshot files into a Screenshots folder.

HOW IT WORKS:
1. You run this script from the command line
2. It scans your Desktop for files
3. It finds screenshots (files with "screenshot" in the name and .png/.jpg extensions)
4. It moves them into ~/Desktop/Screenshots folder
5. It handles conflicts by renaming duplicates (e.g., Screenshot(1).png)

CONTRACTS:
All functions use strict type hints. Main entry point uses argparse for CLI arguments.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

# Add the src directory to Python's path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import our custom modules
from classifier import classify_file, load_rules
from scanner import scan_directory
from mover import move_file, resolve_destination


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments from the user.
    
    This function sets up the argument parser and defines what arguments the script accepts.
    It uses argparse to handle command-line interface with proper help messages and
    type validation.
    
    Supported Arguments:
        --path: Path to the directory to scan and organize. Defaults to ~/Desktop.
            Can be any valid directory path (absolute or relative).
        --dry-run: Preview mode flag. When set, shows what would happen without
            actually moving any files. Useful for testing and verification.
    
    Examples:
        >>> args = parse_arguments()  # Called automatically by argparse
        >>> # Command line: python3 cleanify.py --path ~/Desktop --dry-run
        >>> # args.path = "~/Desktop"
        >>> # args.dry_run = True
    
    Returns:
        argparse.Namespace: An object containing the parsed arguments with attributes:
            - path: str - Directory path to scan (default: ~/Desktop)
            - dry_run: bool - Whether to run in preview mode (default: False)
        
    Note:
        - Uses argparse.ArgumentParser for robust argument parsing
        - Provides automatic help message generation (--help)
        - Validates argument types and provides helpful error messages
    """
    parser = argparse.ArgumentParser(
        description="CleanifyAI Phase 1 - Organize screenshots on your Desktop",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Allow user to specify which folder to scan (default is Desktop)
    parser.add_argument(
        "--path",
        type=str,
        default=str(Path.home() / "Desktop"),
        help="Path to the directory to scan and organize (default: ~/Desktop)"
    )
    
    # Dry-run mode lets you see what would happen without actually moving files
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually moving files"
    )
    
    return parser.parse_args()


def main() -> None:
    """
    Main entry point for the CleanifyAI CLI application.
    
    This function orchestrates the entire file organization process:
    1. Parses command-line arguments (directory path, dry-run mode)
    2. Validates that the target directory exists and is accessible
    3. Loads classification rules from config/rules.json
    4. Scans the directory for files (top-level only)
    5. Classifies each file using the loaded rules
    6. Moves matching files to their destination folders (or previews in dry-run)
    7. Prints a summary of operations performed
    
    The function handles errors gracefully and provides informative output at each step.
    In dry-run mode, it only shows what would happen without actually moving files.
    
    Examples:
        Run in dry-run mode to preview changes:
        $ python3 cleanify.py --path ~/Desktop --dry-run
        
        Actually organize files:
        $ python3 cleanify.py --path ~/Desktop
        
        Organize a different directory:
        $ python3 cleanify.py --path ~/Downloads
    
    Returns:
        None: This function doesn't return a value. It exits the program with:
            - Exit code 0: Success
            - Exit code 1: Error (invalid path, permission denied, etc.)
        
    Raises:
        SystemExit: Exits with code 1 if the target directory is invalid or inaccessible.
            All other errors are handled gracefully with error messages.
        
    Note:
        - Uses the rules.json configuration file for classification rules
        - Only processes top-level files (doesn't scan subdirectories)
        - Automatically creates destination folders if they don't exist
        - Handles filename conflicts by auto-renaming (e.g., Screenshot(1).png)
        - Provides detailed console output for all operations
    """
    # Step 1: Parse command-line arguments
    args = parse_arguments()
    
    # Step 2: Convert the path to a Path object and make sure it's absolute
    # Example: "~/Desktop" becomes "/Users/josephhudak/Desktop"
    target_path = Path(args.path).expanduser().resolve()
    
    # Step 3: Validate that the path exists and is actually a directory
    if not target_path.exists():
        print(f"[CleanifyAI] Error: Path does not exist: {target_path}")
        sys.exit(1)
    
    if not target_path.is_dir():
        print(f"[CleanifyAI] Error: Path is not a directory: {target_path}")
        sys.exit(1)
    
    # Step 4: Print status information
    mode = "DRY RUN" if args.dry_run else "LIVE"
    print(f"[CleanifyAI] Running in {mode} mode.")
    print(f"[CleanifyAI] Scanning folder: {target_path}")
    print()
    
    # Step 5: Load the rules from the config file
    # Rules tell us how to identify screenshots (e.g., filename contains "screenshot" and has .png extension)
    config_path = Path(__file__).parent / "config" / "rules.json"
    try:
        rules = load_rules(str(config_path))
        print(f"[CleanifyAI] Loaded {len(rules)} rule(s) from config.")
    except Exception as e:
        print(f"[CleanifyAI] Warning: Could not load rules: {e}")
        print(f"[CleanifyAI] Continuing with empty ruleset.")
        rules = []
    
    print()
    
    # Step 6: Scan the directory to find all files
    # This returns a list of Path objects, one for each file found
    files = scan_directory(str(target_path))
    print(f"[CleanifyAI] Found {len(files)} file(s).")
    print()
    
    # If no files found, we're done
    if len(files) == 0:
        print("[CleanifyAI] No files to organize.")
        return
    
    # Step 7: Process each file
    # We'll track statistics as we go
    classified_count = 0  # Files that matched a rule
    skipped_count = 0     # Files that didn't match any rule
    moved_count = 0       # Files successfully moved
    error_count = 0       # Files that failed to move
    
    # Loop through each file we found
    for file_path in files:
        # Check if this file matches any of our rules (e.g., is it a screenshot?)
        destination = classify_file(file_path, rules, target_path)
        
        if destination:
            # This file matched a rule! We know where it should go
            classified_count += 1
            
            # Convert the destination string (e.g., "Screenshots") to a full path
            # Example: "Screenshots" + "/Users/josephhudak/Desktop" = "/Users/josephhudak/Desktop/Screenshots"
            dest_path = resolve_destination(target_path, destination)
            
            if args.dry_run:
                # Dry-run mode: just show what we would do, don't actually move anything
                move_file(file_path, dest_path, dry_run=True, display_dest=destination)
            else:
                # Live mode: actually move the file
                success = move_file(file_path, dest_path, dry_run=False, display_dest=destination)
                if success:
                    moved_count += 1
                    print(f"[MOVE] {file_path.name} → {destination}/")
                else:
                    error_count += 1
        else:
            # This file didn't match any rules, so we skip it
            skipped_count += 1
            print(f"[SKIP] {file_path.name} (no matching rule)")
    
    # Step 8: Print summary
    print()
    print(f"[CleanifyAI] Summary: {classified_count} classified, {skipped_count} skipped")
    
    if args.dry_run:
        print("[CleanifyAI] Dry-run complete. No files were moved.")
    else:
        print(f"[CleanifyAI] Files moved: {moved_count}, Errors: {error_count}")


# This is the entry point - when you run "python3 cleanify.py", this code runs
if __name__ == "__main__":
    main()
