from PIL import Image, TiffImagePlugin
from PIL.ExifTags import TAGS
import io

def resize_image(image_path, new_size, encode_format='PNG'):
    img = Image.open(image_path)
    img = img.resize(new_size, Image.Resampling.LANCZOS) # Use LANCZOS for high quality resizing
    with io.BytesIO() as buffer:
        img.save(buffer, format=encode_format)
        data = buffer.getvalue()
    return data

def get_exif_data(image_path):
    with (Image.open(image_path) as img):
        exif_data = img._getexif()
        details = {}
        if not exif_data:
            return None
        else:
            for k, v in exif_data.items():
                details.update({TAGS.get(k): v})

            return details

def sanitise_exif_value(value):
    """Recursively sanitizes IFDRational and byte-string values."""
    if isinstance(value, TiffImagePlugin.IFDRational):
        return float(value)
    elif isinstance(value, dict):
        return {k: sanitise_exif_value(v) for k, v in value.items()}
    elif isinstance(value, (list, tuple)):
        return [sanitise_exif_value(i) for i in value]
    elif isinstance(value, bytes):
        # Decode byte strings to make them JSON serializable if needed
        return value.decode('utf-8', errors='ignore') 
    else:
        return value