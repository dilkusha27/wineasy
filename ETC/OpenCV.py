import numpy as np
import cv2
import pytesseract

# 이미지 불러오기
image = cv2.imread('D:/CHW/workspace/Wineasy/wineImage/import/01082024_015107_unwrapped.jpg')
if image is None:
    raise Exception("이미지를 불러올 수 없습니다. 경로를 확인하세요.")

# 그레이스케일 변환
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 밝기 및 대비 조정
alpha = 0.3  # 대비
beta = 0     # 밝기
adjusted = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)

# 노이즈 제거
denoised = cv2.medianBlur(adjusted, 3)

# 이진화 (경계선 제거 전에 수행)
binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

# 경계선 제거
kernel = np.ones((5, 5), np.uint8)
erosion = cv2.erode(binary, kernel, iterations=1)
dilation = cv2.dilate(erosion, kernel, iterations=1)

# 이미지 저장 (전처리 결과 확인용)
cv2.imwrite('D:/CHW/workspace/Wineasy/wineImage/export/01082024_015107_unwrapped.jpg', dilation)

# Tesseract 경로 설정 (시스템에 설치된 경로로 변경 필요)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 텍스트 인식 설정
custom_config = r'--oem 3 --psm 6'
text = pytesseract.image_to_string(dilation, config=custom_config)

print(text)