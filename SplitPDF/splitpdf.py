import fitz  # Import PyMuPDF


def split_pdf_ranges(input_pdf, output_folder, ranges):
    doc = fitz.open(input_pdf)  # Open the source PDF
    for i, page_range in enumerate(ranges):
        # Create a new PDF document for the current range
        split_doc = fitz.open()
        # Add pages for the current range
        split_doc.insert_pdf(doc, from_page=page_range[0] - 1, to_page=page_range[1] - 1)
        # Define the output file name
        output_path = f"{output_folder}/pages_{page_range[0]}_{page_range[1]}.pdf"
        # Save the PDF file for the current range
        split_doc.save(output_path)
        split_doc.close()  # Close the split document
    doc.close()  # Close the source document


input_pdf_path = 'Samples/input.pdf'

# List of PDF files to merge
page_ranges = [(400, 450)]
output_path = 'Samples'
split_pdf_ranges(input_pdf_path, output_path, page_ranges)
