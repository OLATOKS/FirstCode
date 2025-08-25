import pytesseract
from PIL import Image
import os
import cv2

pytesseract.pytesseract.tesseract_cmd =  "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
ImgPath = (r"")
img = cv2.imread(ImgPath)

ImageCopy = img.copy()
AreaSelection = cv2.selectROI("Select the area to be read", img)

AreaSelected = ImageCopy[int(AreaSelection[1]):int(AreaSelection[1]+AreaSelection[3]), 
                         int(AreaSelection[0]):int(AreaSelection[0]+AreaSelection[2])]

gray = cv2.cvtColor(AreaSelected, cv2.COLOR_BGR2GRAY)

gray = cv2.GaussianBlur(gray,(3, 3), 0)
_, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
Text=pytesseract.image_to_string(gray, config="--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
print("Text Detected:", Text.strip())


cv2.imshow("Area selected",AreaSelected)
cv2.waitKey(0)
cv2.destroyAllWindows()

