FROM python:3.7-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy scripts and resources
COPY scripts/ scripts/
COPY resources/ resources/

# Run the script from scripts directory
CMD ["python", "scripts/compare_yaml.py"]