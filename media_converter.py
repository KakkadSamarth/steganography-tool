# media_converter.py
"""
Media conversion service using bundled FFmpeg for audio and video transcoding.
"""
import subprocess
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
