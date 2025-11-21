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
"""

import argparse
import os
import sys
from pathlib import Path

# Add the src directory to Python's path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import our custom modules
from classifier import classify_file, load_rules
from scanner import scan_directory
from mover import move_file, resolve_destination


def parse_arguments():
    """
    Parse command-line arguments from the user.
    
    This function sets up what arguments the script accepts:
    - --path: Which folder to scan (defaults to ~/Desktop)
    - --dry-run: Preview mode - shows what would happen without actually moving files
    
    Returns:
        An object containing the parsed arguments
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


def main():
    """
    Main function - this is where the program starts.
    
    STEP-BY-STEP PROCESS:
    1. Get command-line arguments (which folder to scan, dry-run mode?)
    2. Check that the folder exists and is valid
    3. Load the rules from rules.json (tells us how to identify screenshots)
    4. Scan the folder to find all files
    5. For each file:
       - Check if it matches our screenshot rules
       - If yes: move it to Screenshots folder
       - If no: skip it
    6. Print a summary of what happened
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
