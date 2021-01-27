from urllib.request import urlopen
from bs4 import BeautifulSoup
import hashlib
import concurrent.futures
import time
import asyncio
import datetime
import threading
import utils.urls as uu


class UPH:

    def __init__(self, delay=180):
        self.delay = delay
        self.URLS = asyncio.run(uu.URLLOADER().find_urls())
        self.url_times_changed = dict(zip(self.URLS, [[1, None] for i in range(len(self.URLS))]))

    def update_hash(self, text):
        soup = BeautifulSoup(text, 'html.parser')
        h = hashlib.md5()
        h.update(text.encode('utf-8'))
        return h.hexdigest()

    def load_url(self, url, timeout):
        with urlopen(url, timeout=timeout) as conn:
            try:
                read_page = conn.read()
            except TimeoutError:
                print(f'retrieving {url} has timed out ...')
                return
            try:
                decoded = read_page.decode('utf-8')
                return self.update_hash(decoded)
            except UnicodeDecodeError:
                print(f"failed to decode utf-8 text of {url}")
                return self.update_hash(read_page)


    async def runner(self):
        self.time_elapsed_per_run = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.url_times_changed)) as executor:
            async def update_change_data():
                future_to_url = {executor.submit(self.load_url, url, 20): url for url in self.url_times_changed}
                for future in concurrent.futures.as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        data = future.result()
                    except Exception as exc:
                        print(f"{url} generated an exception: {exc}")
                        try:
                            del self.url_times_changed[url]
                        except KeyError:
                            ... #  this url has already been deleted!
                    else:
                        url_content_hash = self.url_times_changed[url][1]
                        if not url_content_hash:
                            self.url_times_changed[url][1] = data
                        elif url_content_hash != data:
                            self.url_times_changed[url][0] += 1

            async def sleeping_bag(delay):
                await asyncio.sleep(self.delay)

            task_1 = asyncio.create_task(
                sleeping_bag(self.delay))
            task_2 = asyncio.create_task(
                update_change_data())

            await task_1
            await task_2


if __name__ == "__main__":
    uph = UPH(180)
    start = datetime.datetime.now()
    print(f"started at: {start.strftime('%Y-%m-%d %H:%M:%S')}\n")
    for i in range(int(60 / (uph.delay / 60))):
        asyncio.run(uph.runner())

    finish = datetime.datetime.now()
    print(f"\nfinished at: {finish.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"time elapsed: {finish - start}")

    # output the resulting uphs
    output = {k: v[0] for k, v in uph.url_times_changed.items()}
    for k, v in sorted(output.items(), key=lambda item: -item[1]):
        print(f"{k}: {v} uph")

