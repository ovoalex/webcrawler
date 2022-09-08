import urllib.robotparser
# from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
from link import LinkFinder
from domain import *
from general import *
from langdetect import detect
import hashlib
import os


class Spider:
    project_name = ''
    base_url = ''
    domain_name = ''
    queue_file = ''
    crawled_file = ''
    queue = set()
    crawled = set()
    robots = urllib.robotparser.RobotFileParser()
    lang = ''

    def __init__(self, project_name, base_url, domain_name, language):
        Spider.project_name = project_name
        Spider.base_url = base_url
        self.robots.set_url(base_url + 'robots.txt')
        self.robots.read()
        Spider.lang = language.lower()
        Spider.domain_name = domain_name
        Spider.queue_file = Spider.project_name + '/queue.txt'
        Spider.crawled_file = Spider.project_name + '/crawled.txt'
        self.boot()
        self.crawl_page('First spider', Spider.base_url)

    # Creates directory and files for project on first run and starts the spider
    @staticmethod
    def boot():
        create_project_dir(Spider.project_name)
        create_data_files(Spider.project_name, Spider.domain_name, Spider.base_url)
        Spider.queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)

    # Updates user display, fills queue and updates files
    @staticmethod
    def crawl_page(thread_name, page_url):
        if Spider.robots.can_fetch("*", page_url):
            if page_url not in Spider.crawled:
                print(thread_name + ' now crawling ' + page_url)
                print('Queue ' + str(len(Spider.queue)) + ' | Crawled  ' + str(len(Spider.crawled)))
                links = Spider.gather_links(page_url)
                # if the page is in the desired language
                if -1 not in links:  # error code: {-1}
                    Spider.add_links_to_queue(links)
                    Spider.queue.remove(page_url)
                    Spider.crawled.add(page_url)
                    Spider.update_files()
                    # generates report
                    num_out_links = len(links)
                    append_to_file(os.path.join(Spider.project_name, Spider.domain_name, 'report.csv'),
                                   page_url + ', ' + str(num_out_links))
                else:
                    Spider.queue.remove(page_url)
                    Spider.update_files()
        else:
            print('Page Disallowed: ' + page_url)
            Spider.queue.remove(page_url)
            Spider.crawled.add(page_url)
            Spider.update_files()

    # Converts raw response data into readable information and checks for proper html formatting
    @staticmethod
    def gather_links(page_url):
        html_string = ''
        try:
            response = requests.get(page_url)
            if 'text/html' in response.headers.get('Content-Type'):
                html_string = response.text
                if len(html_string) > 0:
                    soup = BeautifulSoup(html_string, 'html.parser')
                    # set the desired language to the language of the first page
                    if len(Spider.lang) == 0:
                        Spider.lang = detect(soup.body.get_text())
                        print('The desired language is now set to ' + Spider.lang.upper())
                    else:
                        # check if the page is in the desired language
                        if detect(soup.body.get_text()) != Spider.lang:
                            print('Page ' + page_url + ' is not in the desired language ' + Spider.lang.upper())
                            return {-1}  # error code: {-1}
                        else:
                            Spider.save_page(page_url, html_string)
            finder = LinkFinder(Spider.base_url, page_url)
            finder.feed(html_string)
        except Exception as e:
            print(str(e))
            return set()
        return finder.page_links()

    # Saves queue data to project files
    @staticmethod
    def add_links_to_queue(links):
        if -1 not in links:  # error code: {-1}
            for url in links:
                if (url in Spider.queue) or (url in Spider.crawled):
                    continue
                if Spider.domain_name != get_domain_name(url):
                    continue
                Spider.queue.add(url)

    @staticmethod
    def update_files():
        set_to_file(Spider.queue, Spider.queue_file)
        set_to_file(Spider.crawled, Spider.crawled_file)

    @staticmethod
    def save_page(page_url, html_string):
        file_name = hashlib.md5(page_url.encode()).hexdigest().upper() + '.html'
        file_path = os.path.join(Spider.project_name, Spider.domain_name, file_name)
        if not os.path.isfile(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            write_file(file_path, html_string)
        else:
            print('File ' + file_name + ' already exists!')
