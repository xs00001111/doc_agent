# Use an official Python runtime as the base image.
FROM python:3.12-slim

# Set environment variables to non-interactive
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install dependencies (including Chromium)
RUN apt-get update && \
    apt-get install -y \
    chromium \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    ca-certificates \
    fonts-liberation && \
    rm -rf /var/lib/apt/lists/*

# Set the environment variable for Chromium path (adjust if necessary)
ENV CHROME_PATH=/usr/bin/chromium

# Upgrade pip and install Python dependencies
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (e.g., Chromium)
RUN pip install playwright && python -m playwright install chromium

# Copy your application code
COPY . .

# Expose the port (Render will set PORT env variable)
EXPOSE 7860

# Set environment variable to allow Gradio to listen on all interfaces
ENV GRADIO_SERVER_NAME=0.0.0.0

# Set the default command to run your app
CMD ["python", "agent.py"]
