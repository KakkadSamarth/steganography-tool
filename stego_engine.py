# stego_engine.py
"""
Unified facade for backward compatibility.
Exposes ImageStegoEngine, AudioStegoEngine, VideoStegoEngine, MediaConverter, and SteganographyEngine.
"""
from image_stego import ImageStegoEngine
from audio_stego import AudioStegoEngine
from video_stego import VideoStegoEngine
from media_converter import MediaConverter

# Backward-compatible alias
SteganographyEngine = ImageStegoEngine

__all__ = [
    "ImageStegoEngine",
    "AudioStegoEngine",
    "VideoStegoEngine",
    "MediaConverter",
    "SteganographyEngine",
]