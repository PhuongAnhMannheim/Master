url = "https://thereviewmonk.com/?s=a"
from selenium import webdriver
from bs4 import BeautifulSoup
driver = webdriver.Chrome()
driver.get(url)
button = driver.find_element_by_id('more-movies').click()
html_source = driver.page_source
print(html_source)

# soup = BeautifulSoup(html_source, 'html.parser')
# soup.find