"""
Classifier Module - Phase 1

This module is responsible for deciding where files should go.
It matches files against rules to determine their destination folder.

WHAT IT DOES:
- Loads rules from rules.json (tells us how to identify screenshots)
- Checks if a file matches a rule (e.g., filename contains "screenshot" and has .png extension)
- Returns the destination folder for matching files

EXAMPLE:
    File: "Screenshot 2025-01-15.png"
    Rule: "If filename contains 'screenshot' and extension is .png, move to Screenshots"
    Result: Returns "Screenshots"
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from mover import resolve_destination


def load_rules(config_path: str) -> List[Dict]:
    """
    Load classification rules from the rules.json file.
    
    The rules.json file contains instructions on how to identify different types of files.
    For Phase 1, we mainly care about the screenshot rule.
    
    Example rule structure:
    {
        "name": "Screenshots",
        "match": {
            "contains": ["screenshot"],
            "extensions": [".png", ".jpg"]
        },
        "destination": "Screenshots"
    }
    
    This rule says: "If a filename contains 'screenshot' AND has a .png or .jpg extension,
                     move it to the Screenshots folder"
    
    Args:
        config_path: Path to the rules.json file
        
    Returns:
        A list of rule dictionaries
        
    Raises:
        ValueError: If the rules file is invalid
    """
    try:
        # Open and read the JSON file
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        # If file doesn't exist, return empty list (no rules)
        return []
    except json.JSONDecodeError as e:
        # If JSON is invalid, raise an error
        raise ValueError(f"Invalid JSON in rules file: {e}")
    
    # Extract the rules array from the config
    rules = config.get('rules', [])
    
    # Validate that each rule has the required fields
    for i, rule in enumerate(rules):
        if not isinstance(rule, dict):
            raise ValueError(f"Rule {i} is not a dictionary")
        
        # Every rule needs a name, match criteria, and destination
        if 'name' not in rule:
            raise ValueError(f"Rule {i} is missing 'name' field")
        
        if 'match' not in rule:
            raise ValueError(f"Rule {i} ('{rule.get('name', 'unknown')}') is missing 'match' field")
        
        if 'destination' not in rule:
            raise ValueError(f"Rule {i} ('{rule.get('name', 'unknown')}') is missing 'destination' field")
        
        # Validate the match structure
        match = rule['match']
        if not isinstance(match, dict):
            raise ValueError(f"Rule {i} ('{rule.get('name', 'unknown')}') has invalid 'match' field (must be a dictionary)")
        
        # Make sure the rule has at least one matching criterion
        has_criteria = any(key in match for key in ['contains', 'extensions', 'pattern'])
        if not has_criteria:
            raise ValueError(f"Rule {i} ('{rule.get('name', 'unknown')}') has no valid match criteria")
    
    return rules


def match_rule(file_path: Path, rule: Dict) -> bool:
    """
    Check if a file matches a specific rule's criteria.
    
    This function checks if a file meets all the requirements of a rule.
    Rules can check:
    - contains: Filename contains certain text (e.g., "screenshot")
    - extensions: File has certain extension (e.g., ".png")
    - pattern: Filename matches a regex pattern
    
    Multiple criteria are combined with AND logic (all must match).
    
    Example:
        File: "Screenshot 2025-01-15.png"
        Rule: {"contains": ["screenshot"], "extensions": [".png"]}
        Result: True (filename contains "screenshot" AND has .png extension)
    
    Args:
        file_path: The file to check
        rule: The rule to match against
        
    Returns:
        True if the file matches the rule, False otherwise
    """
    match = rule.get('match', {})
    
    # Convert to lowercase for case-insensitive matching
    filename = file_path.name.lower()  # "Screenshot.png" -> "screenshot.png"
    file_ext = file_path.suffix.lower()  # ".PNG" -> ".png"
    
    # Track whether we've checked any criteria and if they all matched
    criteria_checked = False
    all_criteria_match = True
    
    # Check if filename contains any of the specified strings
    # Example: rule says "contains": ["screenshot"] and file is "Screenshot.png" -> matches
    if 'contains' in match:
        criteria_checked = True
        contains_list = match['contains']
        if not isinstance(contains_list, list):
            contains_list = [contains_list]
        
        # Check if filename contains any of the strings (case-insensitive)
        contains_match = any(term.lower() in filename for term in contains_list)
        if not contains_match:
            all_criteria_match = False
    
    # Check if file extension matches any of the specified extensions
    # Example: rule says "extensions": [".png", ".jpg"] and file is "image.png" -> matches
    if 'extensions' in match:
        criteria_checked = True
        extensions_list = match['extensions']
        if not isinstance(extensions_list, list):
            extensions_list = [extensions_list]
        
        # Normalize extensions (make sure they all start with '.')
        normalized_extensions = [
            ext.lower() if ext.startswith('.') else f'.{ext.lower()}'
            for ext in extensions_list
        ]
        
        # Check if the file's extension is in our list
        extension_match = file_ext in normalized_extensions
        if not extension_match:
            all_criteria_match = False
    
    # Check if filename matches a regex pattern
    # Example: rule says "pattern": "screenshot.*\\.png" -> matches "screenshot-2025.png"
    if 'pattern' in match:
        criteria_checked = True
        pattern = match['pattern']
        try:
            # Compile the regex pattern (case-insensitive)
            regex = re.compile(pattern, re.IGNORECASE)
            pattern_match = bool(regex.search(file_path.name))
            if not pattern_match:
                all_criteria_match = False
        except re.error as e:
            # If regex is invalid, print warning and don't match
            print(f"[WARNING] Invalid regex pattern in rule '{rule.get('name', 'unknown')}': {e}")
            all_criteria_match = False
    
    # If no criteria were checked, the rule doesn't match
    if not criteria_checked:
        return False
    
    # All checked criteria must match (AND logic)
    return all_criteria_match


def classify_file(file_path: Path, rules: List[Dict], base_path: Path) -> Optional[str]:
    """
    Determine which rule applies to a file and return its destination folder.
    
    This is the main classification function. It:
    1. Goes through each rule in order
    2. Checks if the file matches that rule
    3. Returns the destination folder for the first matching rule
    4. Returns None if no rules match
    
    Rules are checked in order, so the first match wins (priority-based).
    
    Example:
        File: "Screenshot 2025-01-15.png"
        Rules: [Screenshot rule, PDF rule, ...]
        Result: "Screenshots" (because it matched the first rule)
    
    Args:
        file_path: The file to classify
        rules: List of rules from load_rules()
        base_path: Base directory (e.g., ~/Desktop) for resolving relative paths
        
    Returns:
        Destination folder name (e.g., "Screenshots") if a rule matches, None otherwise
    """
    # Go through each rule in order (first match wins)
    for rule in rules:
        # Check if this file matches the rule
        if match_rule(file_path, rule):
            # It matches! Get the destination folder
            destination = rule['destination']
            
            # Resolve the full path (e.g., "Screenshots" -> "/Users/josephhudak/Desktop/Screenshots")
            resolved_dest = resolve_destination(base_path, destination)
            
            # Return just the relative path for display purposes
            return str(resolved_dest.relative_to(base_path.resolve()))
    
    # No rules matched, so we don't know where this file should go
    return None
