# app.py
import os
import uuid
import io
from flask import Flask, render_template, request, send_file

from stego_engine import SteganographyEngine

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# FIXED: Use the correct class name that was imported
engine = SteganographyEngine()

ALLOWED_EXTENSIONS = {"png"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/process_encode", methods=["POST"])
def process_encode():
    uploaded_file = request.files.get("cover_image")
    secret_text = request.form.get("secret_text", "")

    if not uploaded_file or uploaded_file.filename == "":
        return "No image selected!", 400
    if not allowed_file(uploaded_file.filename):
        return "Please upload a PNG image.", 400
    if secret_text.strip() == "":
        return "Please type a secret message first.", 400

    # FIXED: Generate unique filenames to prevent simultaneous users from overwriting each other
    unique_id = uuid.uuid4().hex
    input_path = os.path.join(UPLOAD_FOLDER, f"temp_cover_{unique_id}.png")
    output_path = os.path.join(UPLOAD_FOLDER, f"encoded_output_{unique_id}.png")
    
    uploaded_file.save(input_path)

    try:
        engine.encode(input_path, secret_text, output_path)
    except ValueError as error:
        os.remove(input_path) # Clean up on error
        return str(error), 400

    # FIXED: Load into memory so we can delete the file before sending the response
    with open(output_path, "rb") as f:
        file_buffer = io.BytesIO(f.read())
    file_buffer.seek(0)

    # Clean up both temp files off the hard drive immediately
    os.remove(input_path)
    os.remove(output_path)

    return send_file(
        file_buffer, 
        mimetype="image/png", 
        as_attachment=True, 
        download_name="encoded_secret.png"
    )

@app.route("/process_decode", methods=["POST"])
def process_decode():
    uploaded_file = request.files.get("encoded_image")

    if not uploaded_file or uploaded_file.filename == "":
        return "No image selected!", 400

    unique_id = uuid.uuid4().hex
    input_path = os.path.join(UPLOAD_FOLDER, f"temp_decode_{unique_id}.png")
    uploaded_file.save(input_path)

    hidden_message = engine.decode(input_path)
    
    os.remove(input_path)

    return render_template("index.html", decoded_message=hidden_message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)