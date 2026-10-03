# audio_stego.py
"""
Audio Steganography Engine using Least Significant Bit (LSB) encoding on PCM WAV audio frames.
"""
import os
import wave
import numpy as np
from config import DELIMITER
from media_converter import MediaConverter


class AudioStegoEngine:
    """Engine for hiding and extracting secret text in audio samples using LSB."""

    def __init__(self, delimiter=DELIMITER):
        self.delimiter = delimiter

    def _text_to_binary(self, text):
        byte_data = text.encode("utf-8")
        return "".join([format(b, "08b") for b in byte_data])

    def get_capacity(self, audio_path):
        """Returns maximum secret text characters/bytes the audio can hold."""
        try:
            with wave.open(audio_path, "rb") as song:
                total_frames = song.getnframes()
                sampwidth = song.getsampwidth()
                nchannels = song.getnchannels()
                total_bytes = total_frames * nchannels * sampwidth
                max_bytes = total_bytes // 8 - len(self.delimiter)
                return max(0, max_bytes)
        except Exception:
            return 0

    def encode(self, audio_path, secret_text, output_path):
        """Embeds secret text into audio frames and saves as WAV."""
        is_temp_wav = False
        temp_wav_path = None
        current_audio = audio_path

        ext = audio_path.rsplit(".", 1)[-1].lower() if "." in audio_path else ""
        if ext != "wav":
            temp_wav_path = audio_path + "_temp_converted.wav"
            MediaConverter.audio_to_wav(audio_path, temp_wav_path)
            current_audio = temp_wav_path
            is_temp_wav = True

        try:
            full_text = secret_text + "#####"
            binary_secret = self._text_to_binary(full_text)
            data_len = len(binary_secret)

            try:
                with wave.open(current_audio, "rb") as song:
                    params = song.getparams()
                    frames = bytearray(song.readframes(song.getnframes()))
            except Exception as e:
                raise ValueError(f"Could not read audio file: {e}. Please ensure it is a valid audio file.")

            if data_len > len(frames):
                max_chars = len(frames) // 8 - len(self.delimiter)
                raise ValueError(f"Message is too long to fit in this audio! Max capacity: {max(0, max_chars)} characters.")

            for i in range(data_len):
                bit = int(binary_secret[i])
                frames[i] = (frames[i] & 0xFE) | bit

            with wave.open(output_path, "wb") as output_song:
                output_song.setparams(params)
                output_song.writeframes(frames)
        finally:
            if is_temp_wav and temp_wav_path and os.path.exists(temp_wav_path):
                try:
                    os.remove(temp_wav_path)
                except OSError:
                    pass

    def decode(self, audio_path):
        """Extracts secret text from WAV audio frames."""
        try:
            with wave.open(audio_path, "rb") as song:
                frames = bytearray(song.readframes(song.getnframes()))
        except Exception as e:
            return f"Error reading audio file: {e}. Please ensure it is a valid WAV file."

        if not frames:
            return "Audio file contains no audio data."

        raw_arr = np.frombuffer(frames, dtype=np.uint8)
        packed_bytes = np.packbits(raw_arr & 1).tobytes()

        delim_idx = packed_bytes.find(self.delimiter)
        if delim_idx != -1:
            clean_bytes = packed_bytes[:delim_idx]
            try:
                return clean_bytes.decode("utf-8")
            except UnicodeDecodeError:
                return "Error: Found hidden data, but it was corrupted or not valid text."

        return "No hidden message found (or this audio file wasn't encoded)."
