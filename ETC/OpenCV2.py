import sys
import cv2
import numpy as np
import pytesseract
import os

# wineReader 모듈이 있는 경로 추가
toolkit_path = 'D:/CHW/workspace/Wineasy/wine_label_reader_toolkit-master/'
sys.path.append(toolkit_path)

from wineReader.labelVision import load_unet_model

# 사용자 환경에 맞게 경로 설정
image_path = 'D:/CHW/workspace/Wineasy/wineImage/import/01082024_015107_unwrapped.jpg'  # 입력 이미지 경로
output_path = 'D:/CHW/workspace/Wineasy/wineImage/export/01082024_015107_unwrapped_processed.jpg'  # 전처리된 이미지 저장 경로
model_path = 'D:/CHW/workspace/Wineasy/wine_label_reader_toolkit-master/models/unet-20220314-134823.hdf5'  # 모델 파일 경로
tesseract_cmd_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # 시스템에 설치된 Tesseract 경로로 변경 필요

# 이미지 불러오기
image = cv2.imread(image_path)
if image is None:
    raise Exception("이미지를 불러올 수 없습니다. 경로를 확인하세요.")

# 모델 로드
model = load_unet_model(model_path)
if model is None:
    raise Exception("모델을 로드하는 중에 오류가 발생했습니다.")

# 이미지 전처리
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
alpha = 1.5  # 대비
beta = 50    # 밝기
adjusted = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
denoised = cv2.medianBlur(adjusted, 3)
binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
kernel = np.ones((5, 5), np.uint8)
erosion = cv2.erode(binary, kernel, iterations=1)
dilation = cv2.dilate(erosion, kernel, iterations=1)

# 이미지 저장 (전처리 결과 확인용)
cv2.imwrite(output_path, dilation)

# Tesseract 경로 설정
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_path

# 텍스트 인식 설정
custom_config = r'--oem 3 --psm 6'
text = pytesseract.image_to_string(dilation, config=custom_config)

print(text)