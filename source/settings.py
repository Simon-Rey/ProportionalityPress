from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


# Rules that are computed. Slow and irrelevant rules are commented out.
ALL_RULES = [
    "av",
    "sav",
    # "pav",  -> Skipped because of MIP package problems
    # "slav",
    "cc",
    # "lexcc",
    # "geom2",
    "seqpav",
    # "revseqpav",
    # "seqslav",
    # "seqcc",
    "seqphragmen",
    # "minimaxphragmen",
    # "leximaxphragmen",
    # "maximin-support",
    # "monroe",
    # "greedy-monroe",
    # "minimaxav",
    # "lexminimaxav",
    "equal-shares",
    "equal-shares-with-av-completion",
    "equal-shares-with-increment-completion",
    "phragmen-enestroem",
    # "consensus-rule",
    # "trivial",
    # "rsd",
    # "eph",
]

# All committee sizes that are computed
ALL_COMMITTEE_SIZES = [3, 5, 8, 10]


# Beautified names for the rules
RULE_NAME_MAPPING = {
    "av": "Approval Voting",
    "sav": "Satisfaction Approval Voting",
    "pav": "Proportional Approval Voting",
    "cc": "Chamberlin–Courant",
    "seqpav": "Sequential Proportional Approval Voting",
    "seqphragmen": "Phragmén's Sequential Rule",
    "equal-shares": "Method of Equal Shares",
    "equal-shares-with-av-completion": "Method of Equal Shares with Approval Voting Completion",
    "equal-shares-with-increment-completion": "Method of Equal Shares with Increment Completion",
    "phragmen-enestroem": "Eneström–Phragmén",
    "consensus-rule": "Consensus Rule",
}

# General settings for the website generation
SITE_NAME = "Proportionality Press"
BASE_URL = "/"
STATIC_URL = "static/"
OUTPUT_DIR = "_site"
TEMPLATES_DIR = "templates"
STATIC_DIR = "static"

# Sources described in here are automatically fetched to generate the website.
# Each source is a dictionary indicating:
#   - 'raw_data_dir_path': the input directory, containing all the raw data files
#   - 'article_data_dir_path': the output directory where the JSON of the articles will be written
#   - 'raw_data_processor': the function to process the raw data. Takes a directory path as input and returns a list of Article objects
SOURCES = [
    {
        "raw_data_dir_path": BASE_DIR / 'raw_data' / 'polis_data',
        "article_data_dir_path": BASE_DIR / 'data' / 'polis',
        "raw_data_processor": "polis.read_polis_dir_as_articles",
    }
]
