# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY src/ ./src/
COPY data/ ./data/
COPY pyproject.toml .
COPY README.md .

# Install the package in development mode
RUN pip install -e .

# Create non-root user
RUN useradd --create-home --shell /bin/bash amc
USER amc

# Expose port (for debugging/monitoring purposes)
EXPOSE 8000

# Set the default command
CMD ["python", "-m", "amc_mcp.server"]