from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class Franchises:

    def __init__(self):
        self.franchise_final_df = pd.DataFrame()

    def get_driver(self, headless: bool, install=True):
        options = webdriver.ChromeOptions()
        if headless is True:
            options.add_argument("--headless")
        options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36')
        # options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("lang=en-GB")
        options.add_argument('--ignore-certificate-errors')
        # self.options.add_argument('--lang=en')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument("--disable-extensions")
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        options.add_argument("--start-maximized")
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        # self.options.add_argument("--log-level=OFF")
        options.add_argument("--log-level=3")

        # path = os.path.join(os.getcwd(), 'chromedriver.exe')
        # driver = webdriver.Chrome(path)

        if install:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        return driver

    def searching_movie(self, driver, movie_title):
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//input[@id='suggestion-search']"))).send_keys(movie_title)
        driver.find_element(By.XPATH, "//input[@id='suggestion-search']").send_keys(Keys.ENTER)

    # Attempt #1
    def try_1(self, driver2, release_year):
        movie = driver2.find_element(By.XPATH, "//section[@data-testid='find-results-section-title']//ul").find_elements(By.XPATH, ".//li")[0]
        name = movie.find_element(By.XPATH, ".//a").text
        link = movie.find_element(By.XPATH, ".//a").get_attribute("href")
        year = movie.text.strip().split("\n")[1]
        imdb_id = link.split("/")[-2]
        return imdb_id, year


    # Attempt #2
    def try_2(self, driver2, release_year):
        WebDriverWait(driver2, 2).until(EC.presence_of_element_located((By.XPATH, '//table[@class="findList"]')))
        link = driver2.find_element(By.XPATH, '//table[@class="findList"]//tr[1]//td[2]//a').get_attribute('href')
        # year = driver.find_element(By.XPATH, '//table[@class="findList"]//tr[1]//td[2]').text.split("(")[-1].replace(")", '')
        year = driver2.find_element(By.XPATH, '//table[@class="findList"]//tr[1]//td[2]').text
        name = driver2.find_element(By.XPATH, '//table[@class="findList"]//tr[1]//td[2]//a').text
        imdb_id = link.split("/")[-2]
        return imdb_id, year

    # Attempt #3
    def try_3(self, driver2, release_year):
        WebDriverWait(driver2, 5).until(EC.presence_of_element_located((By.XPATH, "//section[@data-testid='find-results-section-title']//ul")))
        movie = driver2.find_element(By.XPATH, "//section[@data-testid='find-results-section-title']//ul").find_elements(By.XPATH, ".//li")[0]
        name = movie.find_element(By.XPATH, ".//a").text
        link = movie.find_element(By.XPATH, ".//a").get_attribute("href")
        year = movie.text.strip().split("\n")[1]
        imdb_id = link.split("/")[-2]
        return imdb_id, year

    # Attempt #4
    def try_4(self, driver2, release_year):
        WebDriverWait(driver2, 2).until(EC.presence_of_element_located((By.XPATH, '//table[@class="findList"]')))
        link = driver.find_element(By.XPATH, '//table[@class="findList"]//tr[1]//td[2]//a').get_attribute('href')

        year = driver.find_element(By.XPATH, '//table[@class="findList"]//tr[1]//td[2]').text
        name = driver.find_element(By.XPATH, '//table[@class="findList"]//tr[1]//td[2]//a').text
        imdb_id = link.split("/")[-2]
        return imdb_id, year

    def scrape_franchises(self):

        # Get initial driver via Selenium
        driver = self.get_driver(True)

        # Scrape high-level franchise names and URLs
        driver.get("https://www.the-numbers.com/movies/franchises")

        franchise_names = []
        #for i in range(30):
        for i in range(10):
            time.sleep(0.5)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            franchise_table = soup.find(attrs={"id": "franchise_overview"})

            for row in franchise_table.find_all(name="tr"):
                row_data = []
                for i, cell in enumerate(row.find_all("td")):
                    row_data.append(cell.string)
                    if i==0:
                        row_data.append(cell.b.a["href"])
                franchise_names.append(row_data)

            next_btn = driver.find_element(by="id", value="franchise_overview_next")
            next_btn.click()

        # Create dataframe
        franchise_df = pd.DataFrame(franchise_names, columns = ["Franchise", "URL", "Total_Movies", "2","3","4","5","6","7",])
        franchise_df = franchise_df[["Franchise", "Total_Movies", "URL"]].dropna()

        # Eliminate franchises with less than 2 total movies
        franchise_df['Total_Movies'] = franchise_df['Total_Movies'].astype(int)
        franchise_df = franchise_df[franchise_df['Total_Movies'] >= 2].reset_index(drop = True)

        # Scrape individual franchise data
        movies_data = []
        # Logic for percentage update
        num_iterations = len(franchise_df[["Franchise", "URL"]].values)
        for franchise, url in franchise_df[["Franchise", "URL"]].values:
            movies_url = "https://www.the-numbers.com"+url
            driver.get(movies_url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            movies_table = soup.find(attrs={"id": "franchise_movies_overview"})

            if movies_table:
                for row in movies_table.find_all(name="tr"):
                    row_data = [franchise, ]
                    for i, cell in enumerate(row.find_all("td")):
                        if cell.string and "…" in cell.string:
                            movie_link = cell.a["href"]
                            movie_link = "https://www.the-numbers.com" + movie_link
                            print(movie_link)
                            driver.get(movie_link)
                            soup1 = BeautifulSoup(driver.page_source, 'html.parser')
                            row_data.append(soup1.h1.string.split("(")[0].strip())
                        else:
                            row_data.append(cell.string)

                    if (len(row_data) == 7):
                        if (row_data[1]!= "Averages") or (row_data[1]!= "Totals"):
                            movies_data.append(row_data)


            if (i+1) % 100 == 0 or (i+1) == num_iterations:
                percent_complete = (i+1) * 100 / num_iterations
                print(f"Processed {i+1} out of {num_iterations} franchises ({percent_complete:.2f}%)")

        # Create final dataframe
        movies_df = pd.DataFrame(movies_data, columns=["Franchise", "Date", "Movie_Title", "Production_Budget",
                                               "Opening_Weekend", "Domestic_Box_Office", "Worldwide_Box_Office"
                                              ])
        franchise_final_df = franchise_df.merge(movies_df, left_on="Franchise", right_on="Franchise")

        # Eliminate invalid words from Date column
        invalid = ['Averages', 'Totals', 'Unknown']

        valid_idx = [x for x in franchise_final_df.index if not x in franchise_final_df[franchise_final_df['Date'].isin(invalid)].index]
        franchise_final_df = franchise_final_df.reindex(valid_idx)

        # Add in release year as a column
        franchise_final_df['release_year'] = [x[-4:] for x in franchise_final_df['Date']]

        # Remove titles that are still "untitled"
        idx_valid = franchise_final_df['Movie_Title'].str.contains('Untitled').where(lambda x: x == False).dropna().index
        franchise_final_df = franchise_final_df.reindex(idx_valid).reset_index(drop = True)

        # Save as class variable
        self.franchise_final_df = franchise_final_df


    def scrape_imdb_ids(self):
        # Load driver
        driver = self.get_driver(True)
        driver.get("https://www.imdb.com/?ref_=nv_home")

        results = []
        failed = []

        for idx, row in self.franchise_final_df.iterrows():
            movie = row['Movie_Title']
            release_year = row['release_year']

            self.searching_movie(driver, movie)

            imdb_id = None
            for try_num in range(1, 5):
                try:
                    imdb_id, year = getattr(self, f"try_{try_num}")(driver, release_year)
                    if imdb_id is not None:
                        results.append([idx, movie, release_year, imdb_id, year])
                        break
                except Exception as e:
                    # print(f"Error: try {try_num}")
                    # print(e)
                    pass

            if imdb_id is None:
                failed.append([idx, movie, release_year])

        return results, failed

    def run(self):

        # Scrape franchise information
        print('Scraping Franchises...')
        self.scrape_franchises()

        # Scrape IMDb IDs
        print('Scraping IMDb IDs...')
        self.results, self.failed = self.scrape_imdb_ids()

        # Append the results into the original dataframe
        df_res = pd.DataFrame(self.results, columns = ['index', 'Franchise', 'release_year_original', 'imdb_id', 'release_year_scraped']).set_index('index')

        self.franchise_final_df['imdb_id'] = df_res['imdb_id']
        self.franchise_final_df['release_year_scraped'] = df_res['release_year_scraped']

        # Test to see if release year from our records matches the release year scraped
        df_final = res[['Franchise', 'Movie_Title', 'release_year', 'release_year_scraped', 'imdb_id']].copy()
        df_final['matching'] = [1 if x[2] == x[3] else 0 for x in df_final.values]

        return df_final


if __name__ == '__main__':

    # Instantiate class
    f = franchises()
    df_final = f.run()
    df_final.to_csv('output.csv')
