import io
from PIL import Image

def load_image(image_bytes: bytes) -> Image.Image:
    """
    Load an image from bytes and convert to RGB.
    """
    image = Image.open(io.BytesIO(image_bytes))
    return image.convert("RGB")
