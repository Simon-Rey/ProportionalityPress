import os
import shutil

from generate import generate_site
from article import default_config, dump_article_to_json, load_article_from_json
from rules import compute_rules_for_article
from polis import read_polis_poll, polis_poll_to_article, overwrite_default_content
from source.analysis import add_analysis_to_article



if __name__ == "__main__":

    source_dir_path = os.path.dirname(os.path.realpath(__file__))
    polis_data_dir_path = os.path.join(source_dir_path, 'data', 'polis')

    for article_file in os.listdir(polis_data_dir_path):
        article = load_article_from_json(os.path.join(polis_data_dir_path, article_file))
        overwrite_default_content(article)
        file_path = os.path.join(polis_data_dir_path, article.slugified_title + ".json")
        dump_article_to_json(article, file_path)