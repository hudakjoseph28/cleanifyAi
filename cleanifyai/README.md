# CleanifyAI - File Organization Tool

A file organization tool that automatically organizes files using natural language instructions and rule-based classification.

## What This Does

**Phase 1 (CLI):** A command-line tool that organizes screenshots on your Desktop.

**Phase 2 (GUI):** A full GUI application with natural language instruction parsing, interactive rule management, and real-time file preview.

## Features

### Phase 1 - CLI Features
- ✅ Scans Desktop for files (top-level only)
- ✅ Identifies screenshots based on filename and extension
- ✅ Moves screenshots to `~/Desktop/Screenshots` folder
- ✅ Dry-run mode to preview changes safely
- ✅ Automatic conflict resolution (renames duplicates)
- ✅ Automatically creates the Screenshots folder if it doesn't exist

### Phase 2 - GUI Features
- ✅ Full GUI interface built with PySide6 (Qt for Python)
- ✅ Natural language instruction parsing
- ✅ Interactive rule creation and editing
- ✅ Real-time file preview with before/after view
- ✅ Async file scanning and operations (no UI freezing)
- ✅ Tabbed interface for easy navigation
- ✅ Menu bar and toolbar for quick actions

## Installation

### Requirements
- Python 3.8+
- PySide6 (for GUI)

### Setup

1. **Clone or download the project** to your computer
   - If using Git: `git clone https://github.com/hudakjoseph28/cleanifyAi.git`
   - Or download the ZIP file and extract it

2. **Navigate to the project directory** in Terminal:
   ```bash
   cd path/to/cleanifyAi
   ```
   (Replace `path/to/cleanifyAi` with wherever you saved the project)

3. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```
   Or if you prefer using a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **You're ready to go!** See usage instructions below.

## Usage

### Opening the Application via Terminal

**Step 1: Open Terminal**
- On macOS: Press `Cmd + Space`, type "Terminal", and press Enter
- On Linux: Press `Ctrl + Alt + T` or find Terminal in your applications
- On Windows: Use Command Prompt or PowerShell

**Step 2: Navigate to the Project Directory**
```bash
# Navigate to wherever you cloned/downloaded the CleanifyAI project
# For example, if it's in your Desktop:
cd ~/Desktop/cleanifyAi

# Or if it's in your Documents:
cd ~/Documents/cleanifyAi

# Or if you cloned it from GitHub:
cd ~/path/to/cleanifyAi
```

**Step 3: Choose Your Interface**

#### Option A: Run the GUI (Recommended for Phase 2)
```bash
# Make sure you're in the project root directory (where you see the cleanifyai/ folder)
python3 cleanifyai/gui/main.py
```

#### Option B: Run the CLI
```bash
# Navigate to cleanifyai directory
cd cleanifyai

# Dry run mode (preview without moving files)
python3 cleanify.py --path ~/Desktop --dry-run

# Actually organize files
python3 cleanify.py --path ~/Desktop
```

### CLI Usage (Phase 1)

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

### GUI Usage (Phase 2)

**Start the GUI application:**

```bash
# Make sure you're in the project root directory (where you see the cleanifyai/ folder)
# Navigate to your project location first, for example:
# cd ~/Desktop/cleanifyAi
# or wherever you have the project

# Then run the GUI
python3 cleanifyai/gui/main.py
```

**Using the GUI:**

1. **Select a Directory**: Click "📂 Scan Directory" in the toolbar or use File → Open Directory
2. **Create Rules**: 
   - Use the "Instructions & Rules" tab
   - Enter natural language instructions in plain English:
     - "move all screenshots to Screenshots"
     - "put simulator files in my sim folder"
     - "organize PDF files into Documents"
     - "take the simulator files on my desktop and move them to a new folder called simulator"
   - CleanifyAI will show you what it understood before you confirm
   - Or manually create/edit rules using the rule editor form
3. **Preview Files**: Switch to the "File Preview" tab to see which files will be organized
4. **Run Cleanup**: Click "✨ Run Cleanup" to organize the files

## Project Structure

```
cleanifyai/
├── cleanify.py          # CLI entry point (Phase 1)
├── gui/
│   ├── main.py          # GUI entry point (Phase 2)
│   ├── main_window.py   # Main application window
│   ├── instruction_input.py  # Natural language input widget
│   ├── rule_editor.py   # Rule creation/editing widget
│   ├── file_preview.py  # File preview widget
│   ├── workers.py       # Async worker threads
│   └── components/      # Reusable GUI components
├── core/
│   ├── rules_engine.py  # Rule management engine
│   ├── nlp_parser.py    # Natural language parser
│   └── file_operations.py  # File operations wrapper
├── src/                 # Phase 1 core modules
│   ├── scanner.py       # File scanning
│   ├── classifier.py    # File classification
│   ├── mover.py         # File moving
│   └── utils.py         # Utility functions
├── config/
│   └── rules.json       # Rule configuration file
└── README.md            # This file
```

## Configuration

Rules are defined in `config/rules.json`. Each rule specifies:
- **name**: Descriptive name for the rule
- **match**: Matching criteria (contains, extensions, pattern)
- **destination**: Target folder path

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

## Natural Language Instructions

The GUI supports **casual, everyday language** - just talk to it like you would to a friend! Examples:

**Casual Instructions (All Supported):**
- `"move all screenshots to Screenshots"`
- `"put simulator files in my sim folder"`
- `"organize PDF files into Documents"`
- `"send Java files to my coding folder"`
- `"take the simulator files on my desktop and move them to a new folder called simulator"`
- `"put all images into Images folder"`

**The parser understands:**
- Flexible phrasing (you don't need exact keywords)
- Category names (images → .png/.jpg, documents → .pdf/.docx, code → .java/.py)
- Casual destination phrases ("my folder", "new folder called X", "to X")
- Synonyms (move, put, send, organize all mean the same thing)

The parser converts your natural language into structured rules that can be edited and saved.

## Development Status

### Phase 1 - CLI ✅ Complete
- Command-line interface
- File scanning and classification
- File moving with conflict resolution

### Phase 2 - GUI ✅ Complete
- Full GUI interface
- Natural language instruction parsing
- Interactive rule management
- Real-time file preview
- Async operations

### Future Phases
- Background monitoring (automatic organization)
- AI-powered classification using LLMs
- Advanced natural language understanding
- Cross-platform support improvements

## Example Output (CLI)

```
[CleanifyAI] Running in DRY RUN mode.
[CleanifyAI] Scanning folder: /Users/yourname/Desktop

[CleanifyAI] Loaded 5 rule(s) from config.

[CleanifyAI] Found 7 file(s).

[DRY RUN] Would move: Screenshot 2025-11-20 at 7.27.34 PM.png → Screenshots/
[DRY RUN] Would move: Screenshot 2025-11-20 at 7.27.40 PM.png → Screenshots/
[SKIP] document.pdf (no matching rule)

[CleanifyAI] Summary: 2 classified, 5 skipped
[CleanifyAI] Dry-run complete. No files were moved.
```

## License

This project is open source and available for use.
