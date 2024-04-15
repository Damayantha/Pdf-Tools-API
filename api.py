import os
import shutil
import uuid
import fitz
from PIL import Image
from flask import Flask, request, jsonify

app = Flask(__name__)

TEMP_DIR = os.path.join(app.root_path, 'static', 'temp')
os.makedirs(TEMP_DIR, exist_ok=True)  # Ensure TEMP_DIR exists


def images_to_pdf(image_files, output_pdf_path):
    """
    Convert a list of image files (file storage objects) to a single PDF file with A4 page size.
    """
    # A4 size at 300 dpi in pixels
    a4_width, a4_height = 2480, 3508
    converted_images = []

    for image_file in image_files:
        img = Image.open(image_file).convert("RGB")
        ratio = min(a4_width / img.width, a4_height / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
        a4_page = Image.new('RGB', (a4_width, a4_height), 'white')
        paste_position = ((a4_width - new_size[0]) // 2, (a4_height - new_size[1]) // 2)
        a4_page.paste(img_resized, paste_position)
        converted_images.append(a4_page)

    # Ensure the PDF is saved and closed before sending
    converted_images[0].save(output_pdf_path, save_all=True, append_images=converted_images[1:], resolution=300)


# Ensure the static directory exists
static_dir = os.path.join(app.root_path, 'static')
os.makedirs(static_dir, exist_ok=True)

PDF_DIR = os.path.join(app.root_path, 'static', 'pdf')
os.makedirs(PDF_DIR, exist_ok=True)  # Ensure PDF_DIR exists

# Specify the directory where images are stored
IMAGE_DIR = os.path.join(app.root_path, 'static', 'images')
os.makedirs(IMAGE_DIR, exist_ok=True)  # Ensure IMAGE_DIR exists


def convert_pdf_to_images(pdf_path):
    """
    Convert a PDF file to images, save them to a directory,
    and return the paths to these images.
    """
    doc = fitz.open(pdf_path)
    image_paths = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # Load the current page
        pix = page.get_pixmap()
        image_name = f"image_{page_num}.png"
        image_path = os.path.join(IMAGE_DIR, image_name)
        pix.save(image_path)
        image_paths.append(image_path)

    doc.close()
    return image_paths


@app.route('/convert-pdf-to-images', methods=['POST'])
def api_convert_pdf_to_images():
    # Check for PDF file in the request
    if 'pdf' not in request.files:
        return jsonify({"error": "PDF file is required."}), 400

    pdf_file = request.files['pdf']
    pdf_filename = str(uuid.uuid4()) + '.pdf'
    pdf_path = os.path.join(PDF_DIR, pdf_filename)
    pdf_file.save(pdf_path)

    image_paths = convert_pdf_to_images(pdf_path)

    # Cleanup temporary PDF file
    os.remove(pdf_path)

    # Compress images into a ZIP file
    zip_filename = str(uuid.uuid4()) + '.zip'
    zip_path = os.path.join(app.root_path, 'static', zip_filename)
    shutil.make_archive(zip_path[:-4], 'zip', IMAGE_DIR)

    # Remove individual image files
    for image_path in image_paths:
        os.remove(image_path)

    download_url = f"{request.url_root}static/{zip_filename}"
    return jsonify({"download_url": download_url})


@app.route('/convert-to-pdf', methods=['POST'])
def convert_to_pdf():
    # Check for images in the request
    if 'images' not in request.files:
        return jsonify({"error": "No images part in the request"}), 400

    files = request.files.getlist('images')

    if not files or files[0].filename == '':
        return jsonify({"error": "No images provided"}), 400

    # Generate a unique filename for the output PDF
    output_pdf_name = str(uuid.uuid4()) + '.pdf'  # Example: '7b2a4cf2-4a49-4d6a-a9d0-f8a6151a053e.pdf'
    output_pdf_path = os.path.join(TEMP_DIR, output_pdf_name)
    images_to_pdf(files, output_pdf_path)

    # Construct the download URL for the created PDF
    pdf_url = f"{request.url_root}static/temp/{output_pdf_name}"

    return jsonify({"download_url": pdf_url})


if __name__ == '__main__':
    app.run(debug=True)
