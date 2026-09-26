# StegoVault — Multi-Media Steganography & Conversion Suite

StegoVault is a full-featured multi-media steganography platform that allows users to encode and decode hidden confidential messages across **Images**, **Audio waveforms**, and **Video streams** with 100% media playability, plausible deniability, and integrated format conversion.

---

## 🌟 Key Features

- **Central Tool Selection Hub**: An interactive landing page to select between Image, Audio, Video steganography, or the Media Converter.
- **🖼️ Image Steganography**:
  - Embeds secret text into RGB channels of digital images.
  - Supports: PNG, JPG, JPEG, WEBP, BMP (Encodes into lossless PNG).
  - In-browser image preview, live character counter, and instant download.
- **🎵 Audio Steganography**:
  - Embeds secret text into uncompressed PCM audio waveforms without audible alteration.
  - Accepts **WAV, OGG, MP4, MP3** (auto-converts into clean uncompressed PCM WAV).
  - Interactive in-browser audio player preview.
- **🎬 Video Steganography (100% Playable MP4)**:
  - Embeds secret text into standard **MP4** videos.
  - **Plausible Deniability**: The output video plays smoothly and flawlessly in **Windows Media Player**, Movies & TV, Chrome, Edge, Safari, VLC, and mobile devices without showing that any secret is hidden inside.
  - Supports: MP4, AVI, MOV, MKV, WEBM (Encodes into standard playable `.mp4`).
  - Decoding also supports legacy raw-frame AVI files.
- **🔄 Media Format Converter**:
  - Convert **OGG / MP4 / MP3 &rarr; WAV** (ready for audio steganography).
  - Transcode **AVI / MKV / MOV &rarr; Playable MP4** (for universal media playback).
- **100% Ephemeral & Private**: Temporary files on the server are purged immediately after processing.

---

## 🚀 Getting Started

### 1. Prerequisites & Virtual Environment

Ensure Python 3.10+ is installed:
```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows Command Prompt:
.\.venv\Scripts\activate.bat
```

### 2. Install Dependencies

```bash
pip install Flask pillow opencv-python numpy imageio-ffmpeg
```

### 3. Run the Application

```bash
python app.py
```

Open your browser and navigate to:
```
http://localhost:5000/
```

---

## 🗺️ Application Routes

| Route | Method | Description |
|---|---|---|
| `/` | `GET` | Central Tool Selector Hub |
| `/image` | `GET` | Image Steganography Tool (Encode & Decode) |
| `/image/encode` | `POST` | Encodes secret message into image and downloads `.png` |
| `/image/decode` | `POST` | Decodes hidden message from PNG image |
| `/audio` | `GET` | Audio Steganography Tool (Encode & Decode) |
| `/audio/encode` | `POST` | Encodes secret message into audio (accepts WAV/OGG/MP4/MP3) and downloads `.wav` |
| `/audio/decode` | `POST` | Decodes hidden message from WAV audio |
| `/video` | `GET` | Video Steganography Tool (Encode & Decode) |
| `/video/encode` | `POST` | Encodes secret message into video and downloads playable `.mp4` |
| `/video/decode` | `POST` | Decodes hidden message from MP4 or AVI video |
| `/converter` | `GET` | Media Format Converter Tool |
| `/converter/audio` | `POST` | Converts OGG / MP4 / MP3 to uncompressed `.wav` |
| `/converter/video` | `POST` | Converts AVI / MKV / MOV to standard playable `.mp4` |
