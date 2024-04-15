from PDFNetPython3.PDFNetPython import PDFDoc, Optimizer, SDFDoc, PDFNet
from pdf2image import convert_from_path
from pdf2pptx import convert_pdf2pptx
from pdf2docx import parse
import PyPDF2
import fitz
import os


class PDFOps:

    def __init__(self, token: str = "", show_empty_token_warning: bool = True) -> None:
        self.PDFNet_token = token
        if (token == "" and show_empty_token_warning):
            print("[#] You have not provided token for the PDFNet SDK, you wont be able to compress pdf without it.")
            print(
                "[$] To obtain a demo token, head to 'https://dev.apryse.com/get-key', after signin, choose web and get the trial key.")
            print("[!] You can turn off this warning but passing 'show_empty_token_warning = False'.")

    def __total_pages(self, pdf_file: str) -> int:
        try:
            with open(pdf_file, 'rb') as pdf:
                pdf_reader = PyPDF2.PdfReader(pdf)
                return len(pdf_reader.pages)
        except Exception as err:
            print(f"An exception has occured while accessing pdf. Hint: {err}")
            return 0

    def __get_size_format(b, factor=1024, suffix="B"):
        for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
            if b < factor:
                return f"{b:.2f}{unit}{suffix}"
            b /= factor
        return f"{b:.2f}Y{suffix}"

    def compress_pdf(self, input_pdf: str, output_pdf: str) -> dict:

        try:
            PDFNet.Initialize(self.PDFNet_token)
            doc = PDFDoc(input_pdf)
            doc.InitSecurityHandler()
            Optimizer.Optimize(doc)
            doc.Save(output_pdf, SDFDoc.e_linearized)
            doc.Close()
        except Exception as err:
            print(f"An error occured while compressing pdf. Hint: {err}")
            doc.Close()
            return {
                "status": "failure",
                "initial_size": 0,
                "compressed_size": 0,
                "ratio": 0
            }

        initial_size = os.path.getsize(input_pdf)
        compressed_size = os.path.getsize(output_pdf)
        ratio = 1 - (compressed_size / initial_size)

        result = {
            "status": "success",
            "initial_size": self.__get_size_format(initial_size),
            "compressed_size": self.__get_size_format(compressed_size),
            "ratio": "{0:.3%}.".format(ratio)
        }

        return result

    def convert_to_pptx(self, input_pdf: str, output_pdf: str) -> bool:

        pages = self.__total_pages(input_pdf)

        try:
            convert_pdf2pptx(input_pdf, output_pdf, 500, 0, pages)
        except Exception as err:
            print(f"An error occured while converting pdf to pptx. Hint: {err}")
            return False

        return True

    def convert_to_doc(self, input_pdf: str, output_pdf: str) -> bool:

        try:
            parse(input_pdf, output_pdf)
        except Exception as err:
            print(f"An error occured while converting pdf to doc. Hint: {err}")
            return False

        return True

    def extract_pages_as_images(self, input_pdf: str, output_folder: str) -> bool:

        try:
            os.makedirs(output_folder, exist_ok=True)
        except Exception as err:
            print(f"An error occured while creating directory for images. Hint: {err}")

        try:
            images = convert_from_path(input_pdf)
            for index, image in enumerate(images):
                image_file = f"{output_folder}/page_{index + 1}.jpg"
                image.save(image_file, 'JPEG')
        except Exception as err:
            print(f"An error has occured while converting pdf to doc. Hint: {err}")
            return False

        return True

    def split_pdf(self, input_pdf: str, output_folder: str, page_ranges: list[list[int]]) -> bool:

        try:
            pdf_document = fitz.open(input_pdf)
            index = 0

            for page_range in page_ranges:
                start_page, end_page = page_range
                if start_page > end_page or start_page < 1 or end_page > pdf_document.page_count:
                    print(f"Invalid page range: {page_range}. Skipping...")
                    continue
                new_pdf = fitz.open()
                new_pdf.insert_pdf(pdf_document, from_page=start_page - 1, to_page=end_page - 1)
                temp_file_path = f"{output_folder}/{index}_pages_{start_page}-{end_page}.pdf"
                ind += 1
                new_pdf.save(temp_file_path)
                new_pdf.close()

            pdf_document.close()
        except Exception as err:
            print(f"An error has occured while splitting pdf. Hint: {err}")
            return False

        return True

    def merge_pdfs(self, input_pdfs: list[str], output_pdf: str) -> bool:

        try:
            merged_pdf = fitz.open()
            pdf_paths = []

            for pdf in input_pdfs:
                formatted_pdf_name = pdf.filename.replace(" ", "_")
                pdf_paths.append(formatted_pdf_name)

            for pdf_file in pdf_paths:
                pdf_document = fitz.open(pdf_file)
                for page_number in range(pdf_document.page_count):
                    merged_pdf.insert_pdf(pdf_document, from_page=page_number, to_page=page_number)
                pdf_document.close()
            merged_pdf.save(output_pdf)
            merged_pdf.close()
        except Exception as err:
            print(f"An error has occured while merging pdfs. Hint: {err}")
            return False

        return True

    def encrypt_pdf(self, input_pdf: str, output_pdf: str, password: str) -> bool:

        try:
            inp_pdf = PyPDF2.PdfReader(input_pdf)
            outp_pdf = PyPDF2.PdfWriter()
            if inp_pdf.is_encrypted:
                print("[!] PDF is already encrypted!")
                return False
            for pageNum in range(len(inp_pdf.pages)):
                outp_pdf.add_page(inp_pdf.pages[pageNum])

            outp_pdf.encrypt(password)

            result_pdf = open(output_pdf, "wb")
            outp_pdf.write(result_pdf)
            result_pdf.close()
        except Exception as err:
            print(f"An error has occured while encrypted pdf. Hint: {err}")
            return False

        return True

    def decrypt_pdf(self, input_pdf: str, output_pdf: str, password: str) -> bool:

        try:
            inp_pdf = PyPDF2.PdfReader(input_pdf)
            outp_pdf = PyPDF2.PdfWriter()
            if not inp_pdf.is_encrypted:
                print("[!] PDF does not have any encryption!")
                return False

            inp_pdf.decrypt(password)

            for pageNum in range(len(inp_pdf.pages)):
                outp_pdf.add_page(inp_pdf.pages[pageNum])
            result_pdf = open(output_pdf, "wb")
            outp_pdf.write(result_pdf)
            result_pdf.close()
        except Exception as err:
            print(f"An error has occured while decrypted pdf. Hint: {err}")
            return False

        return True