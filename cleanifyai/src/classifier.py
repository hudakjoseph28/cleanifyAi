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

CONTRACTS:
All functions use strict type hints. Rules are Dict[str, Any] with 'name', 'match', 'destination' keys.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from mover import resolve_destination


def load_rules(config_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Load classification rules from a JSON configuration file.
    
    The rules.json file contains instructions on how to identify different types of files.
    Each rule specifies matching criteria (filename patterns, extensions) and a destination
    folder. Rules are validated to ensure they have the required structure.
    
    Rule Structure:
        {
            "name": "Screenshots",              # Descriptive name for the rule
            "match": {                          # Matching criteria (all must match)
                "contains": ["screenshot"],     # Filename must contain these strings
                "extensions": [".png", ".jpg"]  # File must have one of these extensions
            },
            "destination": "Screenshots"        # Destination folder (relative to base)
        }
    
    Examples:
        >>> rules = load_rules("config/rules.json")
        >>> # Returns: [{"name": "Screenshots", "match": {...}, "destination": "Screenshots"}, ...]
        
        >>> rules = load_rules(Path("config/rules.json"))
        >>> # Returns: List of rule dictionaries
    
    Args:
        config_path: Path to the rules.json file. Can be a string or Path object.
            The file should contain a JSON object with a "rules" array.
            Example: "config/rules.json" or Path("config/rules.json")
        
    Returns:
        List[Dict[str, Any]]: A list of rule dictionaries. Each rule has:
            - 'name': str - Rule name
            - 'match': Dict - Matching criteria (contains, extensions, pattern)
            - 'destination': str - Destination folder path
            Returns an empty list if the file doesn't exist or has no rules.
        
    Raises:
        ValueError: If the JSON file is invalid, malformed, or rules are missing
            required fields. The error message includes details about which rule
            is invalid and what field is missing.
        
    Note:
        - Validates that each rule has 'name', 'match', and 'destination' fields
        - Validates that 'match' is a dictionary with at least one criterion
        - Returns empty list if file doesn't exist (doesn't raise an error)
    """
    # Convert to string if it's a Path object
    config_path_str = str(config_path)
    
    try:
        # Open and read the JSON file
        with open(config_path_str, 'r', encoding='utf-8') as f:
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


def match_rule(file_path: Union[Path, str], rule: Dict[str, Any]) -> bool:
    """
    Check if a file matches a specific rule's criteria.
    
    This function checks if a file meets all the requirements of a rule. Rules can
    specify multiple matching criteria, and ALL criteria must match for the rule
    to match (AND logic). Matching is case-insensitive for contains and extensions.
    
    Supported Match Criteria:
        - contains: List of strings that must appear in the filename
            Example: ["screenshot", "screen"] matches "Screenshot 2025.png"
        - extensions: List of file extensions (with or without leading dot)
            Example: [".png", ".jpg"] matches files with .png or .jpg extension
        - pattern: Regular expression pattern that the filename must match
            Example: r"screenshot.*\.png" matches "screenshot-2025.png"
    
    Examples:
        >>> from pathlib import Path
        >>> file = Path("Screenshot 2025-01-15.png")
        >>> rule = {"match": {"contains": ["screenshot"], "extensions": [".png"]}}
        >>> match_rule(file, rule)
        True  # Matches: contains "screenshot" AND has .png extension
        
        >>> file = Path("document.pdf")
        >>> rule = {"match": {"contains": ["screenshot"]}}
        >>> match_rule(file, rule)
        False  # Doesn't contain "screenshot"
    
    Args:
        file_path: The file to check. Can be a Path object or string.
            Only the filename is checked, not the full path.
            Example: Path("Screenshot.png") or "Screenshot.png"
        rule: The rule dictionary to match against. Must have a 'match' key
            containing the matching criteria.
            Example: {"match": {"contains": ["screenshot"], "extensions": [".png"]}}
        
    Returns:
        bool: True if the file matches ALL criteria in the rule,
            False if any criterion doesn't match or if no criteria are specified.
        
    Note:
        - Matching is case-insensitive for 'contains' and 'extensions'
        - All criteria must match (AND logic, not OR)
        - Invalid regex patterns in 'pattern' are caught and treated as non-matching
        - Returns False if no criteria are checked (empty match dictionary)
    """
    # Convert to Path object if it's a string
    if not isinstance(file_path, Path):
        file_path = Path(str(file_path))
    
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


def classify_file(
    file_path: Union[Path, str],
    rules: List[Dict[str, Any]],
    base_path: Union[Path, str]
) -> Optional[str]:
    """
    Classify a file and return its destination folder based on matching rules.
    
    This is the main classification function. It iterates through rules in order
    and returns the destination for the first matching rule. Rules are checked
    sequentially, so the first match wins (priority-based matching).
    
    The function:
    1. Iterates through rules in the order they appear in the list
    2. Checks if the file matches each rule using match_rule()
    3. Returns the destination folder for the first matching rule
    4. Returns None if no rules match
    
    Examples:
        >>> from pathlib import Path
        >>> file = Path("Screenshot 2025-01-15.png")
        >>> rules = [
        ...     {"name": "Screenshots", "match": {"contains": ["screenshot"]}, "destination": "Screenshots"},
        ...     {"name": "PDFs", "match": {"extensions": [".pdf"]}, "destination": "Documents"}
        ... ]
        >>> base = Path("~/Desktop")
        >>> classify_file(file, rules, base)
        "Screenshots"  # Matched first rule
        
        >>> file = Path("document.pdf")
        >>> classify_file(file, rules, base)
        "Documents"  # Matched second rule
        
        >>> file = Path("random.txt")
        >>> classify_file(file, rules, base)
        None  # No rules matched
    
    Args:
        file_path: The file to classify. Can be a Path object or string.
            Example: Path("Screenshot.png") or "Screenshot.png"
        rules: List of rule dictionaries from load_rules(). Rules are checked
            in order, so put more specific rules first.
            Example: [{"name": "Screenshots", "match": {...}, "destination": "Screenshots"}, ...]
        base_path: Base directory path for resolving relative destination paths.
            Can be a Path object or string. Used to resolve the full destination path.
            Example: Path("~/Desktop") or "~/Desktop"
        
    Returns:
        Optional[str]: The destination folder path (relative to base_path) if a rule
            matches, None if no rules match. The returned path is relative to base_path
            for display purposes.
            Example: "Screenshots" or "Documents/PDFs" or None
        
    Note:
        - Rules are checked in order (first match wins)
        - Returns relative path, not absolute path
        - Returns None if no rules match (file will be skipped)
        - Destination paths are resolved relative to base_path
    """
    # Convert to Path objects
    if not isinstance(file_path, Path):
        file_path = Path(str(file_path))
    if not isinstance(base_path, Path):
        base_path = Path(str(base_path))
    
    # Resolve base_path to absolute path
    base_path_resolved = base_path.resolve()
    
    # Go through each rule in order (first match wins)
    for rule in rules:
        # Check if this file matches the rule
        if match_rule(file_path, rule):
            # It matches! Get the destination folder
            destination = rule['destination']
            
            # Resolve the full path (e.g., "Screenshots" -> "/Users/josephhudak/Desktop/Screenshots")
            resolved_dest = resolve_destination(base_path_resolved, destination)
            
            # Return just the relative path for display purposes
            try:
                return str(resolved_dest.relative_to(base_path_resolved))
            except ValueError:
                # If paths are on different drives (Windows), return the destination as-is
                return destination
    
    # No rules matched, so we don't know where this file should go
    return None
