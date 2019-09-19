"""
Gets the html of a url using headless chrome
and returns html and download time.
"""

import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_html(url):
    start = time.time()

    # create a new Chrome session
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.implicitly_wait(30)
    driver.get(url)

    # Selenium hands the page source to Beautiful Soup
    html = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    end = time.time()
    get_html_time = round(end - start, 2)

    return html, get_html_time
