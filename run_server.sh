#!/bin/bash
# Fake Rovio server for The Croods. Keep this window open while playing.
cd "$(dirname "$0")/server" && exec python3 fake_rovio.py
