from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd


url = 'https://www.dns-shop.ru/catalog/17a8a01d16404e77/smartfony/?p=56'
try:
        # service = Service(executable_path='chromedriver')  # указываем путь до драйвера
    browser = webdriver.Chrome("chromedriver.exe")
    browser.get(url)
    df = pd.DataFrame()
    names = []
    brands = []
    prices = []
    urls = []
    h_prev = 0
    time.sleep(5)
    page = 56
    while True:
        h = browser.execute_script('return window.innerHeight + window.scrollY;')
        browser.execute_script(f'window.scrollTo(0,{h});')
        # browser.execute_script("window.scrollBy(0,500)")
        try:
            """применим неявные ожидания, будем пролистывать, пока элемент не станет кликабельным"""
            time.sleep(0.5)
            # WebDriverWait(browser, 1).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Показать ещё'))).click()
            if h == h_prev:
                print("h=h_prev")
                
                try:
                    print(page)
                    goods = browser.find_elements(By.CLASS_NAME, 'catalog-product__name')
                    names.extend([i.text for i in goods])
                    print("names",len(names))
                    # goods_brand = browser.find_elements(By.CLASS_NAME, 'brand-name')
                    # brands.extend([i.text for i in goods_brand])
                    # print("brands",len(brands))
                    goods_price = browser.find_elements(By.CLASS_NAME, 'product-buy__price')
                    # print("pr",len(prices))
                    prices.extend([price.text.replace('\u00a0','').replace('\u20bd','').replace(" ","").strip() for price in goods_price])
                    print("prices",len(prices))
                    goods_url = browser.find_elements(By.CLASS_NAME, 'catalog-product__name')
                    # print("url",len(goods_url))
                    urls.extend([i.get_attribute('href') for i in goods_url])
                    print("urls",len(urls))

                    if page==72:
                        break
                    l = browser.find_element(By.CLASS_NAME, 'pagination-widget__page-link_next')
                    browser.execute_script("arguments[0].click();", l)
                    page+=1
                    continue
                except:
                    print("АВАРИЯ")
                    break
            h_prev = h
        except:
            continue


    print(len(names))
    print(len(prices))
    print(len(urls))
    df['name'] = names
    df['brand'] = [""]* len(names)
    df['price'] = prices
    df['url'] = urls
    df['category'] = ['smartphones'] * len(names)
    df.to_csv('smartphones_dns4.csv')
    browser.quit()
except Exception as ex:
    print(ex)
    browser.quit()
browser.quit()