FROM python:3.9-slim

ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV SDL_VIDEODRIVER=dummy
ENV PYGAME_HIDE_SUPPORT_PROMPT=1
ENV LOG_PATH=/app/server.log

WORKDIR /app

# Install system dependencies required for pygame and building Python wheels
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       libsdl2-dev \
       libsdl2-image-dev \
       libsdl2-mixer-dev \
       libsdl2-ttf-dev \
       libportmidi-dev \
       libfreetype6-dev \
       libavformat-dev \
       libavcodec-dev \
       libswscale-dev \
       libjpeg-dev \
       libpng-dev \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Create a non-root user early so we can chown files to it and leave the runtime as non-root
RUN useradd --create-home appuser || true

# Copy project files
COPY . /app

# Ensure the app directory and the server log are owned by the non-root user so the process can write logs
RUN mkdir -p /app && chown -R appuser:appuser /app \
    && touch /app/server.log && chown appuser:appuser /app/server.log

# Expose the server port
EXPOSE 5550

# Use a non-root user for safety
USER appuser

# Default command
CMD ["python3", "Server.py"]
