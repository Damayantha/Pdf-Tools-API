from pypdfops import PDFOps
input_pdf = "Samples/temp.pdf"
output_pdf = "compressed_output.pdf"
pdf = PDFOps(token = "COMPRESSION_TOKEN") # Token for compression
pdf.compress_pdf(input_pdf, output_pdf)