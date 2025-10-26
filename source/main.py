import argparse
import importlib
import os

from multiprocessing import Pool

from generate import generate_site
from article import dump_article_to_json, load_article_from_json
from rules import compute_rules_for_article
from analysis import add_analysis_to_article
from settings import SOURCES
from source.settings import ALL_APPROVAL_RULES, ALL_TRICHOTOMOUS_RULES, ALL_SELECTION_SIZES


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


# def add_rule_results():
#     """
#     Read all the JSON files representing articles and add the rule results to them.
#     """
#     for source in SOURCES:
#         article_dir = source["article_data_dir_path"]
#         for article_json_file in os.listdir(article_dir):
#             if article_json_file.endswith(".json"):
#                 file_path = os.path.join(article_dir, article_json_file)
#
#                 article = load_article_from_json(file_path)
#                 compute_rules_for_article(article, approval_rules=ALL_APPROVAL_RULES, trichotomous_rules=ALL_TRICHOTOMOUS_RULES, sizes=ALL_SELECTION_SIZES)
#
#                 dump_article_to_json(article, file_path)



def add_rule_results_for_file(file_path: str):
    """
    Worker function: process one JSON file (load, compute rules, dump).
    Returns the file path when done (for logging).
    """
    article = load_article_from_json(file_path)
    compute_rules_for_article(
        article,
        approval_rules=ALL_APPROVAL_RULES,
        trichotomous_rules=ALL_TRICHOTOMOUS_RULES,
        sizes=ALL_SELECTION_SIZES,
    )
    dump_article_to_json(article, file_path)
    return file_path


def add_rule_results(n_processes=None):
    """
    Read all JSON files representing articles (across SOURCES)
    and add the rule results to them in parallel.
    """
    # Collect all JSON files from all sources
    all_json_files = []
    for source in SOURCES:
        article_dir = source["article_data_dir_path"]
        if not os.path.isdir(article_dir):
            print(f"Skipping non-existent directory: {article_dir}")
            continue
        for article_json_file in os.listdir(article_dir):
            if article_json_file.endswith(".json"):
                all_json_files.append(os.path.join(article_dir, article_json_file))

    if not all_json_files:
        print("No JSON files found in any SOURCES.")
        return

    print(f"Found {len(all_json_files)} JSON files. Starting pool...")

    # Run multiprocessing pool
    with Pool(processes=n_processes) as pool:
        for processed_file in pool.imap_unordered(add_rule_results_for_file, all_json_files):
            if processed_file:
                print(f"Processed {os.path.basename(processed_file)}")

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