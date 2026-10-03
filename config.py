# config.py
"""
Configuration settings and constants for StegoVault.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB max upload limit

# Image formats
IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp"}
IMAGE_DECODE_EXTENSIONS = {"png", "bmp"}

# Audio formats
AUDIO_EXTENSIONS = {"wav", "ogg", "mp4", "mp3", "m4a", "flac"}
AUDIO_DECODE_EXTENSIONS = {"wav"}

# Video formats
VIDEO_EXTENSIONS = {"mp4", "avi", "mov", "mkv", "webm"}
VIDEO_DECODE_EXTENSIONS = {"mp4", "avi", "mov", "mkv", "webm"}

# Media Converter formats
CONVERTER_AUDIO_EXTENSIONS = {"ogg", "mp4", "mp3", "m4a", "flac", "wav"}
CONVERTER_VIDEO_EXTENSIONS = {"avi", "mkv", "mov", "webm", "flv", "wmv", "mp4"}

# Steganography Protocol Delimiters & Markers
DELIMITER = b"#####"
VIDEO_MARKER = b"__STEGO_VAULT_v2__"
VIDEO_DELIMITER = b"__END_STEGO_VAULT__"
