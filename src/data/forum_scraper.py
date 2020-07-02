from src.common import utils
from src.common import constants
from bs4 import BeautifulSoup
import requests
import datetime
import os
import time


class ForumScraper:
    """
    Scrapes text posts/messages from an online forum/message board and stores them into file(s)
    """
    def __init__(self, config, forum_name, debug_mode=False, sleep_time=1):
        """

        :param config: specifies the configuration -- behaviour
        """
        self._config = config
        self.url_regex: str = self._config['url_regex']
        self.base_url: str = self._config['base_url']
        self.thread_urls = self._config['thread_urls']
        self._debug_mode = debug_mode
        self._sleep_time = sleep_time

        self._post_number = None

        self._directory = os.path.join(constants.SCRAPED_DATA_DIR, forum_name)
        if not os.path.exists(self._directory):
            os.makedirs(self._directory)

    def _scrape_page(self, html, thread_id):
        soup = BeautifulSoup(html, 'lxml')

        all_posts_data = list()

        # Display/store all of the links
        for post in soup.select('.message-content'):
            # first spoiler tagged: message.article.div.find(class_='bbCodeBlock bbCodeBlock--spoiler').div.text
            # raw text: message.article.div
            # all spoiler tags message.article.div.select('.bbCodeBlock--spoiler')

            post_data = dict()
            spoilers = list()

            post_data['thread_id'] = thread_id

            if post.select('div')[0]['class'][1] == 'messageNotice--warning':
                # user banned message warning:
                post_data['post_id'] = post.select('div')[1]['data-lb-id']
            else:
                post_data['post_id'] = post.div['data-lb-id']
            post_data['raw_message_content'] = str(post.article.div)
            post_data['message_text'] = post.article.div.text

            all_spoiler_tags = post.article.div.select('.bbCodeBlock--spoiler')
            post_data['number_of_spoiler_tags'] = len(all_spoiler_tags)

            if post_data['number_of_spoiler_tags'] > 0:
                for spoiler_tagged in all_spoiler_tags:
                    spoilers.append(spoiler_tagged.div.text)

            post_data['spoilers'] = spoilers
            post_data['contains_spoiler_tags'] = post_data['number_of_spoiler_tags'] > 0
            post_data['post_number'] = self._post_number

            if self._debug_mode:
                # Print post details to stdout
                print('ˇ' * 60)
                print(post_data['message_text'])
                print('^' * 60)
                print('#{}'.format(self._post_number))
                print('thread_id', post_data['thread_id'])
                print('post_id', post_data['post_id'])
                print('contains_spoiler_tags', post_data['contains_spoiler_tags'])
                print('number_of_spoiler_tags', post_data['number_of_spoiler_tags'])
                print('spoilers', post_data['spoilers'])
                print('=' * 60)
                print()

            self._post_number += 1
            all_posts_data.append(post_data)

        return all_posts_data

    def _scrape_thread(self, thread_url):
        thread_data = list()
        page_number = 1
        self._post_number = 1
        thread_id = thread_url.split('.')[-1]

        jar = requests.cookies.RequestsCookieJar()
        url = self.url_regex.format(self.base_url, thread_url, page_number)

        # Determining the number of pages
        response = requests.get(url, cookies=jar, timeout=10)
        number_of_pages = ForumScraper._get_number_of_pages(response.text)

        for page_number in range(1, number_of_pages + 1):
            url = self.url_regex.format(self.base_url, thread_url, page_number)
            print('Page {} of {}\n > url: {}'.format(page_number, number_of_pages, url))
            response = requests.get(url, cookies=jar)
            thread_data.extend(self._scrape_page(response.text,  thread_id))
            time.sleep(self._sleep_time)

        return thread_data, thread_id

    @staticmethod
    def _get_number_of_pages(response_text):
        """
        Find the number of pages in navbar
        :param response_text: response text in str format
        :return: total number of pages
        """
        soup = BeautifulSoup(response_text, 'lxml')
        number_of_pages = int(soup.find(class_='pageNavSimple-el').text.replace('\n', '').split(' of ')[-1])
        return number_of_pages

    def scrape_page(self):
        """
        :return:
        """
        for thread_url in self.thread_urls:
            thread_data, thread_id = self._scrape_thread(thread_url=thread_url)
            date_time_stamp = datetime.datetime.now().strftime("%d-%b-%Y-%H-%M-%S-%f")
            data_for_file = {
                'thread_id': thread_id,
                'thread_url': thread_url,
                'thread_data': thread_data,
                'scraped_datetime': date_time_stamp,
            }

            file_path = os.path.join(self._directory, "thread_{}.json".format(thread_url))
            utils.save_thread(file_path, data_for_file)
