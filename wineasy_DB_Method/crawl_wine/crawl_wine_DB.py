from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import mysql.connector
import time

# MySQL 데이터베이스 연결 설정
db_config = {
    'user': 'root',
    'password': '1234',
    'host': 'localhost',
    'database': 'wine_DB'
}

# MySQL 연결
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Chrome WebDriver 설정 (경로를 자신의 webdriver 경로로 설정)
driver_path = 'C:/BEN/chromedriver-win64/chromedriver.exe'
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service)

# 페이지 범위 설정
start_index = 5
end_index = 2228

def get_element_text(selector, parent=None, multiple=False):
    try:
        if multiple:
            if parent:
                elements = parent.find_elements(By.CSS_SELECTOR, selector)
            else:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
            return ', '.join([elem.text for elem in elements])
        else:
            if parent:
                return parent.find_element(By.CSS_SELECTOR, selector).text
            else:
                return driver.find_element(By.CSS_SELECTOR, selector).text
    except NoSuchElementException:
        return None

def extract_first_value(text):
    if text:
        return text.split(' > ')[0].split(' / ')[0].strip()
    return None

def get_wine_type():
    for i in range(1, 12):
        selector = f'#container > div.productView.cont > div.tag > span.tag{i}'
        wine_type = get_element_text(selector)
        if wine_type:
            return wine_type
    return None

def exclude_first_word(text):
    if text:
        parts = text.split(' ')
        if len(parts) > 1:
            return ' '.join(parts[1:])
    return text

for i in range(start_index, end_index + 1):
    print(f"현재 크롤링 중인 인덱스: {i}")  # 현재 인덱스를 출력하는 로그 추가
    url = f"https://www.shinsegae-lnb.com/html/product/wineView.html?idx={i}&s_brand=&s_style=&s_food=&s_daily=&s_sort=N&s_type=0&s_nation=0&s_region=0&s_page=1&s_data="
    driver.get(url)
    time.sleep(2)  # 페이지 로드를 기다리기 위해 잠시 대기

    try:
        # 페이지에 데이터가 있는지 확인
        if "페이지를 찾을 수 없습니다" in driver.page_source:
            print(f"Page {i} not found.")
            continue

        wine_name_ko_raw = get_element_text('#container > div.productView.cont > div:nth-child(3) > div.left > h3')
        wine_name_en_raw = get_element_text('#container > div.productView.cont > div:nth-child(3) > div.left > p.nameEng')
        wine_name_ko = exclude_first_word(wine_name_ko_raw)
        wine_name_en = exclude_first_word(wine_name_en_raw)
        
        country_raw = get_element_text('#container > div.productView.cont > div:nth-child(3) > div.right > table > tbody > tr:nth-child(1) > td')
        
        # Find the second parent div with class 'productInner col2'
        parent_divs = driver.find_elements(By.CSS_SELECTOR, '.productInner.col2')
        if len(parent_divs) > 1:
            second_parent_div = parent_divs[1]
            unnamed_div = second_parent_div.find_elements(By.TAG_NAME, 'div')[0]
            taste = get_element_text('.textDes', unnamed_div)
        else:
            taste = None
        
        wine_type = get_wine_type()
        recommended_dish = get_element_text('#container > div.productView.cont > div:nth-child(3) > div.right > table > tbody > tr:nth-child(4) > td', multiple=True)

        country = extract_first_value(country_raw)

        wine_sweet = len(driver.find_elements(By.CSS_SELECTOR, '#container > div.productView.cont > div.productInner.img > div.features > dl:nth-child(1) > dd .on'))
        wine_body = len(driver.find_elements(By.CSS_SELECTOR, '#container > div.productView.cont > div.productInner.img > div.features > dl:nth-child(3) > dd .on'))
        wine_acidity = len(driver.find_elements(By.CSS_SELECTOR, '#container > div.productView.cont > div.productInner.img > div.features > dl:nth-child(2) > dd .on'))

        # 각 요소를 출력하여 확인
        print(f"wine_name_ko_raw: {wine_name_ko_raw}")
        print(f"wine_name_ko: {wine_name_ko}")
        print(f"wine_name_en_raw: {wine_name_en_raw}")
        print(f"wine_name_en: {wine_name_en}")
        print(f"country: {country}")
        print(f"taste: {taste}")
        print(f"wine_type: {wine_type}")
        print(f"wine_sweet: {wine_sweet}")
        print(f"wine_body: {wine_body}")
        print(f"wine_acidity: {wine_acidity}")
        print(f"recommended_dish: {recommended_dish}")

        # MySQL에 데이터 추가
        columns = ["wine_name_ko", "wine_name_en", "wine_type", "wine_country", "wine_sweet", "wine_body", "wine_acidity", "wine_tasting_note", "recommended_dish"]
        values = [wine_name_ko, wine_name_en, wine_type, country, wine_sweet, wine_body, wine_acidity, taste, recommended_dish]

        # 빈 값들을 제외하고 삽입 쿼리를 생성
        insert_columns = []
        insert_values = []
        for col, val in zip(columns, values):
            if val is not None:
                insert_columns.append(col)
                insert_values.append(val)

        if insert_columns and insert_values:
            insert_query = f"INSERT INTO wine_sinsegae ({', '.join(insert_columns)}) VALUES ({', '.join(['%s'] * len(insert_values))})"
            cursor.execute(insert_query, insert_values)
            conn.commit()
        else:
            print(f"Skipping insertion for page {i} due to missing data.")

    except Exception as e:
        print(f"Error on {i}: {e}")
        continue

# WebDriver 종료
driver.quit()

# MySQL 연결 종료
cursor.close()
conn.close()