# stego_engine.py
import os
import wave
import subprocess
from PIL import Image
import numpy as np
import cv2
import imageio_ffmpeg

# Get static FFmpeg executable bundled with imageio-ffmpeg
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()


class MediaConverter:
    """Helper service to convert multimedia formats seamlessly."""

    @staticmethod
    def audio_to_wav(input_path, output_path):
        """Converts any audio or video file (OGG, MP4, MP3, etc.) to uncompressed 16-bit PCM WAV."""
        cmd = [
            FFMPEG_PATH, "-y",
            "-i", input_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "44100",
            "-ac", "2",
            output_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            err_msg = res.stderr.decode("utf-8", errors="ignore")
            raise ValueError(f"Audio conversion to WAV failed: {err_msg}")
        return output_path

    @staticmethod
    def video_to_mp4(input_path, output_path):
        """Converts any video format (AVI, MKV, MOV, etc.) into a universally playable standard H.264 MP4."""
        cmd = [
            FFMPEG_PATH, "-y",
            "-i", input_path,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            output_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            err_msg = res.stderr.decode("utf-8", errors="ignore")
            raise ValueError(f"Video conversion to MP4 failed: {err_msg}")
        return output_path


class ImageStegoEngine:
    def __init__(self):
        # Delimiter used to mark the end of the secret message
        self.delimiter = b"#####"

    def _text_to_binary(self, text):
        byte_data = text.encode("utf-8")
        return "".join([format(b, "08b") for b in byte_data])

    def get_capacity(self, image_path):
        """Returns maximum secret text characters/bytes the image can hold."""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                max_bits = width * height * 3
                max_bytes = max_bits // 8 - len(self.delimiter)
                return max(0, max_bytes)
        except Exception:
            return 0

    def encode(self, image_path, secret_text, output_path):
        full_text = secret_text + "#####"
        binary_secret = self._text_to_binary(full_text)
        data_len = len(binary_secret)

        image = Image.open(image_path).convert("RGB")
        width, height = image.size

        max_capacity = width * height * 3
        if data_len > max_capacity:
            max_chars = max_capacity // 8 - len(self.delimiter)
            raise ValueError(f"Message is too long to fit in this image! (Max capacity: {max(0, max_chars)} characters)")

        pixels = image.load()
        data_index = 0

        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                rgb = [r, g, b]

                for i in range(3):
                    if data_index < data_len:
                        bit = binary_secret[data_index]
                        rgb[i] = (rgb[i] & ~1) | int(bit)
                        data_index += 1

                pixels[x, y] = tuple(rgb)
                
                if data_index >= data_len:
                    image.save(output_path, "PNG")
                    return

        image.save(output_path, "PNG")

    def decode(self, image_path):
        image = Image.open(image_path).convert("RGB")
        width, height = image.size
        pixels = image.load()

        binary_data = ""
        decoded_bytes = bytearray()

        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                
                for value in (r, g, b):
                    binary_data += str(value & 1)

                while len(binary_data) >= 8:
                    byte_str = binary_data[:8]
                    binary_data = binary_data[8:]
                    decoded_bytes.append(int(byte_str, 2))

                    if decoded_bytes.endswith(self.delimiter):
                        clean_bytes = decoded_bytes[:-len(self.delimiter)]
                        try:
                            return clean_bytes.decode("utf-8")
                        except UnicodeDecodeError:
                            return "Error: Found hidden data, but it was corrupted or not valid text."

        return "No hidden message found (or this image wasn't encoded)."


class AudioStegoEngine:
    def __init__(self):
        self.delimiter = b"#####"

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
        # Auto-convert OGG, MP4, MP3, etc. to clean WAV if needed
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


class VideoStegoEngine:
    def __init__(self):
        self.marker = b"__STEGO_VAULT_v2__"
        self.delimiter = b"__END_STEGO_VAULT__"
        # Fallback delimiter for raw LSB legacy files
        self.legacy_delimiter = b"#####"

    def encode(self, video_path, secret_text, output_path):
        """
        Embeds a secret message into a 100% playable, standard MP4 video.
        The resulting MP4 plays seamlessly in Windows Media Player, QuickTime,
        Chrome, Edge, VLC, and mobile devices without any playback errors.
        """
        ext = video_path.rsplit(".", 1)[-1].lower() if "." in video_path else ""
        temp_mp4 = None
        source_mp4 = video_path

        # If source is not already an MP4, convert it to a standard playable MP4 first
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
        First checks the standard playable MP4 container payload;
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


# Backward-compatible alias
SteganographyEngine = ImageStegoEngine