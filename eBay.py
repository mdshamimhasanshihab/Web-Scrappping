import requests, os, time, argparse
from bs4 import BeautifulSoup
import urllib.parse as urlparse
from urllib.parse import parse_qs
from datetime import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from tqdm import tqdm
import pandas as pd
# openpyxl, lxml

def get_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15'}
        response = requests.get(url, headers=headers, timeout=10)
    except:
        print('SOMETHING IS WRONG. RETRYING AFTER 20 SECONDS SLEEP', url)
        if url == "https://app.standvirtual.com":
            return
        time.sleep(20)
        return get_page(url)

    if not response.ok:
        print('server responded:', response.status_code, 'retrying after 20 seconds sleep', url)
        if response.status_code == 400:
            return get_page(url.replace(' ', ''))
        elif response.status_code == 404:
            return None
        time.sleep(20)
        return get_page(url)
    else:
        soup = BeautifulSoup(response.text, 'lxml')

    return soup

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--url')
    argv = p.parse_args()
    if argv.url is None:
        print("--url can't be empty")
        exit(2)
    url = argv.url
    # url = "https://www.ebay.com/sch/i.html?_from=R40&_nkw=phantom+of+the+opera+1911&_sacat=0&rt=nc&LH_Sold=1&LH_Complete=1"

    ################
    # g-drive auth
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    #######################
    # generate folder_name
    parsed_url = parsed = urlparse.urlparse(url)
    now = datetime.now()  # current date and time
    date_time = now.strftime("%d-%m-%Y_%H-%M-%S")
    try:
        keyword = parse_qs(parsed.query)["_nkw"][0]
        folder_name = date_time + "___" + parse_qs(parsed.query)["_nkw"][0].replace(" ", "-")
    except:
        keyword = ""
        folder_name = date_time + "___"


    ################
    # parsing
    datas = []
    file_names = []
    prices = []
    end_dates = []
    soup = get_page(url)
    ul = soup.find("ul", class_="srp-results")
    lis = ul.find_all("li", recursive=False)
    for li in tqdm(lis):
        name = li.find("h3", class_="s-item__title").text.strip()
        image_url = li.find("img", class_="s-item__image-img")["src"].replace("l225.jpg", "l500.jpg")
        price = li.find("span", class_="s-item__price").text.strip()
        ended_date = li.find("span", class_="s-item__ended-date").text.strip()
        file_name = image_url.split("/")[-2] + ".jpg"
        datas.append({"image_url": image_url, "price": price, "ended_date": ended_date, "file_name": file_name})
        file_names.append(file_name)
        prices.append(price)
        end_dates.append(ended_date)

    # create folder in g-drive
    folder = drive.CreateFile({'title': folder_name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [{'id': "1p85IFGuvPfki5rLAyIHJ8U_9lpzXBJfT"}]})
    folder.Upload()

    #######################
    # create xlsx
    df = pd.DataFrame({"Price": prices, "Files": file_names, "End date": end_dates})
    df.to_excel("data.xlsx", index=False)

    # upload xlsx
    for i in tqdm(range(1)):
        file = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": folder["id"]}]
                                    , 'title': "data"
                                    , 'mimeType': 'application/vnd.ms-excel'})
        file.SetContentFile('data.xlsx')
        file.Upload({'convert': True})

    # delete xlsx
    time.sleep(10)
    os.remove("data.xlsx")

    #######################
    # download images
    for data in tqdm(datas):
        img_data = requests.get(data["image_url"]).content
        with open(data["file_name"], 'wb') as handler:
            handler.write(img_data)

    #######################
    # upload folder in g-drive
    for data in tqdm(datas):
        file_drive = drive.CreateFile({'title': data["file_name"], 'mimeType': 'image/jpg', 'parents': [{'id': folder['id']}] })
        file_drive.SetContentFile(data["file_name"])
        file_drive.Upload()

    ########################
    # delete local files
    for data in tqdm(datas):
        os.remove(data["file_name"])