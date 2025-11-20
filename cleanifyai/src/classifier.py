"""
Classifier Module

Handles file classification based on rules.
This module matches files against a set of rules to determine
where they should be moved. Rules are priority-based, with the
first matching rule taking precedence.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from mover import resolve_destination


def load_rules(config_path: str) -> List[Dict]:
    """
    Load classification rules from a JSON configuration file.
    
    The rules file should contain a JSON object with a "rules" array.
    Each rule should have:
    - name: A descriptive name for the rule
    - match: Matching criteria (contains, pattern, extension, etc.)
    - destination: Target folder path relative to the scanned directory
    
    Args:
        config_path: Path to the rules.json file
        
    Returns:
        List of rule dictionaries
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        json.JSONDecodeError: If the JSON is invalid
        ValueError: If rule structure is invalid
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        # Return empty rules list if file doesn't exist
        return []
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in rules file: {e}")
    
    rules = config.get('rules', [])
    
    # Validate rule structure
    for i, rule in enumerate(rules):
        if not isinstance(rule, dict):
            raise ValueError(f"Rule {i} is not a dictionary")
        
        if 'name' not in rule:
            raise ValueError(f"Rule {i} is missing 'name' field")
        
        if 'match' not in rule:
            raise ValueError(f"Rule {i} ('{rule.get('name', 'unknown')}') is missing 'match' field")
        
        if 'destination' not in rule:
            raise ValueError(f"Rule {i} ('{rule.get('name', 'unknown')}') is missing 'destination' field")
        
        # Validate match structure
        match = rule['match']
        if not isinstance(match, dict):
            raise ValueError(f"Rule {i} ('{rule.get('name', 'unknown')}') has invalid 'match' field (must be a dictionary)")
        
        # Check for valid match types
        valid_match_keys = {'type', 'contains', 'extensions', 'pattern'}
        match_keys = set(match.keys())
        
        # If 'type' is specified, validate it
        if 'type' in match:
            valid_types = {'contains', 'extension', 'pattern'}
            if match['type'] not in valid_types:
                raise ValueError(f"Rule {i} ('{rule.get('name', 'unknown')}') has invalid match type: {match['type']}")
        
        # Validate that match has at least one valid criterion
        has_criteria = any(key in match for key in ['contains', 'extensions', 'pattern'])
        if not has_criteria:
            raise ValueError(f"Rule {i} ('{rule.get('name', 'unknown')}') has no valid match criteria")
    
    return rules


def match_rule(file_path: Path, rule: Dict) -> bool:
    """
    Check if a file matches a specific rule's criteria.
    
    Supports multiple match types:
    - contains: Filename contains any of the specified strings (case-insensitive)
    - extension: File extension matches any of the specified extensions
    - pattern: Filename matches a regex pattern
    
    Multiple criteria are combined with AND logic (all must match).
    
    Args:
        file_path: Path object of the file to check
        rule: Rule dictionary with match criteria
        
    Returns:
        True if file matches the rule, False otherwise
    """
    match = rule.get('match', {})
    filename = file_path.name.lower()  # Use lowercase for case-insensitive matching
    file_ext = file_path.suffix.lower()  # Include the dot (e.g., '.pdf')
    
    # Track if any criteria matched
    criteria_checked = False
    all_criteria_match = True
    
    # Check 'contains' criteria
    if 'contains' in match:
        criteria_checked = True
        contains_list = match['contains']
        if not isinstance(contains_list, list):
            contains_list = [contains_list]
        
        # Check if filename contains any of the strings (case-insensitive)
        contains_match = any(term.lower() in filename for term in contains_list)
        if not contains_match:
            all_criteria_match = False
    
    # Check 'extensions' criteria
    if 'extensions' in match:
        criteria_checked = True
        extensions_list = match['extensions']
        if not isinstance(extensions_list, list):
            extensions_list = [extensions_list]
        
        # Normalize extensions (ensure they start with '.')
        normalized_extensions = [
            ext.lower() if ext.startswith('.') else f'.{ext.lower()}'
            for ext in extensions_list
        ]
        
        extension_match = file_ext in normalized_extensions
        if not extension_match:
            all_criteria_match = False
    
    # Check 'pattern' criteria (regex)
    if 'pattern' in match:
        criteria_checked = True
        pattern = match['pattern']
        try:
            # Use case-insensitive matching
            regex = re.compile(pattern, re.IGNORECASE)
            pattern_match = bool(regex.search(file_path.name))
            if not pattern_match:
                all_criteria_match = False
        except re.error as e:
            # Invalid regex pattern - log warning but don't match
            print(f"[WARNING] Invalid regex pattern in rule '{rule.get('name', 'unknown')}': {e}")
            all_criteria_match = False
    
    # If no criteria were checked, rule doesn't match
    if not criteria_checked:
        return False
    
    # All checked criteria must match (AND logic)
    return all_criteria_match


def classify_file(file_path: Path, rules: List[Dict], base_path: Path) -> Optional[str]:
    """
    Determine which rule applies to a given file and return its destination.
    
    This function implements a priority-based rule matching system:
    - Rules are evaluated in order (first match wins)
    - Matching criteria can include:
      * Filename contains certain strings
      * Filename matches a pattern/regex
      * File extension matches
    - Returns the destination path if a rule matches, None otherwise
    
    Args:
        file_path: Path object of the file to classify
        rules: List of rule dictionaries from load_rules()
        base_path: Base directory path (for resolving relative destinations)
        
    Returns:
        Destination path as a string if a rule matches, None otherwise
    """
    # Iterate through rules in order (first match wins)
    for rule in rules:
        if match_rule(file_path, rule):
            destination = rule['destination']
            # Resolve destination relative to base_path
            resolved_dest = resolve_destination(base_path, destination)
            # Return as string (relative to base_path for display)
            return str(resolved_dest.relative_to(base_path.resolve()))
    
    # No rule matched
    return None
