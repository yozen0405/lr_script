import os

BASE_DIR = os.getcwd()
IMG_DIR = os.path.join(BASE_DIR, "bin", "img")
TMP_DIR = os.path.join(BASE_DIR, "bin", "tmp")

DEFAULT_THRESHOLD = 0.7
CHECK_INTERVAL = 0.3
WAIT_TIME_DEFAULT = 0.1

GAME_PACKAGE = "com.linecorp.LGRGS"

TESSERACT_BIN = os.path.join("bin", "tesseract_ocr", "tesseract.exe")
TESSDATA_DIR = os.path.join("bin", "tesseract_ocr", "tessdata")
TESSERACT_LANG = "eng"

OCR_CONFIG_BASIC = "--psm 6"
OCR_CONFIG_NUMERICAL = r'--oem 3 --psm 13 -c tessedit_char_whitelist=0123456789 -c classify_bln_numeric_mode=1'

DIGIT_TEMPLATE_DIR = os.path.join(IMG_DIR, "shared", "ocr", "digit_templates")