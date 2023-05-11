import multiprocessing
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm


def main(start,end,i):
    df_books_cg = pd.read_csv('data/cg_books_data.csv')
    options = Options()
    options.add_argument('--headless')

    driver = webdriver.Chrome("chromedriver.exe")
    for id, row in tqdm(df_books_cg[start:end].iterrows()):
        url = row['url']
        # print(url)
        driver.get(url)
        time.sleep(0.5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        specs = soup.find_all('div',class_ = 'product-detail-characteristics__item')
        res_specs = {}
        for spec in specs:
            title = spec.find('span',class_ = 'product-detail-characteristics__item-title').text
            try:
                value = spec.find('span',class_ = 'product-detail-characteristics__item-value').text
            except:
                value = spec.find('a').text
            if 'ID' not in title:
                res_specs[title.strip()] = value.strip()
        
        df_books_cg.at[id,'specifications'] = res_specs

    driver.quit()
        

    df_books_cg[start:end].to_csv(f'data/cg_books_updated_{i}.csv',index=False)
    print('ready')


def main2():
    processes = []
    from_val = 3500
    for i in range(7):
        print(i, from_val)
        p = multiprocessing.Process(target=main, args=(from_val,from_val+10,i,))
        p.start()
        processes.append(p)
        from_val += 10

    for p in processes:
        p.join()

if __name__ == '__main__':
    main(3570,3571,0)

