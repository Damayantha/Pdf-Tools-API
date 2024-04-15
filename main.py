import pyheif
from PIL import Image


def convert_heic_to_jpg(heic_path, jpg_path):
    # Read the HEIC file
    heif_file = pyheif.read(heic_path)

    # Convert to an image that Pillow can handle
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )

    # Save the image as a JPG file
    image.save(jpg_path, "JPEG")


# Example usage
heic_path = 'image.heic'
jpg_path = 'image.jpg'
convert_heic_to_jpg(heic_path, jpg_path)
