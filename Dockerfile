FROM python:3.13-slim

# Install dependencies
RUN apt-get update && apt-get install -y wget tar unzip && rm -rf /var/lib/apt/lists/*

# Download and install N_m3u8DL-RE
RUN wget -O N_m3u8DL-RE.tar.gz https://github.com/nilaoda/N_m3u8DL-RE/releases/latest/download/N_m3u8DL-RE_Linux_x64.tar.gz \
    && tar -xzf N_m3u8DL-RE.tar.gz \
    && chmod +x N_m3u8DL-RE \
    && mv N_m3u8DL-RE /usr/local/bin/ \
    && rm N_m3u8DL-RE.tar.gz

# Set working directory
WORKDIR /app

# Copy repo files
COPY . .

# Install Python requirements
RUN pip install --no-cache-dir -r requirements.txt

# Run the bot
CMD ["python", "bot.py"]
