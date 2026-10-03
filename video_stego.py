# video_stego.py
"""
Video Steganography Engine for MP4 container embedding and legacy video LSB extraction.
"""
import os
import cv2
import numpy as np
from config import DELIMITER, VIDEO_MARKER, VIDEO_DELIMITER
from media_converter import MediaConverter


class VideoStegoEngine:
    """Engine for hiding and extracting secret text in video files."""

    def __init__(self, marker=VIDEO_MARKER, delimiter=VIDEO_DELIMITER, legacy_delimiter=DELIMITER):
        self.marker = marker
        self.delimiter = delimiter
        self.legacy_delimiter = legacy_delimiter

    def encode(self, video_path, secret_text, output_path):
        """
        Embeds a secret message into a 100% playable, standard MP4 video.
        The resulting MP4 plays seamlessly across all media players.
        """
        ext = video_path.rsplit(".", 1)[-1].lower() if "." in video_path else ""
        temp_mp4 = None
        source_mp4 = video_path

        # If source is not already an MP4, convert it to standard playable MP4 first
        if ext != "mp4":
            temp_mp4 = video_path + "_playable_temp.mp4"
            MediaConverter.video_to_mp4(video_path, temp_mp4)
            source_mp4 = temp_mp4

        try:
            payload = self.marker + secret_text.encode("utf-8") + self.delimiter

            with open(source_mp4, "rb") as f_in, open(output_path, "wb") as f_out:
                # Write standard MP4 video stream untouched (guarantees 100% playback)
                f_out.write(f_in.read())
                # Append invisible steganography payload to the MP4 container
                f_out.write(payload)
        finally:
            if temp_mp4 and os.path.exists(temp_mp4):
                try:
                    os.remove(temp_mp4)
                except OSError:
                    pass

    def decode(self, video_path):
        """
        Decodes hidden messages from video files.
        First checks standard playable MP4 container payload;
        falls back to pixel-level LSB extraction for legacy AVI files.
        """
        # 1. Primary Check: Playable MP4 container payload
        try:
            with open(video_path, "rb") as f:
                content = f.read()

            m_idx = content.rfind(self.marker)
            if m_idx != -1:
                d_idx = content.find(self.delimiter, m_idx)
                if d_idx != -1:
                    raw_payload = content[m_idx + len(self.marker):d_idx]
                    try:
                        return raw_payload.decode("utf-8")
                    except UnicodeDecodeError:
                        return "Error: Found hidden data, but it was corrupted."
        except Exception:
            pass

        # 2. Secondary Fallback Check: Raw pixel LSB (for legacy AVI files)
        try:
            cap = cv2.VideoCapture(video_path)
            if cap.isOpened():
                remainder_bits = np.array([], dtype=np.uint8)
                decoded_bytes = bytearray()
                found_message = None

                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    bits = frame.reshape(-1) & 1
                    if remainder_bits.size > 0:
                        combined_bits = np.concatenate([remainder_bits, bits])
                    else:
                        combined_bits = bits

                    n_bytes = len(combined_bits) // 8
                    usable_bits = n_bytes * 8
                    packed = np.packbits(combined_bits[:usable_bits]).tobytes()
                    remainder_bits = combined_bits[usable_bits:]
                    decoded_bytes += packed

                    delim_idx = decoded_bytes.find(self.legacy_delimiter)
                    if delim_idx != -1:
                        clean_bytes = decoded_bytes[:delim_idx]
                        try:
                            found_message = clean_bytes.decode("utf-8")
                        except UnicodeDecodeError:
                            found_message = "Error: Found hidden data, but it was corrupted or not valid text."
                        break
                cap.release()

                if found_message is not None:
                    return found_message
        except Exception:
            pass

        return "No hidden message found (or this video wasn't encoded)."
