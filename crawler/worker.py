from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
from utils import get_logger, get_urlhash, normalize
from simhash import Simhash, SimhashIndex
import uuid

class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier

        self.simhash_index = SimhashIndex([])
        self.traps = set()
        self.current_subdomain = ''
        self.current_subdomain_time = time.time()
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests from scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break

            resp = download(tbd_url, self.config, self.logger)
            document_size, tokens = scraper.token_info(tbd_url, resp)

            self.frontier.add_page_details(
                    tbd_url,
                    document_size,
                    tokens
            )

            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")

            url = normalize(url)
            subdomain_urlhash = get_urlhash(url)
            if subdomain_urlhash != self.current_subdomain:
                self.current_subdomain = subdomain_urlhash
                self.current_subdomain_time = time.time()
            if (time.time() - self.current_subdomain_time >= 600) or self.simhash_index.get_near_dups(Simhash(tokens)):
                self.traps.add(subdomain_urlhash)
            if subdomain_urlhash not in self.traps:
                scraped_urls = scraper.scraper(tbd_url, resp)
            else:
                scraped_urls = []

            self.simhash_index.add(str(uuid.uuid4), Simhash(tokens))
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
