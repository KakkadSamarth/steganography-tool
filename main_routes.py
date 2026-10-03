# main_routes.py
"""
Flask routes for the main navigation hub and tool selector.
"""
from flask import Blueprint, render_template

main_bp = Blueprint("main_bp", __name__)


@main_bp.route("/")
def home():
    """Main landing hub to choose between Image, Audio, Video tools or Media Converter."""
    return render_template("index.html", active_page="hub")
