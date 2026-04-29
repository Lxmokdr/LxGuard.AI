# Use official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model (required by nlp_core.py)
RUN python -m spacy download en_core_web_sm

# Copy project files
COPY . .

# Expose port
EXPOSE 8001

# Command to run the application (No reload for production)
CMD ["uvicorn", "api.api_hybrid:app", "--host", "0.0.0.0", "--port", "8001"]
