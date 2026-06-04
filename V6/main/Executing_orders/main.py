# pip install selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# webdriver download link: https://sites.google.com/chromium.org/driver/
# current driver link: https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.70/win64/chromedriver-win64.zip

# Starting a debugging Chrome session, in cmd:
'''
cd C:\Program Files\Google\Chrome\Application
chrome.exe --remote-debugging-port=9238 --user-data-dir="C:\chrome-session"
'''

chrome_driver_path = r'C:\Users\David\Documents\ProfitPilot\V6\R&D\Executing_orders\chromedriver-win64\chromedriver.exe'
service = Service(executable_path=chrome_driver_path)

# Correct option setup for remote debugging
opt = Options()
opt.add_experimental_option('debuggerAddress', 'localhost:9238')  # Correct spelling here

# Initialize Chrome WebDriver with service and options
driver = webdriver.Chrome(service=service, options=opt)

# Interact with the browser
driver.get('https://google.com')

input_element = driver.find_element(By.CLASS_NAME, "gLFyf")
time.sleep(3)
input_element.send_keys("Yahoo Finance" + Keys.ENTER)
time.sleep(10)

driver.quit()
