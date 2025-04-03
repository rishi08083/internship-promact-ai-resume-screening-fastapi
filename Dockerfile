# Base image
FROM python:3.11.9

# Install Tesseract-OCR and its dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libpng-dev \
    libjpeg-dev \
    zlib1g-dev \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file first (for better caching)
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the application code
COPY . .

# Set Tesseract path environment variable
ENV TESSERACT_PATH=/usr/bin/tesseract

# Expose the FastAPI port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
