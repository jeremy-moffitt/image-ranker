import os
from PIL import Image
from PIL.ExifTags import TAGS
import exifread
import exif

# def get_exif_data(image_path):
#     """
#     Extracts EXIF metadata from an image.
#     """
#     with open(image_path, 'rb') as img_file:
#         tags = exifread.process_file(img_file)
#         sorted_keys = sorted(tags)
#         for tag in sorted_keys:
#             if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename'):
#                 print(f"{tag}: {tags[tag]}")

def get_exif_data(image_path):
    with open(image_path, 'rb') as img_file:
        image = exif.Image(img_file)
        simplified_details = [
                    [image.aperture_value],
                    [image.shutter_speed_value],
                    [image.exposure_index],
                    [image.photographic_sensitivity]
                ]
        print(simplified_details)
        # list_all = sorted(image.list_all())
        # print(list_all)
        # for tag in list_all:
        #     print(f"{tag}: {image.get(tag)}")


# Example usage:
image_file = "./images/img.jpg"  # Replace with the path to your image
get_exif_data(image_file)

# if metadata:
#     print(f"Metadata for {image_file}:")
#     for key, value in metadata.items():
#         print(f"  {key}: {value}")
# else:
#     print(f"No EXIF metadata found for {image_file} or an error occurred.")