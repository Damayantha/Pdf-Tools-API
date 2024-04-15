from pdf2docx import Converter

pdf_file = 'Samples/Scan 09 Mar 24 13·44·39.pdf'
docx_file = 'Samples/sample.docx'

# convert pdf to docx
cv = Converter(pdf_file)
cv.convert(docx_file)  # all pages by default
cv.close()
