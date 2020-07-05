from src.common import constants
import argparse
import yaml
import json


def parse_arguments(function_name):
    parser = argparse.ArgumentParser(description='Raw data scraper for {}'.format(constants.APP_NAME))
    parser.add_argument('config_path', type=str,
                        help='Path of config file for {}'.format(function_name))
    return parser.parse_args()


def load_config(path_to_config):
    """
    Loads the yaml config file.
    :param path_to_config:
    :return:
    """
    config = yaml.safe_load(open(path_to_config))
    return config


def save_thread(filename, data, jsonl=False):
    if not jsonl:
        with open(filename, 'w') as file:
            json.dump(data, file)
    else:
        with open(filename, 'w') as file:
            for entry in data:
                json.dump(entry, file)
                file.write('\n')
