from selenium import webdriver
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import os
import csv
import pandas as pd
import warnings
from tqdm import tqdm
import traceback
import multiprocessing
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from parsers.wb.wb_get_cards import write_to_csv

# 1) попробовать отправить request

url = 'https://www.dns-shop.ru/product/26ea6c2e3e2bed20/667-smartfon-huawei-nova-10-se-128-gb-zelenyj/'

def get_html(url):
    options = Options()
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu')  # Last I checked this was necessary.
    
    driver = webdriver.Chrome("chromedriver.exe", chrome_options=options)
    driver.get(url)

    time.sleep(2)
    driver.execute_script("window.scrollBy(0,700)")
    l = driver.find_element(By.CLASS_NAME, 'product-characteristics__expand')
    driver.execute_script("arguments[0].click();", l)
    # WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.LINK_TEXT, '"Развернуть все"'))).click()
    time.sleep(0.5)
    html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    driver.quit()
    return html

def get_sku(soup):
    return soup.find('div', attrs={'class': 'product-card-top__code'}).get_text().replace("Код товара: ","")

def get_stars(soup):
    return soup.find('a', attrs={'class': 'product-card-top__rating'})['data-rating']

def get_h1(soup):
    return soup.find('div',attrs={'class': 'product-card-top__name'}).get_text()
    # return soup.h1.string

def get_price(soup):
    try:
        return soup.find('div', attrs={'class': 'product-buy__price'}).get_text().split('₽')[0].strip().replace(" ","")
    except:
        return None

def get_description(soup):
    return soup.find('div', attrs={'class': 'product-card-description-text'}).get_text()

def get_brand(soup):
    return soup.find('img', attrs={'class': 'product-card-top__brand-image loaded'}).get('alt')

def get_tables_specifications(soup):
    return soup.find('div', attrs={'class': 'product-characteristics-content'}).find_all('div', attrs={'class': 'product-characteristics__group'})

def prepare_specifications(tables):
    data_spec_all = {}
    data_spec = []
    for table in tables:
        caption = table.find('div', attrs={'class': 'product-characteristics__group-title'}).get_text()
        for tr in table.find_all('div', attrs={'class': 'product-characteristics__spec'}):
            char = tr.find('div', attrs={'class': 'product-characteristics__spec-title'}).get_text()
            value = tr.find('div', attrs={'class': 'product-characteristics__spec-value'}).get_text()
            data_spec.append([char.strip(), value.strip()])
        data_spec_all[caption] = data_spec

    return data_spec_all

def parse_data(html, url, file_name):
    soup = BeautifulSoup(html, 'html.parser')
    h1 = get_h1(soup)
    sku = get_sku(soup)
    stars = get_stars(soup)
    price = get_price(soup)
    # print(h1,sku,stars,price)
    # # original_price = get_original_price(soup)
    description = get_description(soup)
    # print(description)
    brand = get_brand(soup)
    # print(brand)

    tables = get_tables_specifications(soup)
    # print(len(tables))
    specifications = prepare_specifications(tables) if tables else None
    # print(specifications)

    payload = {
        'title': h1,
        'sku': sku,   
        'price': price if price else None,
        'description': str(description),
        'stars': stars,
        'brand': brand,
        'specifications': specifications,
        'url':url,
    }
    # # print(description)

    write_to_csv(payload,file_name)



def main(from_val,to_val,i ):
    df = pd.read_csv("data/dns/smartphones/smartphones_dns_all.csv")
    urls = df['url'].tolist()
    urls = urls[from_val:to_val]
    file_name = "dns_data_test" + str(i) + ".csv"

    page = 0
    for url in tqdm(urls):
        try:
            print(f' url {page} processing')
            
            html = get_html(url)
            if html: 
                parse_data(html, url,file_name)
            else:
                print(f' url {page} failed {url}')
            page+=1
        except Exception:
            traceback.print_exc()
            # print("АВАРИЯ")
            # print(page, url)
            with open(f"urls_dns_failed{i}.csv",'a') as file:
                file.write(url + "\n")

    # url = 'https://www.dns-shop.ru/product/26ea6c2e3e2bed20/667-smartfon-huawei-nova-10-se-128-gb-zelenyj/'

    # html = get_html(url)

    # parse_data(html, url,"dns_dataset.csv")

    # print(html)

def main2():
    x = 1225
    for i in range(1):
        print("process number:" , i)

        processes = []
        for i in range(5):
            from_val = x
            to_val = x + 10
            p = multiprocessing.Process(target=main, args=(from_val,to_val,i,))
            p.start()
            processes.append(p)
            x += 10

        for p in processes:
            p.join()

if __name__ == '__main__':
    main2()