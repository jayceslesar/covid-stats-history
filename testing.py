import io
import requests
import PyPDF2

url = "https://www.medrxiv.org/content/10.1101/2020.05.23.20111021v2.full.pdf"
response = requests.get(url, stream=True)
pdf = PyPDF2.PdfFileReader(io.BytesIO(response.content))

with open('output.txt', 'w') as f_output:
    for page in range(pdf.getNumPages()):
        f_output.write(str(pdf.getPage(page).extractText()))