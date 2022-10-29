import os
import shelve

from threading import Thread, RLock
from queue import Queue, Empty
from glob import glob

from utils import get_logger, get_urlhash, normalize
from scraper import is_valid, is_subdomain

class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.to_be_downloaded = list()

        state_files = [
            self.config.save_file,
            self.config.tokens_file,
            self.config.word_count_file,
            self.config.subdomains_file,
        ]

        state_files = [f + '*' for f in state_files]

        state_files_exist = [len(glob(f)) > 0 for f in state_files]

        self.logger.info(
            f"TESTING: \n\t{state_files}\n\t{state_files_exist}"
        )

        if not any(state_files_exist) and not restart:
            # State file does not exist, but request to load save.
            self.logger.info(
                f"Did not find any save state files, starting from seed."
            )
        elif any(state_files_exist) and restart:
            # State file does exists, but request to start from seed.
            for state_file in state_files:
                for i, f in enumerate(glob(state_file)):
                    self.logger.info(f"DELETING {f}")
                    if i == 0:
                        self.logger.info(
                            f"Found save state file {state_file}, deleting it."
                        )
                    os.remove(f)
                # if not os.path.exists(state_file):
                #     continue
                # self.logger.info(
                #     f"Found save state file {state_file}, deleting it."
                # )
                # os.remove(state_file)

        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.save_file)
        self.tokens = shelve.open(self.config.tokens_file)
        self.word_count = shelve.open(self.config.word_count_file)
        self.subdomains = shelve.open(self.config.subdomains_file)

        if restart:
            for url in self.config.seed_urls:
                self.add_url(url)
        else:
            # Set the frontier state with contents of save file.
            self._parse_save_file()
            if not self.save:
                for url in self.config.seed_urls:
                    self.add_url(url)

    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        total_count = len(self.save)
        tbd_count = 0
        for url, completed in self.save.values():
            if not completed and is_valid(url):
                self.to_be_downloaded.append(url)
                tbd_count += 1
        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} "
            f"total urls discovered.")

    def get_tbd_url(self):
        try:
            return self.to_be_downloaded.pop()
        except IndexError:
            return None

    def add_url(self, url):
        url = normalize(url)
        urlhash = get_urlhash(url)
        if urlhash not in self.save:
            self.save[urlhash] = (url, False)
            self.save.sync()
            self.to_be_downloaded.append(url)

    def add_page_details(self, url, word_count, tokens):
        url = normalize(url)
        urlhash = get_urlhash(url)

        # Question 2 Aid
        if urlhash not in self.word_count:
            self.word_count[urlhash] = (url, word_count)
            self.word_count.sync()

        # Question 3 Aid
        for token in tokens:
            if token not in self.tokens:
                self.tokens[token] = 0
                self.tokens.sync()
            self.tokens[token] += 1
            self.tokens.sync()
        
        # Question 4 Aid
        if not is_subdomain(url):
            return

        if urlhash not in self.subdomains:
            self.subdomains[urlhash] = (url, 1)
        else:
            _, prev_count = self.subdomains[urlhash]
            self.subdomains[urlhash] = (url, prev_count + 1)
        self.subdomains.sync()
    
    def mark_url_complete(self, url):
        urlhash = get_urlhash(url)
        if urlhash not in self.save:
            # This should not happen.
            self.logger.error(
                f"Completed url {url}, but have not seen it before.")

        self.save[urlhash] = (url, True)
        self.save.sync()
