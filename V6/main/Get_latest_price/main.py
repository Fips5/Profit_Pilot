from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Specify the path to your chromedriver
CHROME_DRIVER_PATH = r'C:\Users\David\Documents\ProfitPilot\V6\R&D\Get_latest_price\chromedriver-win64\chromedriver.exe'


def get_latest_price(web_driver_path):

    # Set up the Service for ChromeDriver
    service = Service(web_driver_path)

    # Set up the Chrome options
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
    options.add_argument("--no-sandbox")  # Bypass OS security model
    options.add_argument("--disable-images")  # Disable images (if applicable)
    options.add_argument("--disable-javascript")  # Disable JavaScript (if not needed)
    options.add_argument("--window-size=1920x1080")  # Set window size

    # Create the WebDriver instance with the service and options
    driver = webdriver.Chrome(service=service, options=options)

    # Navigate to the eToro NVDA market page
    driver.get("https://www.etoro.com/markets/nvda")

    # Use WebDriverWait to wait for the price element to be visible
    price_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "span.instrument-price.et-font-3xl"))
    )  # Closing parenthesis added here

    # Get the text (the price) from the element
    nvda_price = price_element.text

    driver.quit()

    return float(nvda_price)

price = get_latest_price(CHROME_DRIVER_PATH)
print(price)
