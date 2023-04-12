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

warnings.filterwarnings("ignore")

def get_html(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')  # Last I checked this was necessary.
    # options.add_argument("--log-level=OFF")
    
    driver = webdriver.Chrome("chromedriver.exe", chrome_options=options)
    driver.get(url)
    time.sleep(3.5)
    html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    driver.quit()
    return html

def parse_data(html, url, file_name):
    soup = BeautifulSoup(html, 'html.parser')
    h1 = get_h1(soup)
    sku = get_sku(soup)
    stars = get_stars(soup)
    price = get_price(soup)
    # original_price = get_original_price(soup)
    description = get_description(soup)
    brand = get_brand(soup)

    tables = get_tables_specifications(soup)
    specifications = prepare_specifications(tables) if tables else None

    payload = {
        'title': h1,
        'sku': sku,
        'price': re.findall(r'[0-9]+', re.sub(r'\xa0', '', price))[0] if price else None,
        'description': str(description),
        'stars': stars,
        'brand': brand,
        'specifications': specifications,
        'url':url,
    }
    # print(description)

    write_to_csv(payload,file_name)

def write_to_csv(data, filename):
    # filename = 'wildberries_data_test.csv'
    if os.path.isfile(filename):
        with open (filename,"a", encoding="utf-8", newline='') as file:
            columns = ['sku','brand',"title", "price",'stars','url', 'description', 'specifications']
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writerow(data)
    else:
        with open (filename,"w", encoding="utf-8", newline='') as file:
            columns = ['sku','brand',"title", "price",'stars','url', 'description', 'specifications']
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            # print(data)
            writer.writerow(data)

def get_sku(soup):
    return soup.find('span', attrs={'id': 'productNmId'}).get_text()

def get_stars(soup):
    return soup.find('div', attrs={'class': 'product-page__common-info'}).find('span', attrs={'data-link': 'text{: product^star}'}).get_text()

# def get_original_price(soup):
#     return soup.find('del', attrs={'class': 'price-block__old-price j-final-saving j-wba-card-item-show'}).get_text()

def get_h1(soup):
    return soup.h1.string

def get_price(soup):
    try:
        return soup.find('ins', attrs={'class': 'price-block__final-price'}).get_text()
    except:
        return None

def get_description(soup):
    return soup.find('p', attrs={'class': 'collapsable__text'}).get_text()

def get_brand(soup):
    return soup.find('div', attrs={'class': 'product-page__brand-logo hide-mobile'}).find('a').get('title')

def get_tables_specifications(soup):
    return soup.find('div', attrs={'class': 'collapsable__content j-add-info-section'}).find_all('table')

def prepare_specifications(tables):
    data_spec_all = {}
    data_spec = []
    for table in tables:
        caption = table.find('caption').get_text()
        for tr in table.find_all('tr'):
            char = tr.find('th').get_text()
            value = tr.find('td').get_text()
            data_spec.append([char.strip(), value.strip()])
        data_spec_all[caption] = data_spec

    return data_spec_all

def main(from_val,to_val,i):
    # url = 'https://www.wildberries.ru/catalog/139656805/detail.aspx'
    # url = "https://www.wildberries.ru/catalog/elektronika/smartfony-i-telefony/vse-smartfony"
    df = pd.read_csv("data/wb/smartphones/smartphones_wb_all.csv")
    urls = df['url'].tolist()
    # print(len(urls))
    # urls = urls[800:1100]
    urls = urls[from_val:to_val]
    file_name = "wb_data_test" + str(i) + ".csv"
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
            with open(f"urls_failed{i}.csv",'a') as file:
                file.write(url + "\n")

def main2():
    x = 8200
    for i in range(2):
        print("process number:" , i)

        processes = []
        for i in range(5):
            from_val = x
            to_val = x + 7
            p = multiprocessing.Process(target=main, args=(from_val,to_val,i,))
            p.start()
            processes.append(p)
            x += 7

        for p in processes:
            p.join()
        
    

    
def main3(i):
    failed_file_name = f"new_urls_failed{i}.csv"
    with open(failed_file_name, "r", newline="") as file:
        reader = csv.reader(file)
        file_name = "wb_data_test" + str(i) + ".csv"
        for row in tqdm(reader):
            try:
                url = row[0]
                html = get_html(url)
                if html: 
                    parse_data(html, url,file_name)
            except Exception:
                traceback.print_exc()
                # print("АВАРИЯ")
                # print(page, url)
                with open(f"urls_failed{i}.csv",'a') as file:
                    file.write(url + "\n")

def main4():
    processes = []
    for i in range(5):
        p = multiprocessing.Process(target=main3, args=(i,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
        # df = pd.read_csv(file_name)
        # print(f' i = {i}, shape = {df.shape}')



    # start_url = "https://www.wildberries.ru/catalog/111864727/detail.aspx"

    # html = get_html(start_url)
    # if html: 
    #     parse_data(html, start_url)

if __name__ == '__main__':
    main2()

# print(1)

# url = "https://www.wildberries.ru/catalog/13615125/detail.aspx"



# options = Options()
# options.add_argument('--headless')
# options.add_argument('--disable-gpu')  # Last I checked this was necessary.
# driver = webdriver.Chrome("chromedriver.exe", chrome_options=options)
# # driver = webdriver.Chrome("chromedriver.exe")
# driver.get(url)

# # html = driver.page_source

# time.sleep(5)
# # print(html)

# html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
# # print(html)
# soup = BeautifulSoup(html, 'html.parser')

# print(soup.h1.string)
# print(soup.find('ins', attrs={'class': 'price-block__final-price'}).get_text())
# print(soup.find('p', attrs={'class': 'collapsable__text'}).get_text())
# tables = soup.find('div', attrs={'class': 'collapsable__content j-add-info-section'}).find_all('table')
# print(prepare_specifications(tables))


# url = "https://www.wildberries.ru/catalog/139656805/detail.aspx?targetUrl=MI"

# driver.get(url)
# time.sleep(5)
# driver.quit()