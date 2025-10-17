# YAML File Comparison Tool

A Python script to compare two YAML configuration files and display differences in a readable format. Good for CI/CD pipelines and local development.

## Features

✅ **Environment Variable Support** - Easy integration with CI/CD pipelines  
✅ **Concise Diff Output** - Shows only the fields that differ  
✅ **Nested Structure Support** - Handles complex YAML hierarchies  
✅ **List Order Comparison** - Optional ignore list order differences  
✅ **Exit Codes** - 0 for identical, 1 for differences, 2 for errors  
✅ **Default Paths** - Works with global variables for quick local testing


## Prerequisites

- Python 3.7 or higher
- Docker (optional, for containerized execution)

## How to run

---

## Option 1: Running with Virtual Environment

### 1. Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Deactivate virtual env
deactivate
```
### 2. Run with Default Files
The script uses default paths defined in scipt:

```bash
DEFAULT_FILE_1 = "resources/config1.yml"
DEFAULT_FILE_2 = "resources/config2.yml"

# Run with defaults
python scripts/compare_yaml.py
```

### 3. Run  with Custom Files (ENV Variable)

```bash
export YAML_FILE_1=resources/production.yml
export YAML_FILE_2=resources/staging.yml
export IGNORE_ORDER=false  # Optional

# Run the script
python scripts/compare_yaml.py
```

### 4. Run with absolute path (ENV Variable)
```bash
export YAML_FILE_1=/full/path/to/config1.yml
export YAML_FILE_2=/full/path/to/config2.yml
python scripts/compare_yaml.py
```

## Option 2: Run with Docker

```bash
docker build -t yaml-compare .

# Uses default paths from global variables
docker run yaml-compare

# Run with custom files

docker run -e YAML_FILE_1=resources/production.yml \
           -e YAML_FILE_2=resources/staging.yml \
           -e IGNORE_ORDER=false \
           yaml-compare

# Run with external files (volumn mount)
docker run -v /path/to/configs:/app/configs \
           -e YAML_FILE_1=configs/file1.yml \
           -e YAML_FILE_2=configs/file2.yml \
           yaml-compare
```

### Error codes

Code	Meaning
0	    Files are identical
1	    Files have differences
2	    Error (file not found, invalid YAML, etc.)