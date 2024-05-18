from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from docx import Document
import time


def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = ' '.join([p.get_text() for p in soup.find_all('p')])
    return text


def get_text_from_google(query, num_links=3):
    content_list = {}
    driver = webdriver.Chrome()
    driver.get("https://www.google.com/")
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(query)
    search_box.submit()

    time.sleep(2)  # Waiting for search results to load

    links = driver.find_elements(By.XPATH, "//div[@class='yuRUbf']//a")

    for i, link in enumerate(links):
        if i >= num_links:
            break
        link_url = link.get_attribute('href')
        driver.execute_script("window.open('{}', '_blank');".format(link_url))
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(2)
        link_text = extract_text_from_html(driver.page_source)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        content_list[f'link_{i}'] = link_text

    driver.quit()
    return content_list
