# CleanifyAI - Phase 1: Screenshot Organizer

A simple command-line tool that automatically organizes screenshots on your Desktop.

## What This Does

This is **Phase 1** of CleanifyAI - a screenshot organizer. It:
- Scans your Desktop for screenshot files
- Identifies screenshots (files with "screenshot" in the name and .png/.jpg extensions)
- Moves them into a `Screenshots` folder on your Desktop
- Handles duplicate files by renaming them (e.g., `Screenshot(1).png`)

## How It Works

```
User runs cleanify.py
    ↓
1. Parse command-line arguments
    ↓
2. Load rules from rules.json
    ↓
3. Scan directory for files (scanner.py)
    ↓
4. For each file:
    - Classify it (classifier.py)
    - Move it if matched (mover.py)
    ↓
5. Print summary
```

## Project Structure

```
cleanifyai/
├── cleanify.py          # Main CLI entry point - starts the program
├── config/
│   └── rules.json       # Configuration file - defines how to identify screenshots
├── src/
│   ├── scanner.py       # Finds files on your Desktop
│   ├── classifier.py    # Determines if a file is a screenshot
│   ├── mover.py         # Moves files to the Screenshots folder
│   └── utils.py         # Helper functions
└── README.md            # This file
```

## Usage

**From the project root directory** (`cleanifyAi/`):

```bash
# Navigate to the cleanifyai directory first
cd cleanifyai

# Dry run mode (see what would be done without moving files)
python3 cleanify.py --path ~/Desktop --dry-run

# Actually organize screenshots on Desktop
python3 cleanify.py --path ~/Desktop

# Organize a different folder
python3 cleanify.py --path ~/Downloads
```

**Or run from the project root without changing directories:**

```bash
# From cleanifyAi/ directory
python3 cleanifyai/cleanify.py --path ~/Desktop --dry-run
python3 cleanifyai/cleanify.py --path ~/Desktop
```

## Features (Phase 1)

- ✅ Scans Desktop for files (top-level only)
- ✅ Identifies screenshots based on filename and extension
- ✅ Moves screenshots to `~/Desktop/Screenshots` folder
- ✅ Dry-run mode to preview changes safely
- ✅ Automatic conflict resolution (renames duplicates)
- ✅ Automatically creates the Screenshots folder if it doesn't exist

## Configuration

Screenshot detection rules are defined in `config/rules.json`. The default rule looks for:
- Files with "screenshot" in the filename (case-insensitive)
- Files with `.png`, `.jpg`, or `.jpeg` extensions
- Moves matching files to the `Screenshots` folder

Example rule:
```json
{
  "name": "Screenshots",
  "match": {
    "contains": ["screenshot"],
    "extensions": [".png", ".jpg", ".jpeg"]
  },
  "destination": "Screenshots"
}
```

## Requirements

- Python 3.8+
- macOS (tested on macOS, may work on other systems)

## Phase 1 Status

✅ **Complete** - Screenshot organizer is fully functional

This phase focuses solely on organizing screenshots. Future phases will add:
- Support for organizing other file types
- Background monitoring (automatic organization)
- GUI interface
- AI-powered classification

## Example Output

```
[CleanifyAI] Running in DRY RUN mode.
[CleanifyAI] Scanning folder: /Users/josephhudak/Desktop

[CleanifyAI] Loaded 5 rule(s) from config.

[CleanifyAI] Found 7 file(s).

[DRY RUN] Would move: Screenshot 2025-11-20 at 7.27.34 PM.png → Screenshots/
[DRY RUN] Would move: Screenshot 2025-11-20 at 7.27.40 PM.png → Screenshots/
[SKIP] document.pdf (no matching rule)

[CleanifyAI] Summary: 2 classified, 5 skipped
[CleanifyAI] Dry-run complete. No files were moved.
```
