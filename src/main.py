from src.data.forum_scraper import ForumScraper
from src.common import utils
from src.common import constants

FORUM_NAME = 'resetera'


if __name__ == '__main__':
    print('=== {}:: starting main ==='.format('Recommendation pipeline for {}'.format(constants.APP_NAME)))
    args = utils.parse_arguments(__file__)
    config = utils.load_config(args.config_path)

    fs = ForumScraper(config=config['scraper'][FORUM_NAME],
                      forum_name=FORUM_NAME,
                      debug_mode=config['scraper']['debug_mode'])
    fs.scrape_page()
