# image_routes.py
"""
Flask routes for Image Steganography (encoding and decoding).
"""
import io
import os
from flask import Blueprint, render_template, request, send_file
from config import UPLOAD_FOLDER, IMAGE_EXTENSIONS, IMAGE_DECODE_EXTENSIONS
from utils import check_extension, get_file_extension, generate_unique_filename, cleanup_files
from image_stego import ImageStegoEngine

image_bp = Blueprint("image_bp", __name__)
image_engine = ImageStegoEngine()


@image_bp.route("/image")
def image_tool():
    return render_template("image.html", active_page="image", active_tab="encode")


@image_bp.route("/image/encode", methods=["POST"])
@image_bp.route("/process_encode", methods=["POST"])  # Backwards compatibility
def image_encode():
    uploaded_file = request.files.get("cover_image")
    secret_text = request.form.get("secret_text", "")

    if not uploaded_file or uploaded_file.filename == "":
        return render_template("image.html", active_page="image", active_tab="encode", error_message="Please choose a cover image first.")
    if not check_extension(uploaded_file.filename, IMAGE_EXTENSIONS):
        return render_template("image.html", active_page="image", active_tab="encode", error_message="Supported image formats are PNG, JPG, JPEG, WEBP, and BMP.")
    if secret_text.strip() == "":
        return render_template("image.html", active_page="image", active_tab="encode", error_message="Please enter a secret message to hide.")

    ext = get_file_extension(uploaded_file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, generate_unique_filename("temp_cover_img", ext))
    output_path = os.path.join(UPLOAD_FOLDER, generate_unique_filename("encoded_img", "png"))

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
        cleanup_files(input_path, output_path)


@image_bp.route("/image/decode", methods=["POST"])
@image_bp.route("/process_decode", methods=["POST"])  # Backwards compatibility
def image_decode():
    uploaded_file = request.files.get("encoded_image")

    if not uploaded_file or uploaded_file.filename == "":
        return render_template("image.html", active_page="image", active_tab="decode", error_message="Please choose an image to decode.")
    if not check_extension(uploaded_file.filename, IMAGE_DECODE_EXTENSIONS):
        return render_template("image.html", active_page="image", active_tab="decode", error_message="Please upload a lossless PNG or BMP file.")

    ext = get_file_extension(uploaded_file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, generate_unique_filename("temp_decode_img", ext))

    try:
        uploaded_file.save(input_path)
        hidden_message = image_engine.decode(input_path)
        return render_template("image.html", active_page="image", active_tab="decode", decoded_message=hidden_message)
    except Exception as err:
        return render_template("image.html", active_page="image", active_tab="decode", error_message=f"Decoding failed: {err}")
    finally:
        cleanup_files(input_path)
