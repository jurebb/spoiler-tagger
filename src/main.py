from src.scraper.forum_scraper import ForumScraper
from src.common import utils
from src.common import constants

FORUM_NAME = 'resetera'


def scrape_resetera():
    fs = ForumScraper(config=config['scraper'][FORUM_NAME],
                      forum_name=FORUM_NAME,
                      debug_mode=config['scraper']['debug_mode'])
    fs.scrape_page()


def upload_to_bigquery():
    # uploading to bigquery
    # TODO automatize, this is only a test
    ForumScraper.upload_to_bigquery(
        json_filename="../data/scraped_data/resetera/thread_red-dead-redemption-ii-spoiler-thread.75874.json",
        project_id="spoiler-tagger-poc",
        dataset_id="spoilertaggerpocdb",
        target_table_id="posts",
        target_table_location="US",
    )


if __name__ == '__main__':
    print('=== {}:: starting main ==='.format('Recommendation pipeline for {}'.format(constants.APP_NAME)))
    args = utils.parse_arguments(__file__)
    config = utils.load_config(args.config_path)

    scrape_resetera()

    upload_to_bigquery()
