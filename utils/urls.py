from selenium import webdriver
import time
from bs4 import BeautifulSoup


class URLLOADER:

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36")
        self.driver = webdriver.Chrome('chromedriver', options=chrome_options)

    async def find_urls(self, retrieve_urls_from="https://blog.feedspot.com/usa_news_websites/"):
        self.driver.get(retrieve_urls_from)
        time.sleep(2)
        await self.scroll(3)
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        urls = [u['href'] for u in soup.find_all('a', {'class': "ext"})]
        self.driver.quit()
        return urls

    async def scroll(self, timeout):
        scroll_pause_time = timeout
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print('scrolled to the very bottom!')
                break
            last_height = new_height