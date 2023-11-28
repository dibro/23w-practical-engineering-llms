import PyPDF2
import pdfminer.high_level as high
import pdfminer.layout as layout
import sys
import os

def text_extraction(pdf_path):
    text = ""

    try: 
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfFileReader(file)
            num_pages = pdf_reader.numPages

            for page in range(num_pages):
                text += pdf_reader.getPage(page).extractText()

    except: # In case we fail with PyPDF2, switch to pdfminer.six
        with open(pdf_path, 'rb') as file:
            try:
                high.extract_text_to_fp(file, sys.stdout)
            except:
                print("Error occurred while extracting the PDF content")

    return text

# Try a random pdf
pdf_path = os.path.join(os.getcwd(), 'data','sample.pdf')
print(text_extraction(pdf_path))

# Mount content if using Drive
#from google.colab import drive
#drive.mount('/content/drive')
     
