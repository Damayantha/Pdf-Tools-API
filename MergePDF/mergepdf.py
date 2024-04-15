import fitz  # PyMuPDF
import os


def merge_pdfs(paths, output):
    merged_document = fitz.open()  # Create a new PDF to merge files into
    for path in paths:
        document = fitz.open(path)  # Open the current PDF
        merged_document.insert_pdf(document)  # Insert the entire PDF document
    merged_document.save(
        output)  # Save the merged PDF to the specified output path  # Save the merged PDF to the specified output path


pdf_folder = 'Samples'

# List all image files in the directory
pdf_files = [os.path.join(pdf_folder, f) for f in os.listdir(pdf_folder) if
             f.endswith('.pdf')]
# List of PDF files to merge
output_path = 'Samples/merged.pdf'  # Path to save the merged PDF
merge_pdfs(pdf_files, output_path)
