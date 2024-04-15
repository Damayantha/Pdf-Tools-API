import docx2pdf


def convert_docx_to_pdf(docx_file, pdf_file):
    docx2pdf.convert(docx_file, pdf_file)


# Example usage
docx_file = "Samples/First Six week reoport.docx"
pdf_file = "Samples/my_document.pdf"
convert_docx_to_pdf(docx_file, pdf_file)
