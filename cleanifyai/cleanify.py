#!/usr/bin/env python3
"""
CleanifyAI - Phase 1 CLI Entry Point

A command-line tool for automatically organizing files on macOS.
This is the main entry point that parses arguments and orchestrates
the scanning, classification, and moving of files.
"""

import argparse
import os
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from classifier import classify_file, load_rules
from scanner import scan_directory
from mover import move_file, resolve_destination


def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments containing:
            - path: Target directory to scan (default: ~/Desktop)
            - dry_run: Boolean flag for dry-run mode
    """
    parser = argparse.ArgumentParser(
        description="CleanifyAI - Automatically organize files on your Desktop",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--path",
        type=str,
        default=os.path.expanduser("~/Desktop"),
        help="Path to the directory to scan and organize (default: ~/Desktop)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually moving files"
    )
    
    return parser.parse_args()


def main():
    """
    Main entry point for CleanifyAI.
    
    This function:
    1. Parses command-line arguments
    2. Loads classification rules from config
    3. Scans the target directory
    4. Classifies and moves files (or shows what would be done in dry-run mode)
    5. Prints a summary of operations
    """
    args = parse_arguments()
    
    # Expand user path and convert to Path object
    target_path = Path(args.path).expanduser().resolve()
    
    # Validate that the path exists
    if not target_path.exists():
        print(f"[CleanifyAI] Error: Path does not exist: {target_path}")
        sys.exit(1)
    
    if not target_path.is_dir():
        print(f"[CleanifyAI] Error: Path is not a directory: {target_path}")
        sys.exit(1)
    
    # Print status
    mode = "DRY RUN" if args.dry_run else "LIVE"
    print(f"[CleanifyAI] Running in {mode} mode.")
    print(f"[CleanifyAI] Scanning folder: {target_path}")
    print()
    
    # Load rules from config
    config_path = Path(__file__).parent / "config" / "rules.json"
    try:
        rules = load_rules(str(config_path))
        print(f"[CleanifyAI] Loaded {len(rules)} rule(s) from config.")
    except Exception as e:
        print(f"[CleanifyAI] Warning: Could not load rules: {e}")
        print(f"[CleanifyAI] Continuing with empty ruleset.")
        rules = []
    
    print()
    
    # Scan directory for files
    files = scan_directory(str(target_path))
    print(f"[CleanifyAI] Found {len(files)} file(s).")
    print()
    
    if len(files) == 0:
        print("[CleanifyAI] No files to organize.")
        return
    
    # Classify and process each file
    classified_count = 0
    skipped_count = 0
    moved_count = 0
    error_count = 0
    
    for file_path in files:
        destination = classify_file(file_path, rules, target_path)
        
        if destination:
            classified_count += 1
            # Resolve the full destination path
            dest_path = resolve_destination(target_path, destination)
            
            if args.dry_run:
                # move_file will handle the dry-run output
                move_file(file_path, dest_path, dry_run=True, display_dest=destination)
            else:
                # Perform actual file move
                success = move_file(file_path, dest_path, dry_run=False, display_dest=destination)
                if success:
                    moved_count += 1
                    print(f"[MOVE] {file_path.name} → {destination}/")
                else:
                    error_count += 1
        else:
            skipped_count += 1
            print(f"[SKIP] {file_path.name} (no matching rule)")
    
    print()
    print(f"[CleanifyAI] Summary: {classified_count} classified, {skipped_count} skipped")
    
    if args.dry_run:
        print("[CleanifyAI] Dry-run complete. No files were moved.")
    else:
        print(f"[CleanifyAI] Files moved: {moved_count}, Errors: {error_count}")


if __name__ == "__main__":
    main()

