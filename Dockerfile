# Use a slim Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies first (optimize layer caching)sss
COPY requirements.txt ./
RUN pip install --no-cache-dir --default-timeout=600 -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the required port
EXPOSE 45441

# Run the app
CMD ["uvicorn", "FastAPI_BotGrid2025:app", "--host", "0.0.0.0", "--port", "45441"]
