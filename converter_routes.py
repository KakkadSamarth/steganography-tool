# converter_routes.py
"""
Flask routes for Media Format Converter (Audio/Video to WAV/MP4).
"""
import io
import os
from flask import Blueprint, render_template, request, send_file
from config import UPLOAD_FOLDER, CONVERTER_AUDIO_EXTENSIONS, CONVERTER_VIDEO_EXTENSIONS
from utils import check_extension, get_file_extension, generate_unique_filename, cleanup_files
from media_converter import MediaConverter

converter_bp = Blueprint("converter_bp", __name__)


@converter_bp.route("/converter")
def converter_page():
    return render_template("converter.html", active_page="converter")


@converter_bp.route("/converter/audio", methods=["POST"])
def convert_audio():
    uploaded_file = request.files.get("audio_file")
    if not uploaded_file or uploaded_file.filename == "":
        return render_template("converter.html", active_page="converter", error_message="Please select an audio or video file to convert.")
    if not check_extension(uploaded_file.filename, CONVERTER_AUDIO_EXTENSIONS):
        return render_template("converter.html", active_page="converter", error_message="Supported formats for WAV conversion are OGG, MP4, MP3, M4A, FLAC, and WAV.")

    ext = get_file_extension(uploaded_file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, generate_unique_filename("conv_in_audio", ext))
    output_path = os.path.join(UPLOAD_FOLDER, generate_unique_filename("converted_audio", "wav"))

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
        cleanup_files(input_path, output_path)


@converter_bp.route("/converter/video", methods=["POST"])
def convert_video():
    uploaded_file = request.files.get("video_file")
    if not uploaded_file or uploaded_file.filename == "":
        return render_template("converter.html", active_page="converter", error_message="Please select a video file to convert.")
    if not check_extension(uploaded_file.filename, CONVERTER_VIDEO_EXTENSIONS):
        return render_template("converter.html", active_page="converter", error_message="Supported video formats are AVI, MKV, MOV, WEBM, FLV, WMV, and MP4.")

    ext = get_file_extension(uploaded_file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, generate_unique_filename("conv_in_vid", ext))
    output_path = os.path.join(UPLOAD_FOLDER, generate_unique_filename("converted_vid", "mp4"))

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
        cleanup_files(input_path, output_path)
