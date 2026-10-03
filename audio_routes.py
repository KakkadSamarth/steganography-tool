# audio_routes.py
"""
Flask routes for Audio Steganography (encoding and decoding).
"""
import io
import os
from flask import Blueprint, render_template, request, send_file
from config import UPLOAD_FOLDER, AUDIO_EXTENSIONS, AUDIO_DECODE_EXTENSIONS
from utils import check_extension, get_file_extension, generate_unique_filename, cleanup_files
from audio_stego import AudioStegoEngine

audio_bp = Blueprint("audio_bp", __name__)
audio_engine = AudioStegoEngine()


@audio_bp.route("/audio")
def audio_tool():
    return render_template("audio.html", active_page="audio", active_tab="encode")


@audio_bp.route("/audio/encode", methods=["POST"])
def audio_encode():
    uploaded_file = request.files.get("cover_audio")
    secret_text = request.form.get("secret_text", "")

    if not uploaded_file or uploaded_file.filename == "":
        return render_template("audio.html", active_page="audio", active_tab="encode", error_message="Please choose a cover audio file.")
    if not check_extension(uploaded_file.filename, AUDIO_EXTENSIONS):
        return render_template("audio.html", active_page="audio", active_tab="encode", error_message="Supported audio formats are WAV, OGG, MP4, and MP3.")
    if secret_text.strip() == "":
        return render_template("audio.html", active_page="audio", active_tab="encode", error_message="Please enter a secret message to hide.")

    ext = get_file_extension(uploaded_file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, generate_unique_filename("temp_cover_audio", ext))
    output_path = os.path.join(UPLOAD_FOLDER, generate_unique_filename("encoded_audio", "wav"))

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
        cleanup_files(input_path, output_path)


@audio_bp.route("/audio/decode", methods=["POST"])
def audio_decode():
    uploaded_file = request.files.get("encoded_audio")

    if not uploaded_file or uploaded_file.filename == "":
        return render_template("audio.html", active_page="audio", active_tab="decode", error_message="Please choose a WAV audio file to decode.")
    if not check_extension(uploaded_file.filename, AUDIO_DECODE_EXTENSIONS):
        return render_template("audio.html", active_page="audio", active_tab="decode", error_message="Please upload an encoded WAV audio file (.wav).")

    input_path = os.path.join(UPLOAD_FOLDER, generate_unique_filename("temp_decode_audio", "wav"))

    try:
        uploaded_file.save(input_path)
        hidden_message = audio_engine.decode(input_path)
        return render_template("audio.html", active_page="audio", active_tab="decode", decoded_message=hidden_message)
    except Exception as err:
        return render_template("audio.html", active_page="audio", active_tab="decode", error_message=f"Audio decoding failed: {err}")
    finally:
        cleanup_files(input_path)
