FROM python:3.13-slim

# Install curl and unzip
RUN apt-get update && apt-get install -y curl unzip && rm -rf /var/lib/apt/lists/*

# Download and set up N_m3u8DL-RE
RUN curl -L https://github.com/nilaoda/N_m3u8DL-RE/releases/latest/download/N_m3u8DL-RE_Linux_x64.zip -o N_m3u8DL-RE.zip \
    && unzip N_m3u8DL-RE.zip \
    && chmod +x N_m3u8DL-RE \
    && mv N_m3u8DL-RE /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy code
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run
CMD ["python", "main.py"]
