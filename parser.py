import random
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Create a new instance of the WebDriver
driver = webdriver.Chrome('chromedrive.exe')
result_task_name_list = []
# Navigate to the URL
url = 'https://my.365done.ru/happiness'
driver.get(url)
for i in range(100):
    # Find and click the button
    button_xpath = '//*[@id="root"]/div/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/button'
    button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, button_xpath)))
    button.click()

    # Wait for the new page to load
    wait = WebDriverWait(driver, 5)
    page_content = driver.page_source

    soup = BeautifulSoup(page_content, "html.parser")
    # Perform further extraction or processing here
    lst = str(soup.find_all("div", {"class": "suggestions-picker"}))[33:-7]
    lst = lst.split('<a class="suggestions-picker__item" title="нажми, чтобы добавить в свой список">')[1:]
    result_task_name_list.extend([x[:-4] for x in lst])


driver.quit()
print(result_task_name_list)