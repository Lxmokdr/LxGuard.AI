# Use official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from Expert_Agent folder
COPY Expert_Agent/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy source code from Expert_Agent folder into the container root
# This ensures uvicorn api.api_hybrid:app works correctly
COPY Expert_Agent/ ./

# Expose port (Hugging Face expects 7860)
EXPOSE 7860

# Command to run the application
CMD ["uvicorn", "api.api_hybrid:app", "--host", "0.0.0.0", "--port", "7860"]
