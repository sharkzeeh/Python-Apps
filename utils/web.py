import os
import requests
import urllib.request
import json
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import asyncio
import re

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome('chromedriver', options=chrome_options)

INSTA_USERNAME = ""
INSTA_PASSWORD = ""

class InstaLoad:

    def __init__(self, url="https://www.instagram.com/sharkzeeh", username=INSTA_USERNAME, password=INSTA_PASSWORD):
        self.url = url
        self.username = self.url.split('/')[-1]
        self.login_username = username
        self.password = password
        self.hs = set()
        self.images, self.vids = [], []

    @staticmethod
    def make_dir(dirname):
        current_path = os.getcwd()
        path = os.path.join(current_path, dirname)
        if not os.path.exists(path) or not os.listdir(path):
            os.makedirs(path)

    @staticmethod
    def save_image_to_file(image, dirname, username, suffix):
        with open(f'{dirname}/{username}_{suffix}.jpg' ,'wb') as fh:
            fh.write(image.content)

    @staticmethod
    def download_images(dirname, links, username):
        length = len(links)
        for index, link in enumerate(links):
            print (f'Downloading {index + 1} of {length} images')
            response = requests.get(link, stream=True)
            InstaLoad.save_image_to_file(response, dirname, username, index)
            del response

    async def scroll(self, driver, timeout):
        scroll_pause_time = timeout

        last_height = driver.execute_script("return document.body.scrollHeight")


        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(scroll_pause_time)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print('scrolled to the bottom of the profile!')
                break
            last_height = new_height
            await self.single_scroll_images()


    async def profile(self):

        driver.get("https://www.instagram.com")
        time.sleep(5)

        usr = driver.find_element_by_name("username")
        pswd = driver.find_element_by_name('password')

        ActionChains(driver)\
            .move_to_element(usr).click()\
            .send_keys(self.login_username)\
            .move_to_element(pswd).click()\
            .send_keys(self.password)\
            .perform()

        login_button = driver.find_element_by_xpath(
            '//form/div/button')

        ActionChains(driver)\
            .move_to_element(login_button)\
            .click().perform()

        time.sleep(5)
        driver.get(self.url)
        await self.scroll(driver, 7)

    
    async def single_scroll_images(self):
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        article = soup.find('article')
        one_scroll_hrefs = [h['href'] for h in article.find_all('a')]
        self.hs.update(one_scroll_hrefs)


    async def get_content_links(self):
        shared_data = re.compile(r'window._sharedData = ({[^\n]*});')
        self.hs = [self.url + h for h in self.hs]
        for h in self.hs:
            contents = urllib.request.urlopen(h)
            html = contents.read().decode("utf-8")
            match = re.search(shared_data, html)
            media = json.loads(match.group(1))['entry_data']['PostPage'][0]['graphql']['shortcode_media']
            if media['__typename'] == "GraphSidecar":
                for slide in media['edge_sidecar_to_children']['edges']:
                    display_url = slide['node']['display_url']
                    self.images.append(display_url)
            elif media['__typename'] == "GraphVideo":
                self.vids.append(media['video_url'])
            else:
                self.images.append(media['display_url'])

    async def downloader(self):
        await self.profile()
        driver.quit()
        await self.get_content_links()
        InstaLoad.make_dir(self.username)
        InstaLoad.download_images(self.username, self.images, self.username)
        print('loaded!')


if __name__ == "__main__":
    asyncio.run(InstaLoad().downloader())
