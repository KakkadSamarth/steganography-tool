# app.py
"""
Main application entry point for StegoVault.
Configures and launches the Flask web server with modular blueprints.
"""
import os
from flask import Flask
from config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH
from main_routes import main_bp
from image_routes import image_bp, image_engine
from audio_routes import audio_bp, audio_engine
from video_routes import video_bp, video_engine
from converter_routes import converter_bp


def create_app():
    """Application factory for StegoVault."""
    app = Flask(__name__)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Register modular blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(audio_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(converter_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)