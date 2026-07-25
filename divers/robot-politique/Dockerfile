# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py .
COPY logs logs/

# Expose port (for local testing)
EXPOSE 8080

# Set entrypoint
CMD ["python", "main.py"]
