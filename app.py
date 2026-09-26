# app.py
import os
import uuid
import io
from flask import Flask, render_template, request, send_file

from stego_engine import ImageStegoEngine, AudioStegoEngine, VideoStegoEngine, MediaConverter, SteganographyEngine

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize steganography engines
image_engine = ImageStegoEngine()
audio_engine = AudioStegoEngine()
video_engine = VideoStegoEngine()

# Supported file extensions
IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp"}
IMAGE_DECODE_EXTENSIONS = {"png", "bmp"}

# Audio cover supports WAV plus OGG, MP4, MP3 for automatic extraction
AUDIO_EXTENSIONS = {"wav", "ogg", "mp4", "mp3", "m4a", "flac"}
AUDIO_DECODE_EXTENSIONS = {"wav"}

VIDEO_EXTENSIONS = {"mp4", "avi", "mov", "mkv", "webm"}
VIDEO_DECODE_EXTENSIONS = {"mp4", "avi", "mov", "mkv", "webm"}

CONVERTER_AUDIO_EXTENSIONS = {"ogg", "mp4", "mp3", "m4a", "flac", "wav"}
CONVERTER_VIDEO_EXTENSIONS = {"avi", "mkv", "mov", "webm", "flv", "wmv", "mp4"}

def check_extension(filename, allowed_set):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_set


# ==========================================
# HUB / SELECTOR ROUTE
# ==========================================
@app.route("/")
def home():
    """Main landing hub to choose between Image, Audio, Video tools or Media Converter."""
    return render_template("index.html", active_page="hub")


# ==========================================
# IMAGE STEGANOGRAPHY ROUTES
# ==========================================
@app.route("/image")
def image_tool():
    return render_template("image.html", active_page="image", active_tab="encode")

@app.route("/image/encode", methods=["POST"])
@app.route("/process_encode", methods=["POST"])  # Backwards compatibility
def image_encode():
    uploaded_file = request.files.get("cover_image")
    secret_text = request.form.get("secret_text", "")

    if not uploaded_file or uploaded_file.filename == "":
        return render_template("image.html", active_page="image", active_tab="encode", error_message="Please choose a cover image first.")
    if not check_extension(uploaded_file.filename, IMAGE_EXTENSIONS):
        return render_template("image.html", active_page="image", active_tab="encode", error_message="Supported image formats are PNG, JPG, JPEG, WEBP, and BMP.")
    if secret_text.strip() == "":
        return render_template("image.html", active_page="image", active_tab="encode", error_message="Please enter a secret message to hide.")

    ext = uploaded_file.filename.rsplit(".", 1)[1].lower()
    unique_id = uuid.uuid4().hex
    input_path = os.path.join(UPLOAD_FOLDER, f"temp_cover_img_{unique_id}.{ext}")
    output_path = os.path.join(UPLOAD_FOLDER, f"encoded_img_{unique_id}.png")

    try:
        uploaded_file.save(input_path)
        image_engine.encode(input_path, secret_text, output_path)

        with open(output_path, "rb") as f:
            file_buffer = io.BytesIO(f.read())
        file_buffer.seek(0)

        return send_file(
            file_buffer,
            mimetype="image/png",
            as_attachment=True,
            download_name="encoded_image.png"
        )
    except ValueError as err:
        return render_template("image.html", active_page="image", active_tab="encode", error_message=str(err))
    except Exception as err:
        return render_template("image.html", active_page="image", active_tab="encode", error_message=f"Processing failed: {err}")
    finally:
        for p in (input_path, output_path):
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass

@app.route("/image/decode", methods=["POST"])
@app.route("/process_decode", methods=["POST"])  # Backwards compatibility
def image_decode():
    uploaded_file = request.files.get("encoded_image")

    if not uploaded_file or uploaded_file.filename == "":
        return render_template("image.html", active_page="image", active_tab="decode", error_message="Please choose an image to decode.")
    if not check_extension(uploaded_file.filename, IMAGE_DECODE_EXTENSIONS):
        return render_template("image.html", active_page="image", active_tab="decode", error_message="Please upload a lossless PNG or BMP file.")

    ext = uploaded_file.filename.rsplit(".", 1)[1].lower()
    unique_id = uuid.uuid4().hex
    input_path = os.path.join(UPLOAD_FOLDER, f"temp_decode_img_{unique_id}.{ext}")

    try:
        uploaded_file.save(input_path)
        hidden_message = image_engine.decode(input_path)
        return render_template("image.html", active_page="image", active_tab="decode", decoded_message=hidden_message)
    except Exception as err:
        return render_template("image.html", active_page="image", active_tab="decode", error_message=f"Decoding failed: {err}")
    finally:
        if os.path.exists(input_path):
            try:
                os.remove(input_path)
            except OSError:
                pass


