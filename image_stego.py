# image_stego.py
"""
Image Steganography Engine using Least Significant Bit (LSB) encoding on RGB channels.
"""
from PIL import Image
from config import DELIMITER


class ImageStegoEngine:
    """Engine for hiding and extracting secret text in image pixels using LSB."""

    def __init__(self, delimiter=DELIMITER):
        self.delimiter = delimiter

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
        """Embeds secret text into the LSB of RGB image channels and saves as PNG."""
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
        """Extracts secret text from the LSB of image channels."""
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
