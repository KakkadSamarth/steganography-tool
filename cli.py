# cli.py
"""
StegoVault Command Line Interface.
Allows quick terminal-based encoding and decoding for images, audio, and video.
"""
import sys
from image_stego import ImageStegoEngine
from audio_stego import AudioStegoEngine
from video_stego import VideoStegoEngine


def print_help():
    print("StegoVault CLI Tool")
    print("Usage:")
    print("  python cli.py image encode <cover_image> <secret_text> <output_png>")
    print("  python cli.py image decode <image_file>")
    print("  python cli.py audio encode <cover_audio> <secret_text> <output_wav>")
    print("  python cli.py audio decode <audio_file>")
    print("  python cli.py video encode <cover_video> <secret_text> <output_mp4>")
    print("  python cli.py video decode <video_file>")


def main():
    if len(sys.argv) < 3:
        print_help()
        return

    media_type = sys.argv[1].lower()
    action = sys.argv[2].lower()

    engines = {
        "image": ImageStegoEngine,
        "audio": AudioStegoEngine,
        "video": VideoStegoEngine,
    }

    if media_type not in engines:
        print(f"Error: Unknown media type '{media_type}'. Supported: image, audio, video")
        return

    engine = engines[media_type]()

    if action == "encode":
        if len(sys.argv) < 6:
            print("Error: encode requires <cover_path> <secret_text> <output_path>")
            return
        cover_path, text, output_path = sys.argv[3], sys.argv[4], sys.argv[5]
        try:
            engine.encode(cover_path, text, output_path)
            print(f"[SUCCESS] Secret successfully hidden into: {output_path}")
        except Exception as e:
            print(f"[ERROR] Encoding failed: {e}")

    elif action == "decode":
        if len(sys.argv) < 4:
            print("Error: decode requires <file_path>")
            return
        input_path = sys.argv[3]
        try:
            result = engine.decode(input_path)
            print(f"[RESULT] Decoded message: {result}")
        except Exception as e:
            print(f"[ERROR] Decoding failed: {e}")

    else:
        print(f"Error: Unknown action '{action}'. Supported: encode, decode")


if __name__ == "__main__":
    main()