# ==========================================
# AUDIO STEGANOGRAPHY ROUTES
# ==========================================
@app.route("/audio")
def audio_tool():
    return render_template("audio.html", active_page="audio", active_tab="encode")

@app.route("/audio/encode", methods=["POST"])
def audio_encode():
    uploaded_file = request.files.get("cover_audio")
    secret_text = request.form.get("secret_text", "")

    if not uploaded_file or uploaded_file.filename == "":
        return render_template("audio.html", active_page="audio", active_tab="encode", error_message="Please choose a cover audio file.")
    if not check_extension(uploaded_file.filename, AUDIO_EXTENSIONS):
        return render_template("audio.html", active_page="audio", active_tab="encode", error_message="Supported audio formats are WAV, OGG, MP4, and MP3.")
    if secret_text.strip() == "":
        return render_template("audio.html", active_page="audio", active_tab="encode", error_message="Please enter a secret message to hide.")

    ext = uploaded_file.filename.rsplit(".", 1)[1].lower()
    unique_id = uuid.uuid4().hex
    input_path = os.path.join(UPLOAD_FOLDER, f"temp_cover_audio_{unique_id}.{ext}")
    output_path = os.path.join(UPLOAD_FOLDER, f"encoded_audio_{unique_id}.wav")

    try:
        uploaded_file.save(input_path)
        audio_engine.encode(input_path, secret_text, output_path)

        with open(output_path, "rb") as f:
            file_buffer = io.BytesIO(f.read())
        file_buffer.seek(0)

        return send_file(
            file_buffer,
            mimetype="audio/wav",
            as_attachment=True,
            download_name="encoded_audio.wav"
        )
    except ValueError as err:
        return render_template("audio.html", active_page="audio", active_tab="encode", error_message=str(err))
    except Exception as err:
        return render_template("audio.html", active_page="audio", active_tab="encode", error_message=f"Audio encoding failed: {err}")
    finally:
        for p in (input_path, output_path):
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass

@app.route("/audio/decode", methods=["POST"])
def audio_decode():
    uploaded_file = request.files.get("encoded_audio")

    if not uploaded_file or uploaded_file.filename == "":
        return render_template("audio.html", active_page="audio", active_tab="decode", error_message="Please choose a WAV audio file to decode.")
    if not check_extension(uploaded_file.filename, AUDIO_DECODE_EXTENSIONS):
        return render_template("audio.html", active_page="audio", active_tab="decode", error_message="Please upload an encoded WAV audio file (.wav).")

    unique_id = uuid.uuid4().hex
    input_path = os.path.join(UPLOAD_FOLDER, f"temp_decode_audio_{unique_id}.wav")

    try:
        uploaded_file.save(input_path)
        hidden_message = audio_engine.decode(input_path)
        return render_template("audio.html", active_page="audio", active_tab="decode", decoded_message=hidden_message)
    except Exception as err:
        return render_template("audio.html", active_page="audio", active_tab="decode", error_message=f"Audio decoding failed: {err}")
    finally:
        if os.path.exists(input_path):
            try:
                os.remove(input_path)
            except OSError:
                pass


# ==========================================
# VIDEO STEGANOGRAPHY ROUTES (100% PLAYABLE MP4)
# ==========================================
@app.route("/video")
def video_tool():
    return render_template("video.html", active_page="video", active_tab="encode")

@app.route("/video/encode", methods=["POST"])
def video_encode():
    uploaded_file = request.files.get("cover_video")
    secret_text = request.form.get("secret_text", "")

    if not uploaded_file or uploaded_file.filename == "":
        return render_template("video.html", active_page="video", active_tab="encode", error_message="Please choose a cover video first.")
    if not check_extension(uploaded_file.filename, VIDEO_EXTENSIONS):
        return render_template("video.html", active_page="video", active_tab="encode", error_message="Supported video formats are MP4, AVI, MOV, MKV, and WEBM.")
    if secret_text.strip() == "":
        return render_template("video.html", active_page="video", active_tab="encode", error_message="Please enter a secret message to hide.")

    ext = uploaded_file.filename.rsplit(".", 1)[1].lower()
    unique_id = uuid.uuid4().hex
    input_path = os.path.join(UPLOAD_FOLDER, f"temp_cover_vid_{unique_id}.{ext}")
    output_path = os.path.join(UPLOAD_FOLDER, f"encoded_vid_{unique_id}.mp4")

    try:
        uploaded_file.save(input_path)
        # Encodes directly into a 100% playable, compliant MP4 video
        video_engine.encode(input_path, secret_text, output_path)

        with open(output_path, "rb") as f:
            file_buffer = io.BytesIO(f.read())
        file_buffer.seek(0)

        return send_file(
            file_buffer,
            mimetype="video/mp4",
            as_attachment=True,
            download_name="encoded_video.mp4"
        )
    except ValueError as err:
        return render_template("video.html", active_page="video", active_tab="encode", error_message=str(err))
    except Exception as err:
        return render_template("video.html", active_page="video", active_tab="encode", error_message=f"Video encoding failed: {err}")
    finally:
        for p in (input_path, output_path):
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass

