from bs4 import BeautifulSoup
import requests


class ForumScraper:
    """
    Scrapes text posts/messages from an online forum/message board and stores them into file(s)
    """
    def __init__(self, config, debug_mode=False):
        """

        :param config: specifies the configuration -- behaviour
        """
        self._config = config
        self.url_regex: str = self._config['url_regex']
        self.base_url: str = self._config['base_url']
        self.thread_urls = self._config['thread_urls']
        self._debug_mode = debug_mode

    def _store_link(self, html, post_number, thread_id):
        soup = BeautifulSoup(html, 'lxml')

        # Display/store all of the links
        for post in soup.select('.message-content'):
            # first spoiler tagged: message.article.div.find(class_='bbCodeBlock bbCodeBlock--spoiler').div.text
            # raw text: message.article.div
            # all spoiler tags message.article.div.select('.bbCodeBlock--spoiler')

            post_data = dict()
            spoilers = list()

            post_data['thread_id'] = thread_id

            post_data['post_id'] = post.div['data-lb-id']
            post_data['raw_message_content'] = post.article.div
            post_data['message_text'] = post.article.div.text

            all_spoiler_tags = post.article.div.select('.bbCodeBlock--spoiler')
            post_data['number_of_spoiler_tags'] = len(all_spoiler_tags)

            if post_data['number_of_spoiler_tags'] > 0:
                for spoiler_tagged in all_spoiler_tags:
                    spoilers.append(spoiler_tagged.div.text)

            post_data['spoilers'] = spoilers
            post_data['contains_spoiler_tags'] = post_data['number_of_spoiler_tags'] > 0

            if self._debug_mode:
                # Print post details to stdout
                print('ˇ' * 60)
                print(post_data['message_text'])
                print('^' * 60)
                print('#{}'.format(post_number))
                print('thread_id', post_data['thread_id'])
                print('post_id', post_data['post_id'])
                print('contains_spoiler_tags', post_data['contains_spoiler_tags'])
                print('number_of_spoiler_tags', post_data['number_of_spoiler_tags'])
                print('spoilers', post_data['spoilers'])
                print('=' * 60)
                print()

            post_number += 1

        return post_number

    def _scrape_thread(self, thread_url):
        page_number = 1
        post_number = 1
        thread_id = thread_url.split('.')[-1]

        jar = requests.cookies.RequestsCookieJar()
        url = self.url_regex.format(self.base_url, thread_url, page_number)

        # Determining the number of pages
        response = requests.get(url, cookies=jar)
        number_of_pages = ForumScraper._get_number_of_pages(response.text)

        for page_number in range(1, number_of_pages + 1):
            url = self.url_regex.format(self.base_url, thread_url, page_number)
            print('Page {} of {}\n > url: {}'.format(page_number, number_of_pages, url))
            response = requests.get(url, cookies=jar)
            post_number = self._store_link(response.text, post_number, thread_id)

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
            self._scrape_thread(thread_url=thread_url)
