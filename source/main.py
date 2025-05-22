import os
import shutil

from abc_vote import article_to_abc_profile, compute_rules_for_article
from generate import generate_site
from article import default_config, dump_article_to_json, load_article_from_json
from polis import read_polis_poll, polis_poll_to_article


def all_polis_to_json():
    source_dir_path = os.path.dirname(os.path.realpath(__file__))
    polis_raw_data_dir_path = os.path.join(source_dir_path, 'raw_data', 'polis_data')

    # Create the polis data folder, deleting the current one if exists
    data_dir_path = os.path.join(source_dir_path, 'data', 'polis')
    if os.path.exists(data_dir_path):
        shutil.rmtree(data_dir_path)
    os.makedirs(data_dir_path)

    # Read all the polis data, create corresponding Article object and dump to JSON
    for poll_dir in os.listdir(polis_raw_data_dir_path):
        poll = read_polis_poll(os.path.join(polis_raw_data_dir_path, poll_dir))
        article = polis_poll_to_article(poll)

        # Dump the json in the folder
        file_path = os.path.join(data_dir_path, article.slugified_title + ".json")
        dump_article_to_json(article, file_path)

def generate_all_polis():
    source_dir_path = os.path.dirname(os.path.realpath(__file__))
    polis_data_dir_path = os.path.join(source_dir_path, 'data', 'polis')

    all_articles = []
    for article_file in os.listdir(polis_data_dir_path):
        all_articles.append(load_article_from_json(os.path.join(polis_data_dir_path, article_file)))

    config = default_config()
    generate_site(config, all_articles)

def compute_and_write_all_rules():
    source_dir_path = os.path.dirname(os.path.realpath(__file__))
    polis_data_dir_path = os.path.join(source_dir_path, 'data', 'polis')

    for article_file in os.listdir(polis_data_dir_path):
        article = load_article_from_json(os.path.join(polis_data_dir_path, article_file))
        compute_rules_for_article(article)
        file_path = os.path.join(polis_data_dir_path, article.slugified_title + ".json")
        dump_article_to_json(article, file_path)
        generate_all_polis()

def main():
    # all_polis_to_json()
    # compute_and_write_all_rules()
    generate_all_polis()

    # source_dir_path = os.path.dirname(os.path.realpath(__file__))
    # article = load_article_from_json(os.path.join(source_dir_path, "data", "polis", "canadianelectoralreform.json"))
    # compute_rules_for_article(article)
    # for rule, rule_dict in article.representative_comments.items():
    #     for size, res in rule_dict.items():
    #         print(rule, size, res)

if __name__ == '__main__':
    main()