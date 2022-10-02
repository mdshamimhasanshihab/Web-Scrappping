from selenium import webdriver
from selenium.webdriver.common.keys import Keys
dri=webdriver.Chrome(executable_path="C:\Driver\chromedriver_win32 (3)\chromedriver.exe")
dri.get("http://newtours.demoaut.com/")
print(dri.title)
print(dri.current_url)
print(dri.page_source)
dri.close()
