print("Environment Creating......")
import subprocess
subprocess.check_call(['pip', 'install', 'pandas'])
subprocess.check_call(['pip', 'install', 'selenium'])
subprocess.check_call(['pip', 'install', 'webdriver_manager'])
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
from webdriver_manager.chrome import ChromeDriverManager
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument(
    'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36')
# options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("lang=en-GB")
chrome_options.add_argument('--ignore-certificate-errors')
# self.options.add_argument('--lang=en')
chrome_options.add_argument('--allow-running-insecure-content')
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--proxy-server='direct://'")
chrome_options.add_argument("--proxy-bypass-list=*")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')
# self.options.add_argument("--log-level=OFF")
chrome_options.add_argument("--log-level=3")
# driver = webdriver.Chrome(ChromeDriverManager().install())
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.maximize_window()

driver.get("https://www.the-numbers.com/movies/franchises")
time.sleep(1)
select = Select(driver.find_element(By.TAG_NAME, 'select'))
select.select_by_visible_text('100')

gc = pd.DataFrame()
last_page = int(driver.find_elements(By.CSS_SELECTOR, "#franchise_overview_paginate > span > a:nth-child(n)")[-1].text)
for b in range(last_page):
    td = driver.find_elements(By.CSS_SELECTOR,
                              "#franchise_overview > tbody > tr:nth-child(n) > td:nth-child(1) > b > a")
    for a in range(len(td)):
        fra_name = td[a].text
        fra_u = td[a].get_attribute("href")
        Dic = {'Franchise': fra_name, 'fra_link': fra_u}
        gc = pd.concat([gc, pd.DataFrame([Dic])], ignore_index=True)

    driver.find_element(By.CSS_SELECTOR, "#franchise_overview_next").click()
    if b != 0:
        print(f"extracted {len(gc)} franchises")
    # if b==1:
    #     break
print(f"franchises extraction completed\n\n")
time.sleep(2)
print(f"Extracting Final Data.....")

gc2 = pd.DataFrame()
for d in range(len(gc)):
    gc1 = pd.DataFrame()
    driver.get(gc.fra_link[d])
    time.sleep(2)
    td = driver.find_elements(By.CSS_SELECTOR,
                              "#franchise_movies_overview > tbody > tr:nth-child(n) > td:nth-child(2) > b > a")
    td1 = driver.find_elements(By.CSS_SELECTOR, "#franchise_movies_overview > tbody > tr:nth-child(n) > td.sorting_1")
    for c in range(len(td)):
        if td[c].text.split(" ")[0] != "Untitled":
            try:
                date = td1[c].text.split(",")[-1]
            except:
                date = td1[c].text
            Dic = {'Franchise': gc.Franchise[d], 'Movie_title': td[c].text, 'Release_date': date}
            gc1 = pd.concat([gc1, pd.DataFrame([Dic])], ignore_index=True)

    driver.get("https://www.imdb.com/?ref_=nv_home")

    time.sleep(2)

    for e in range(0, len(gc1)):

        inp = driver.find_element(By.CSS_SELECTOR, "#suggestion-search")
        txt = gc1.Movie_title[e] + " " + gc1.Release_date[e]
        inp.send_keys(txt)
        inp.send_keys(Keys.ENTER)
        driver.find_element(By.CSS_SELECTOR,
                            "#__next > main > div.ipc-page-content-container.ipc-page-content-container--full.sc-4f91839f-0.hmcKDt > div.ipc-page-content-container.ipc-page-content-container--center > section > div > div.ipc-page-grid__item.ipc-page-grid__item--span-2 > section:nth-child(3) > div.sc-17bafbdb-2.ffAEHI > ul > li:nth-child(1) > div.ipc-metadata-list-summary-item__c > div > a").click()
        im = driver.current_url
        imdb = im.split("/")[-2]
        # print(imdb)
        Dic = {'Franchise': gc1.Franchise[e], 'Movie_title': gc1.Movie_title[e], 'Release_Year': gc1.Release_date[e],
               'IMDB_id': imdb}
        gc2 = pd.concat([gc2, pd.DataFrame([Dic])], ignore_index=True)
        if len(gc2) % 10 == 0:
            # gc2 = gc2.drop(gc2.columns[0], axis=1)
            gc2.to_excel("Output.xlsx")
            print(f"Extraxted {len(gc2)} Data")
gc2.to_excel("Output.xlsx")
print("Extraction Successfully Completed!!!!")

