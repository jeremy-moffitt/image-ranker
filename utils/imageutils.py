from PIL import Image
import io

def resize_image(image_path, new_size, encode_format='PNG'):
    img = Image.open(image_path)
    img = img.resize(new_size, Image.Resampling.LANCZOS) # Use LANCZOS for high quality resizing
    with io.BytesIO() as buffer:
        img.save(buffer, format=encode_format)
        data = buffer.getvalue()
    return data