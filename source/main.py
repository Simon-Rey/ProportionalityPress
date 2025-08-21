import argparse
import importlib
import os

from generate import generate_site
from article import dump_article_to_json, load_article_from_json
from rules import compute_rules_for_article
from analysis import add_analysis_to_article
from settings import SOURCES


def sources_to_json() -> None:
    """
    Process all the sources and write the JSON files for the corresponding articles.
    """
    for source in SOURCES:
        in_dir = source["raw_data_dir_path"]
        out_dir = source["article_data_dir_path"]
        processor_str = source["raw_data_processor"]
        module_path, func_name = processor_str.rsplit(".", 1)  # split at last dot
        module = importlib.import_module(module_path)
        processor = getattr(module, func_name)

        # Create out dir if needed
        os.makedirs(out_dir, exist_ok=True)

        for article in processor(in_dir):
            file_path = os.path.join(out_dir, article.slugified_title + ".json")
            dump_article_to_json(article, file_path)


def generate_website_from_json() -> None:
    """
    Read all the JSON files representing articles and generate the website based on that.
    """
    all_articles = []

    for source in SOURCES:
        article_dir = source["article_data_dir_path"]
        for article_json_file in os.listdir(article_dir):
            if article_json_file.endswith(".json"):
                article = load_article_from_json(os.path.join(article_dir, article_json_file))
                all_articles.append(article)

    generate_site(all_articles)


def add_rule_results():
    """
    Read all the JSON files representing articles and add the rule results to them.
    """
    for source in SOURCES:
        article_dir = source["article_data_dir_path"]
        for article_json_file in os.listdir(article_dir):
            if article_json_file.endswith(".json"):
                file_path = os.path.join(article_dir, article_json_file)

                article = load_article_from_json(file_path)
                compute_rules_for_article(article)

                dump_article_to_json(article, file_path)

def add_analysis_measures():
    """
    Read all the JSON files representing articles and add the analysis measure to them.
    """
    for source in SOURCES:
        article_dir = source["article_data_dir_path"]
        for article_json_file in os.listdir(article_dir):
            if article_json_file.endswith(".json"):
                file_path = os.path.join(article_dir, article_json_file)

                article = load_article_from_json(file_path)
                add_analysis_to_article(article)

                dump_article_to_json(article, file_path)


def main():
    """
    Entry point for the processing pipeline. See the parser arguments for usage.
    """
    parser = argparse.ArgumentParser(description="Process raw data to generate the Proportionality Press website.")
    parser.add_argument("--sources-to-json", action="store_true", help="Convert raw data to JSON")
    parser.add_argument("--compute-rules", action="store_true", help="Compute voting rule results")
    parser.add_argument("--add-analysis", action="store_true", help="Add analysis measures")
    parser.add_argument("--generate", action="store_true", help="Generate the website")

    args = parser.parse_args()

    if args.sources_to_json:
        sources_to_json()
    if args.compute_rules:
        add_rule_results()
    if args.add_analysis:
        add_analysis_measures()
    if args.generate:
        generate_website_from_json()


if __name__ == '__main__':
    main()