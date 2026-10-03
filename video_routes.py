# video_routes.py
"""
Flask routes for Video Steganography (encoding and decoding).
"""
import io
import os
from flask import Blueprint, render_template, request, send_file
from config import UPLOAD_FOLDER, VIDEO_EXTENSIONS, VIDEO_DECODE_EXTENSIONS
from utils import check_extension, get_file_extension, generate_unique_filename, cleanup_files
from video_stego import VideoStegoEngine

video_bp = Blueprint("video_bp", __name__)
video_engine = VideoStegoEngine()


@video_bp.route("/video")
def video_tool():
    return render_template("video.html", active_page="video", active_tab="encode")


@video_bp.route("/video/encode", methods=["POST"])
def video_encode():
    uploaded_file = request.files.get("cover_video")
    secret_text = request.form.get("secret_text", "")

    if not uploaded_file or uploaded_file.filename == "":
        return render_template("video.html", active_page="video", active_tab="encode", error_message="Please choose a cover video first.")
    if not check_extension(uploaded_file.filename, VIDEO_EXTENSIONS):
        return render_template("video.html", active_page="video", active_tab="encode", error_message="Supported video formats are MP4, AVI, MOV, MKV, and WEBM.")
    if secret_text.strip() == "":
        return render_template("video.html", active_page="video", active_tab="encode", error_message="Please enter a secret message to hide.")

    ext = get_file_extension(uploaded_file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, generate_unique_filename("temp_cover_vid", ext))
    output_path = os.path.join(UPLOAD_FOLDER, generate_unique_filename("encoded_vid", "mp4"))

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
        cleanup_files(input_path, output_path)


@video_bp.route("/video/decode", methods=["POST"])
def video_decode():
    uploaded_file = request.files.get("encoded_video")

    if not uploaded_file or uploaded_file.filename == "":
        return render_template("video.html", active_page="video", active_tab="decode", error_message="Please choose a video file to decode.")
    if not check_extension(uploaded_file.filename, VIDEO_DECODE_EXTENSIONS):
        return render_template("video.html", active_page="video", active_tab="decode", error_message="Please upload a valid MP4 or AVI video file.")

    ext = get_file_extension(uploaded_file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, generate_unique_filename("temp_decode_vid", ext))

    try:
        uploaded_file.save(input_path)
        hidden_message = video_engine.decode(input_path)
        return render_template("video.html", active_page="video", active_tab="decode", decoded_message=hidden_message)
    except Exception as err:
        return render_template("video.html", active_page="video", active_tab="decode", error_message=f"Video decoding failed: {err}")
    finally:
        cleanup_files(input_path)
