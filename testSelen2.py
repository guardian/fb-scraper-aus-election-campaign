import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()
options.headless = True
upto = 0

driver = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver', options=options)

driver.get('https://python.org') 
print(driver.title)