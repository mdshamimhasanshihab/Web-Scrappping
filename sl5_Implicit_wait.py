from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
driver=webdriver.Chrome(executable_path="C:/Driver/cc/chromedriver.exe")
driver.get("https://www.facebook.com/")
driver.implicitly_wait(100)

assert "Facebook – log in or sign up" in driver.title
Username_ele=driver.find_element_by_name('email')
Pass_ele=driver.find_element_by_id('pass')
Username_ele.send_keys("01784365872")
Pass_ele.send_keys("balerprem09")
driver.find_element_by_name("login").click()  
# print(driver.title)
# assert "Mercury Tours" in driver.title
