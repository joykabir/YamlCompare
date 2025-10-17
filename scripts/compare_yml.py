#!/usr/bin/env python3
"""
YAML File Comparison Script for CI/CD
Compares two YAML files and shows differences.

Environment Variables:
    YAML_FILE_1: Path to the first YAML file
    YAML_FILE_2: Path to the second YAML file
    IGNORE_ORDER: (Optional) Set to 'true' to ignore list order differences (default: false)

Exit Codes:
    0: Files are identical
    1: Files have differences
    2: Error (file not found, invalid YAML, etc.)
"""

import os
import sys
import yaml
from typing import Any, Dict, List, Tuple, Set
from pathlib import Path


# ==============================================================================
# GLOBAL CONFIGURATION - Default file paths for local testing
# ==============================================================================
# These paths are used when YAML_FILE_1 and YAML_FILE_2 environment variables
# are not set. Paths are relative to the project root.
DEFAULT_FILE_1 = "resources/config1.yml"
DEFAULT_FILE_2 = "resources/config2.yml"
# ==============================================================================


class Color:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def get_project_root() -> str:
    """Get the project root directory (directory containing this script's parent)."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Assume project root is the parent directory of the script
    # Adjust this logic if your script is in a subdirectory like scripts/
    project_root = os.path.dirname(script_dir)
    return project_root


def resolve_file_path(relative_path: str) -> str:
    """
    Convert relative path to absolute path based on project root.
    
    Args:
        relative_path: Path relative to project root
        
    Returns:
        Absolute path
    """
    if os.path.isabs(relative_path):
        return relative_path
    
    project_root = get_project_root()
    absolute_path = os.path.join(project_root, relative_path)
    return os.path.normpath(absolute_path)


def load_yaml_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a YAML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"{Color.RED}Error: File not found: {file_path}{Color.RESET}", file=sys.stderr)
        sys.exit(2)
    except yaml.YAMLError as e:
        print(f"{Color.RED}Error: Invalid YAML in {file_path}: {e}{Color.RESET}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"{Color.RED}Error reading {file_path}: {e}{Color.RESET}", file=sys.stderr)
        sys.exit(2)


def get_all_keys(data: Dict[str, Any], prefix: str = "") -> Set[str]:
    """Recursively get all keys from a nested dictionary."""
    keys = set()
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        keys.add(full_key)
        if isinstance(value, dict):
            keys.update(get_all_keys(value, full_key))
    return keys


def get_nested_value(data: Dict[str, Any], key_path: str) -> Any:
    """Get value from nested dictionary using dot-separated key path."""
    keys = key_path.split('.')
    value = data
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value


def format_value_inline(value: Any) -> str:
    """Format value for inline display (concise)."""
    if isinstance(value, dict):
        if not value:
            return "{}"
        # Show dict as compact representation
        items = [f"{k}: {format_value_inline(v)}" for k, v in value.items()]
        if len(str(value)) < 60:  # If short enough, show inline
            return "{" + ", ".join(items) + "}"
        else:
            return f"{{...{len(value)} keys...}}"
    elif isinstance(value, list):
        if not value:
            return "[]"
        # Show list compactly
        if len(value) <= 3 and all(not isinstance(v, (dict, list)) for v in value):
            return "[" + ", ".join(str(v) for v in value) + "]"
        else:
            return f"[...{len(value)} items...]"
    elif value is None:
        return "null"
    elif isinstance(value, str):
        return f'"{value}"' if ' ' in value or value == '' else value
    else:
        return str(value)


def compare_values(val1: Any, val2: Any, ignore_order: bool = False) -> bool:
    """Compare two values, optionally ignoring list order."""
    if type(val1) != type(val2):
        return False
    
    if isinstance(val1, dict):
        if set(val1.keys()) != set(val2.keys()):
            return False
        return all(compare_values(val1[k], val2[k], ignore_order) for k in val1.keys())
    
    elif isinstance(val1, list):
        if len(val1) != len(val2):
            return False
        if ignore_order:
            # Try to match items regardless of order (for simple types)
            try:
                return sorted(str(v) for v in val1) == sorted(str(v) for v in val2)
            except:
                return val1 == val2
        return val1 == val2
    
    else:
        return val1 == val2


def compare_yaml_files(file1_path: str, file2_path: str, ignore_order: bool = False) -> Tuple[bool, List[str]]:
    """
    Compare two YAML files and return differences.
    
    Returns:
        Tuple of (are_identical, list_of_differences)
    """
    data1 = load_yaml_file(file1_path)
    data2 = load_yaml_file(file2_path)
    
    all_keys = get_all_keys(data1) | get_all_keys(data2)
    differences = []
    
    file1_name = os.path.basename(file1_path)
    file2_name = os.path.basename(file2_path)
    
    for key in sorted(all_keys):
        val1 = get_nested_value(data1, key)
        val2 = get_nested_value(data2, key)
        
        if val1 is None and val2 is not None:
            # Key only exists in file2
            differences.append(
                f"{Color.RED}[-]{Color.RESET} {Color.BOLD}{key}{Color.RESET}:\n"
                f"    {Color.BLUE}{file1_name}{Color.RESET}: {Color.RED}<missing>{Color.RESET}\n"
                f"    {Color.BLUE}{file2_name}{Color.RESET}: {format_value_inline(val2)}"
            )
        elif val2 is None and val1 is not None:
            # Key only exists in file1
            differences.append(
                f"{Color.RED}[-]{Color.RESET} {Color.BOLD}{key}{Color.RESET}:\n"
                f"    {Color.BLUE}{file1_name}{Color.RESET}: {format_value_inline(val1)}\n"
                f"    {Color.BLUE}{file2_name}{Color.RESET}: {Color.RED}<missing>{Color.RESET}"
            )
        elif not compare_values(val1, val2, ignore_order):
            # Key exists in both but values differ
            differences.append(
                f"{Color.YELLOW}[~]{Color.RESET} {Color.BOLD}{key}{Color.RESET}:\n"
                f"    {Color.BLUE}{file1_name}{Color.RESET}: {format_value_inline(val1)}\n"
                f"    {Color.BLUE}{file2_name}{Color.RESET}: {format_value_inline(val2)}"
            )
    
    return len(differences) == 0, differences


def main():
    """Main function."""
    # Get file paths from environment variables or use defaults
    file1_relative = os.getenv('YAML_FILE_1', DEFAULT_FILE_1)
    file2_relative = os.getenv('YAML_FILE_2', DEFAULT_FILE_2)
    ignore_order = os.getenv('IGNORE_ORDER', 'false').lower() == 'true'
    
    # Determine source of configuration
    using_env_vars = os.getenv('YAML_FILE_1') is not None and os.getenv('YAML_FILE_2') is not None
    
    # Convert to absolute paths
    file1_path = resolve_file_path(file1_relative)
    file2_path = resolve_file_path(file2_relative)
    
    # Print header
    print(f"\n{Color.BOLD}{'='*80}{Color.RESET}")
    print(f"{Color.BOLD}YAML File Comparison{Color.RESET}")
    print(f"{Color.BOLD}{'='*80}{Color.RESET}")
    print(f"Configuration source: {Color.CYAN}{'Environment Variables' if using_env_vars else 'Default Global Variables'}{Color.RESET}")
    print(f"File 1: {Color.BLUE}{os.path.basename(file1_path)}{Color.RESET} ({file1_path})")
    print(f"File 2: {Color.BLUE}{os.path.basename(file2_path)}{Color.RESET} ({file2_path})")
    print(f"Ignore list order: {Color.YELLOW}{ignore_order}{Color.RESET}")
    print(f"{Color.BOLD}{'='*80}{Color.RESET}\n")
    
    # Validate that files exist
    if not os.path.exists(file1_path):
        print(f"{Color.RED}Error: File 1 does not exist: {file1_path}{Color.RESET}", file=sys.stderr)
        print(f"{Color.YELLOW}Tip: Check if the path is correct relative to project root: {get_project_root()}{Color.RESET}", 
              file=sys.stderr)
        sys.exit(2)
    
    if not os.path.exists(file2_path):
        print(f"{Color.RED}Error: File 2 does not exist: {file2_path}{Color.RESET}", file=sys.stderr)
        print(f"{Color.YELLOW}Tip: Check if the path is correct relative to project root: {get_project_root()}{Color.RESET}", 
              file=sys.stderr)
        sys.exit(2)
    
    # Compare files
    are_identical, differences = compare_yaml_files(file1_path, file2_path, ignore_order)
    
    if are_identical:
        print(f"{Color.GREEN}✓ Files are identical{Color.RESET}\n")
        sys.exit(0)
    else:
        print(f"{Color.RED}✗ Found {len(differences)} difference(s):{Color.RESET}\n")
        for diff in differences:
            print(diff)
            print()
        sys.exit(1)


if __name__ == "__main__":
    main()