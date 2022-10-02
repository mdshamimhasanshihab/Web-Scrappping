from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
driver=webdriver.Chrome(executable_path="C:\Driver\chromedriver_win32 (3)\chromedriver.exe")
driver.get("https://www.facebook.com/?stype=lo&jlou=AfckJsG4KXkYnZhahizcGnfbaTPd1DjpNB_9rr_KkrEJA_kv0cO9cIE8ijqqgnahWORiI7g-_r2EVp_OschOk5rZfqnoruGeBbk_zDd6EywTJA&smuh=34084&lh=Ac8WPlOHevyDbJNFZ1Q")
Username_ele=driver.find_element_by_name('email')
print(Username_ele.is_displayed())
print(Username_ele.is_enabled())
Pass_ele=driver.find_element_by_id('pass')
print(Pass_ele.is_displayed())
print(Pass_ele.is_enabled())
Username_ele.send_keys("01784365872")
Pass_ele.send_keys("dhbkfjhk")
driver.find_element_by_name("login").click()