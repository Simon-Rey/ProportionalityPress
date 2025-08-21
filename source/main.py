import argparse
import os
import shutil

from generate import generate_site
from article import dump_article_to_json, load_article_from_json
from rules import compute_rules_for_article
from polis import read_polis_poll, polis_poll_to_article, overwrite_default_content
from source.analysis import add_analysis_to_article


def all_polis_to_json():
    """
    Convert all raw Polis CSV directories under `raw_data/polis_data` into JSON Article files.

    Steps:
        - Read all polls from raw_data/polis_data.
        - Convert to Article objects.
        - Save as JSON in data/polis (overwrites old folder).
    """
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
    """
    Load all JSON Articles from data/polis and generate the static site.
    """
    source_dir_path = os.path.dirname(os.path.realpath(__file__))
    polis_data_dir_path = os.path.join(source_dir_path, 'data', 'polis')

    all_articles = []
    for article_file in os.listdir(polis_data_dir_path):
        all_articles.append(load_article_from_json(os.path.join(polis_data_dir_path, article_file)))

    generate_site(all_articles)

def compute_and_write_all_rules():
    """
    For each Article JSON:
        - Compute all rule results.
        - Add analysis data.
        - Save back to JSON.
        - Regenerate site.
    """
    source_dir_path = os.path.dirname(os.path.realpath(__file__))
    polis_data_dir_path = os.path.join(source_dir_path, 'data', 'polis')

    for article_file in os.listdir(polis_data_dir_path):
        article = load_article_from_json(os.path.join(polis_data_dir_path, article_file))
        compute_rules_for_article(article)
        add_analysis_to_article(article)
        file_path = os.path.join(polis_data_dir_path, article.slugified_title + ".json")
        dump_article_to_json(article, file_path)
        generate_all_polis()

def add_analysis_measures():
    """
    Add analysis measures to each Article JSON and regenerate site.
    """
    source_dir_path = os.path.dirname(os.path.realpath(__file__))
    polis_data_dir_path = os.path.join(source_dir_path, 'data', 'polis')

    for article_file in os.listdir(polis_data_dir_path):
        article = load_article_from_json(os.path.join(polis_data_dir_path, article_file))
        add_analysis_to_article(article)
        file_path = os.path.join(polis_data_dir_path, article.slugified_title + ".json")
        dump_article_to_json(article, file_path)
    generate_all_polis()

def overwrite_default_content_all():
    """
    Overwrite default content in each Article JSON and regenerate site.
    """
    source_dir_path = os.path.dirname(os.path.realpath(__file__))
    polis_data_dir_path = os.path.join(source_dir_path, 'data', 'polis')

    for article_file in os.listdir(polis_data_dir_path):
        article = load_article_from_json(os.path.join(polis_data_dir_path, article_file))
        overwrite_default_content(article)
        file_path = os.path.join(polis_data_dir_path, article.slugified_title + ".json")
        dump_article_to_json(article, file_path)
    generate_all_polis()

def main():
    """
    Entry point for the processing pipeline.
    Uncomment the steps you need:
        - all_polis_to_json()
        - compute_and_write_all_rules()
        - add_analysis_measures()
        - overwrite_default_content_all()
        - generate_all_polis()
    """

    parser = argparse.ArgumentParser(description="Process Polis articles pipeline")
    parser.add_argument("--to-json", action="store_true", help="Convert raw Polis polls to JSON")
    parser.add_argument("--compute-rules", action="store_true", help="Compute voting rule results")
    parser.add_argument("--add-analysis", action="store_true", help="Add analysis measures")
    parser.add_argument("--overwrite-content", action="store_true", help="Overwrite default content")
    parser.add_argument("--generate-site", action="store_true", help="Generate the website")

    args = parser.parse_args()

    if args.to_json:
        all_polis_to_json()
    if args.compute_rules:
        compute_and_write_all_rules()
    if args.add_analysis:
        add_analysis_measures()
    if args.overwrite_content:
        overwrite_default_content_all()
    if args.generate_site:
        generate_all_polis()


    # all_polis_to_json()
    # compute_and_write_all_rules()
    # add_analysis_measures()
    overwrite_default_content_all()
    generate_all_polis()

    # source_dir_path = os.path.dirname(os.path.realpath(__file__))
    # article = load_article_from_json(os.path.join(source_dir_path, "data", "polis", "canadianelectoralreform.json"))
    # compute_rules_for_article(article)
    # for rule, rule_dict in article.representative_comments.items():
    #     for size, res in rule_dict.items():
    #         print(rule, size, res)

if __name__ == '__main__':
    main()