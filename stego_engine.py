# stego_engine.py
from PIL import Image

class SteganographyEngine:
    def __init__(self):
        # We use bytes instead of a string to handle raw UTF-8 data safely.
        self.delimiter = b"#####"

    def _text_to_binary(self, text):
        # Convert text into UTF-8 bytes first. This ensures emojis and 
        # special characters are properly chunked into 8-bit blocks.
        byte_data = text.encode("utf-8")
        
        # Turn each byte into an 8-bit binary string
        binary_result = "".join([format(b, "08b") for b in byte_data])
        return binary_result

    def encode(self, image_path, secret_text, output_path):
        # 1. Attach the delimiter as a string before converting
        full_text = secret_text + "#####"

        # 2. Convert to binary
        binary_secret = self._text_to_binary(full_text)
        data_len = len(binary_secret)

        # 3. Open image
        image = Image.open(image_path).convert("RGB")
        width, height = image.size

        # 4. Check capacity
        max_capacity = width * height * 3
        if data_len > max_capacity:
            raise ValueError("Message is too long to fit in this image!")

        pixels = image.load()
        data_index = 0

        # 5. Hide the bits
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
                
                # Check if we are done hiding data. If so, immediately 
                # save and return to avoid looping through the rest of the image.
                if data_index >= data_len:
                    image.save(output_path, "PNG")
                    return

        # Fallback save (only reached if the message takes exactly 100% of the image)
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
                
                # Grab the last bit of R, G, and B
                for value in (r, g, b):
                    binary_data += str(value & 1)

                # Process in 8-bit chunks
                while len(binary_data) >= 8:
                    byte_str = binary_data[:8]
                    binary_data = binary_data[8:]
                    
                    # Convert the 8-bit string back to an integer byte
                    decoded_bytes.append(int(byte_str, 2))

                    # Check if our byte array ends with the delimiter bytes
                    if decoded_bytes.endswith(self.delimiter):
                        # Chop off the delimiter
                        clean_bytes = decoded_bytes[:-len(self.delimiter)]
                        
                        try:
                            # Convert bytes back to a UTF-8 string
                            return clean_bytes.decode("utf-8")
                        except UnicodeDecodeError:
                            return "Error: Found hidden data, but it was corrupted or not valid text."

        return "No hidden message found (or this image wasn't encoded)."