from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
driver=webdriver.Chrome(executable_path="C:\Driver\chromedriver_win32 (3)\chromedriver.exe")
driver.get("http://newtours.demoaut.com/")
print(driver.title)
driver.get("http://demo.automationtesting.in/Windows.html")
time.sleep(5)
print(driver.title)

driver.back()
time.sleep(5)
print(driver.title)

driver.forward()
time.sleep(5)
print(driver.title)
# time.sleep(5)
# # driver.close()
# driver.quit()