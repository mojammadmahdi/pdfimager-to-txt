import os
import cv2
import numpy as np
from PIL import Image
import pytesseract
from pdf2image import convert_from_path, pdfinfo_from_path

# تنظیم مسیر Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# تنظیم مسیر Poppler
poppler_path = r'C:\Program Files\poppler\bin'  # مسیر دقیق Poppler را وارد کنید

# تابع پیش‌پردازش تصویر
def preprocess_image(image):
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(thresh)

# مسیر فایل PDF و خروجی
pdf_path = "input.pdf"  # مسیر فایل PDF
output_file = "output.txt"  # مسیر فایل متنی
output_image_folder = "images"  # پوشه برای تصاویر

# بررسی وجود فایل PDF
if not os.path.exists(pdf_path):
    print(f"dont found pdf {pdf_path} ")
    print("pls chek location pdf and name file")
    exit(1)

# بررسی وجود پوشه Poppler
if not os.path.exists(poppler_path):
    print(f"we can't find poppler {poppler_path} ")
    print("pls chek location poppler or install this")
    exit(1)

# بررسی وجود pdftoppm.exe
pdftoppm_path = os.path.join(poppler_path, "pdftoppm.exe")
if not os.path.exists(pdftoppm_path):
    print(f"we can't find pdftoppm.exe {pdftoppm_path}")
    exit(1)

# ایجاد پوشه تصاویر
if not os.path.exists(output_image_folder):
    os.makedirs(output_image_folder)

# بررسی دسترسی به Tesseract
try:
    print("vertion Tesseract:", pytesseract.get_tesseract_version())
except Exception as e:
    print(f"error to access Tesseract: {e}")
    print(r"pls chek install Tesseract in location C:\Program Files\Tesseract-OCR\tesseract.exe ")
    exit(1)

# بررسی دسترسی به Poppler و PDF
try:
    pdf_info = pdfinfo_from_path(pdf_path, poppler_path=poppler_path)
    print(f"information PDF: {pdf_info}")
except Exception as e:
    print(f"error to access Poppler or PDF file: {e}")
    print(f"pls chek install pdftoppm.exe in location {poppler_path} and pdf file location.")
    exit(1)

# تبدیل PDF به تصاویر
try:
    pages = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
except Exception as e:
    print(f"error pdf to image: {e}")
    exit(1)

# تنظیمات Tesseract برای فارسی
custom_config = r'--oem 3 --psm 6 -l fas'

# حلقه برای پردازش صفحات
for i, page in enumerate(pages):
    image_path = os.path.join(output_image_folder, f"page_{i+1:03d}.png")
    page.save(image_path, 'PNG')
    try:
        preprocessed_image = preprocess_image(page)
        text = pytesseract.image_to_string(preprocessed_image, config=custom_config)
        with open(output_file, "a", encoding="utf-8") as f:
           # f.write(f"متن استخراج‌شده از صفحه {i+1}:\n")
            f.write(text + "\n\n")
        print(f"gived text {image_path} sucsses.")
    except Exception as e:
        print(f"error {image_path}: {e}")


print(f"saved in {output_file}.")
