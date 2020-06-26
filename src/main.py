from src.data import scrape_raw_data_utils
from src.common import utils
from src.common import constants


if __name__ == '__main__':
    print('=== {}:: starting main ==='.format('Recommendation pipeline for {}'.format(constants.APP_NAME)))
    args = utils.parse_arguments(__file__)
    config = utils.load_config(args.config_path)

    scrape_raw_data_utils.scrape_page(config=config['scraper']['resetera'],
                                      debug_mode=config['scraper']['debug_mode'])