@app.route("/video/decode", methods=["POST"])
def video_decode():
    uploaded_file = request.files.get("encoded_video")

    if not uploaded_file or uploaded_file.filename == "":
        return render_template("video.html", active_page="video", active_tab="decode", error_message="Please choose a video file to decode.")
    if not check_extension(uploaded_file.filename, VIDEO_DECODE_EXTENSIONS):
        return render_template("video.html", active_page="video", active_tab="decode", error_message="Please upload a valid MP4 or AVI video file.")

    ext = uploaded_file.filename.rsplit(".", 1)[1].lower()
    unique_id = uuid.uuid4().hex
    input_path = os.path.join(UPLOAD_FOLDER, f"temp_decode_vid_{unique_id}.{ext}")

    try:
        uploaded_file.save(input_path)
        hidden_message = video_engine.decode(input_path)
        return render_template("video.html", active_page="video", active_tab="decode", decoded_message=hidden_message)
    except Exception as err:
        return render_template("video.html", active_page="video", active_tab="decode", error_message=f"Video decoding failed: {err}")
    finally:
        if os.path.exists(input_path):
            try:
                os.remove(input_path)
            except OSError:
                pass


# ==========================================
# MEDIA CONVERTER ROUTES (OGG/MP4 -> WAV & AVI -> MP4)
# ==========================================
@app.route("/converter")
def converter_page():
    return render_template("converter.html", active_page="converter")

@app.route("/converter/audio", methods=["POST"])
def convert_audio():
    uploaded_file = request.files.get("audio_file")
    if not uploaded_file or uploaded_file.filename == "":
        return render_template("converter.html", active_page="converter", error_message="Please select an audio or video file to convert.")
    if not check_extension(uploaded_file.filename, CONVERTER_AUDIO_EXTENSIONS):
        return render_template("converter.html", active_page="converter", error_message="Supported formats for WAV conversion are OGG, MP4, MP3, M4A, FLAC, and WAV.")

    ext = uploaded_file.filename.rsplit(".", 1)[1].lower()
    unique_id = uuid.uuid4().hex
    input_path = os.path.join(UPLOAD_FOLDER, f"conv_in_audio_{unique_id}.{ext}")
    output_path = os.path.join(UPLOAD_FOLDER, f"converted_audio_{unique_id}.wav")

    try:
        uploaded_file.save(input_path)
        MediaConverter.audio_to_wav(input_path, output_path)

        with open(output_path, "rb") as f:
            file_buffer = io.BytesIO(f.read())
        file_buffer.seek(0)

        base_name = uploaded_file.filename.rsplit(".", 1)[0]
        return send_file(
            file_buffer,
            mimetype="audio/wav",
            as_attachment=True,
            download_name=f"{base_name}_converted.wav"
        )
    except Exception as err:
        return render_template("converter.html", active_page="converter", error_message=f"Audio conversion failed: {err}")
    finally:
        for p in (input_path, output_path):
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass

@app.route("/converter/video", methods=["POST"])
def convert_video():
    uploaded_file = request.files.get("video_file")
    if not uploaded_file or uploaded_file.filename == "":
        return render_template("converter.html", active_page="converter", error_message="Please select a video file to convert.")
    if not check_extension(uploaded_file.filename, CONVERTER_VIDEO_EXTENSIONS):
        return render_template("converter.html", active_page="converter", error_message="Supported video formats are AVI, MKV, MOV, WEBM, FLV, WMV, and MP4.")

    ext = uploaded_file.filename.rsplit(".", 1)[1].lower()
    unique_id = uuid.uuid4().hex
    input_path = os.path.join(UPLOAD_FOLDER, f"conv_in_vid_{unique_id}.{ext}")
    output_path = os.path.join(UPLOAD_FOLDER, f"converted_vid_{unique_id}.mp4")

    try:
        uploaded_file.save(input_path)
        MediaConverter.video_to_mp4(input_path, output_path)

        with open(output_path, "rb") as f:
            file_buffer = io.BytesIO(f.read())
        file_buffer.seek(0)

        base_name = uploaded_file.filename.rsplit(".", 1)[0]
        return send_file(
            file_buffer,
            mimetype="video/mp4",
            as_attachment=True,
            download_name=f"{base_name}_converted.mp4"
        )
    except Exception as err:
        return render_template("converter.html", active_page="converter", error_message=f"Video conversion failed: {err}")
    finally:
        for p in (input_path, output_path):
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)