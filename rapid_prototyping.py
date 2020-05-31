import pdfreader
from pdfreader import PDFDocument, SimplePDFViewer
import sys

t = ""
fd = open(r"pdfs\curr.pdf", "rb")
doc = PDFDocument(fd)
all_pages = [p for p in doc.pages()]
viewer = SimplePDFViewer(fd)

for p in range(len(all_pages)):
    viewer.navigate(p + 1)
    viewer.render()
    print(u"".join(viewer.canvas.strings).encode(sys.stdout.encoding, errors='replace').decode("windows-1252"))
    t += (u"".join(viewer.canvas.strings).encode(sys.stdout.encoding, errors='replace').decode("windows-1252"))

# print(t)
