# CleanifyAI

#User runs cleanify.py
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






A macOS file organization tool that automatically organizes files on your Desktop (and eventually other folders) by detecting, classifying, and moving them into appropriate folders.

## Phase 1 - CLI Script

This is **Phase 1** of CleanifyAI: a command-line Python script that you can run manually from Terminal to organize files.

### Current Status

This is the **scaffolding phase**. The project structure is in place with placeholder functions, but the actual file scanning, classification, and moving logic will be implemented in subsequent prompts.

### Project Structure

```
cleanifyai/
├── cleanify.py          # Main CLI entry point
├── config/
│   └── rules.json       # Rule configuration file
├── src/
│   ├── scanner.py       # Directory scanning logic
│   ├── classifier.py    # File classification logic
│   ├── mover.py         # File moving logic
│   └── utils.py         # Utility functions
├── logs/                # Directory for log files
└── README.md            # This file
```

### Usage (Once Implemented)

```bash
# Organize files on Desktop
python3 cleanify.py --path ~/Desktop

# Dry run mode (see what would be done without moving files)
python3 cleanify.py --path ~/Desktop --dry-run

# Organize a different folder
python3 cleanify.py --path ~/Downloads
```

### Features (Planned for Phase 1)

- Scan a directory for files
- Classify files based on configurable rules
- Move files to organized folders
- Dry-run mode to preview changes
- Detailed logging of operations

### Configuration

Rules are defined in `config/rules.json`. Each rule specifies:
- **name**: Descriptive name for the rule
- **match**: Matching criteria (contains, pattern, extension, etc.)
- **destination**: Target folder path

### Future Phases

- **Phase 1.5**: Background daemon mode with file watching
- **Phase 2**: UI/Config tool for visual rule creation
- **Phase 3**: Native macOS Swift/SwiftUI app
- **Phase 4**: AI-powered classification using LLMs

### Requirements

- Python 3.8+
- macOS (for Phase 1; cross-platform support possible later)

### Development Status

- ✅ Project structure and scaffolding
- ⏳ File scanning implementation (Prompt #2)
- ⏳ Classification logic (Prompt #2)
- ⏳ File moving and dry-run (Prompt #3)
- ⏳ Logging and error handling (Prompt #3)

