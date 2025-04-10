from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from settings import settings

def init_driver():
    """Initialize the WebDriver with settings."""
    service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()

    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"user-agent={UserAgent().random}")

    if settings["headless"]:
        chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(settings["window_width"], settings["window_height"])
    return driver