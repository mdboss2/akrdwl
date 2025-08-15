#!/bin/bash
set -e
apt-get update && apt-get install -y wget tar
wget -O N_m3u8DL-RE.tar.gz https://github.com/nilaoda/N_m3u8DL-RE/releases/latest/download/N_m3u8DL-RE_Linux_x64.tar.gz
tar -xzf N_m3u8DL-RE.tar.gz
chmod +x N_m3u8DL-RE
mv N_m3u8DL-RE /usr/local/bin/
pip install -r requirements.txt
