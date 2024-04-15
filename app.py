import os
import shutil
import uuid
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException
from PIL import Image
import fitz

app = FastAPI()

TEMP_DIR = "./static/temp"
os.makedirs(TEMP_DIR, exist_ok=True)

PDF_DIR = "./static/pdf"
os.makedirs(PDF_DIR, exist_ok=True)

IMAGE_DIR = "./static/images"
os.makedirs(IMAGE_DIR, exist_ok=True)


def images_to_pdf(image_files: List[Image.Image], output_pdf_path: str):
    """
    Convert a list of image files to a single PDF file with A4 page size.
    """
    a4_width, a4_height = 2480, 3508
    converted_images = []

    for img in image_files:
        ratio = min(a4_width / img.width, a4_height / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img_resized = img.resize(new_size, Image.LANCZOS)
        a4_page = Image.new('RGB', (a4_width, a4_height), 'white')
        paste_position = ((a4_width - new_size[0]) // 2, (a4_height - new_size[1]) // 2)
        a4_page.paste(img_resized, paste_position)
        converted_images.append(a4_page)

    converted_images[0].save(output_pdf_path, save_all=True, append_images=converted_images[1:], resolution=300)


def convert_pdf_to_images(pdf_path: str) -> List[str]:
    """
    Convert a PDF file to images, save them to a directory,
    and return the paths to these images.
    """
    doc = fitz.open(pdf_path)
    image_paths = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        image_name = f"image_{page_num}.png"
        image_path = os.path.join(IMAGE_DIR, image_name)
        pix.save(image_path)
        image_paths.append(image_path)

    doc.close()
    return image_paths


@app.post('/convert-pdf-to-images')
async def api_convert_pdf_to_images(pdf: UploadFile = File(...)):
    pdf_filename = str(uuid.uuid4()) + '.pdf'
    pdf_path = os.path.join(PDF_DIR, pdf_filename)

    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(pdf.file, f)

    image_paths = convert_pdf_to_images(pdf_path)
    os.remove(pdf_path)

    zip_filename = str(uuid.uuid4()) + '.zip'
    zip_path = os.path.join(app.root_path, 'static', zip_filename)
    shutil.make_archive(zip_path[:-4], 'zip', IMAGE_DIR)

    for image_path in image_paths:
        os.remove(image_path)

    download_url = f"{app.root_path}/static/{zip_filename}"
    return {"download_url": download_url}


@app.post('/convert-to-pdf')
async def convert_to_pdf(images: List[UploadFile] = File(...)):
    if not images or images[0].filename == '':
        raise HTTPException(status_code=400, detail="No images provided")

    output_pdf_name = str(uuid.uuid4()) + '.pdf'
    output_pdf_path = os.path.join(TEMP_DIR, output_pdf_name)

    image_files = [Image.open(await img.read()) for img in images]
    images_to_pdf(image_files, output_pdf_path)

    pdf_url = f"{app.root_path}/static/temp/{output_pdf_name}"
    return {"download_url": pdf_url}
