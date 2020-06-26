from bs4 import BeautifulSoup
import requests

# handle multiple spoilers -- CHECK
# handle nested spoilers -- CHECK, captures them all. -- see post 26 in test thread (psa-use-spoiler-not-hide.3028)
# remove quotations
# remove other noise (e.g. \n\n\n)
# move debug and url stuff to config -- CHECK


def get_number_of_pages(response_text):
    """
    Find the number of pages in navbar
    :param response_text: response text in str format
    :return: total number of pages
    """
    soup = BeautifulSoup(response_text, 'lxml')
    number_of_pages = int(soup.find(class_='pageNavSimple-el').text.replace('\n', '').split(' of ')[-1])
    return number_of_pages


def store_link(html, post_number, debug_mode=False):
    soup = BeautifulSoup(html, 'lxml')

    # Display/store all of the links
    for message in soup.select('.message-content'):
        # first spoiler tagged: message.article.div.find(class_='bbCodeBlock bbCodeBlock--spoiler').div.text
        # raw text: message.article.div
        # all spoiler tags message.article.div.select('.bbCodeBlock--spoiler')

        post_data = dict()
        spoilers = list()

        post_data['raw_message_content'] = message.article.div
        post_data['message_text'] = message.article.div.text

        all_spoiler_tags = message.article.div.select('.bbCodeBlock--spoiler')
        post_data['number_of_spoiler_tags'] = len(all_spoiler_tags)

        if post_data['number_of_spoiler_tags'] > 0:
            for spoiler_tagged in all_spoiler_tags:
                spoilers.append(spoiler_tagged.div.text)

        post_data['spoilers'] = spoilers
        post_data['contains_spoiler_tags'] = post_data['number_of_spoiler_tags'] > 0

        if debug_mode:
            print('ˇ' * 60)
            print(post_data['message_text'])
            print('^' * 60)
            print('#{}'.format(post_number))
            print('contains_spoiler_tags', post_data['contains_spoiler_tags'])
            print('number_of_spoiler_tags', post_data['number_of_spoiler_tags'])
            print('spoilers', post_data['spoilers'])
            print('=' * 60)
            print()

        post_number += 1

    return post_number


def scrape_thread(url_regex, base_url, thread_url, debug_mode):
    page_number = 1
    post_number = 1

    jar = requests.cookies.RequestsCookieJar()
    url = url_regex.format(base_url, thread_url, page_number)

    # Determining the number of pages
    response = requests.get(url, cookies=jar)
    number_of_pages = get_number_of_pages(response.text)

    for page_number in range(1, number_of_pages + 1):
        url = url_regex.format(base_url, thread_url, page_number)
        print('Page {} of {}\n > url: {}'.format(page_number, number_of_pages, url))
        response = requests.get(url, cookies=jar)
        post_number = store_link(response.text, post_number, debug_mode)


def scrape_page(config, debug_mode=False):
    """
    :param config: dict-like project config object
    :return:
    """
    for thread_url in config['thread_urls']:
        scrape_thread(url_regex=config['url_regex'],
                      base_url=config['base_url'],
                      thread_url=thread_url,
                      debug_mode=debug_mode)
