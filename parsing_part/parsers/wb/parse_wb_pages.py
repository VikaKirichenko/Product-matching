
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd

url = 'https://www.wildberries.ru/catalog/elektronika/smartfony-i-telefony/vse-smartfony'
url = 'https://www.wildberries.ru/catalog/elektronika/smartfony-i-telefony/vse-smartfony?sort=popular&page=13'
try:
        # service = Service(executable_path='chromedriver')  # указываем путь до драйвера
    browser = webdriver.Chrome("chromedriver.exe")
    browser.get(url)
    time.sleep(2)
    df = pd.DataFrame()
    names = []
    brands = []
    prices = []
    urls = []
    h_prev = 0
    while True:
        h = browser.execute_script('return window.innerHeight + window.scrollY;')
        browser.execute_script(f'window.scrollTo(0,{h});')
        # browser.execute_script("window.scrollBy(0,700)")
        try:
            """применим неявные ожидания, будем пролистывать, пока элемент не станет кликабельным"""
            time.sleep(0.5)
            
            if h == h_prev:
                print("h=h_prev")
                goods = browser.find_elements(By.CLASS_NAME, 'goods-name')
                names.extend([i.text for i in goods])
                goods_brand = browser.find_elements(By.CLASS_NAME, 'brand-name')
                brands.extend([i.text for i in goods_brand])
                print("brands",len(brands))
                goods_price = browser.find_elements(By.CLASS_NAME, 'price__lower-price')
                # print("pr",len(prices))
                prices.extend([price.text.replace('\u00a0','').replace('\u20bd','').replace(" ","").strip() for price in goods_price])
                # print("prices",len(prices))
                goods_url = browser.find_elements(By.CLASS_NAME, 'j-card-link')
                # print("url",len(goods_url))
                urls.extend([i.get_attribute('href') for i in goods_url])
                try:
                    
                    WebDriverWait(browser, 1).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Следующая страница'))).click()
                    continue
                except:
                    break
            h_prev = h
        except:
            continue

    df['name'] = names
    df['brand'] = brands
    df['price'] = prices
    df['url'] = urls
    df['category'] = ['smartphones'] * len(names)
    df.to_csv('test.csv')
    # time.sleep(5)
    # soup = BeautifulSoup(browser.page_source, 'html.parser')
    # name = soup.find('span', attrs={'class': 'goods-name'}).get_text()
    # print(name)
    # time.sleep(10)
    browser.quit()
except Exception as ex:
    print(ex)
    browser.quit()
browser.quit()