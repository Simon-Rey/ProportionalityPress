from __future__ import annotations

import os
from enum import Enum
from pathlib import Path

from rules import (AV, SAV, CC, SeqPAV, SeqPhragmen, EqualShares, EqualSharesWithAVCompletion,
                   EqualSharesWithIncrementCompletion,
                   PhragmenEnestroem, TriPAVILPKraiczy2025, TriPAVILPHervounin2025, TriPAVILPTalmonPage2021,
                   TriTaxSeqPhrag, TriSeqPhrag, TriTaxMESKPPS2025, TriMaxSatisfaction, TriChamberlinCourant)

BASE_DIR = Path(__file__).resolve().parent


class BallotModeEnum(Enum):
    APPROVAL_ONLY = 1
    TRICHOTOMOUS_ONLY = 2
    APPROVAL_AND_TRICHOTOMOUS = 3

ALL_APPROVAL_RULES = [
    AV,
    SAV,
    # PAV, -> Skipped because of MIP package issues
    # SLAV,
    CC,
    #LexCC,
    # Geom2,
    SeqPAV,
    # RevSeqPAV,
    # SeqSLAV,
    # SeqCC,
    SeqPhragmen,
    # MinimaxPhragmen,
    # LeximaxPhragmen,
    # MaximinSupport,
    # Monroe,
    # GreedyMonroe,
    # MinimaxAV,
    # LexMinimaxAV,
    EqualShares,
    EqualSharesWithAVCompletion,
    EqualSharesWithIncrementCompletion,
    PhragmenEnestroem,
    # ConsensusRule,
    # Trivial,
    # RSD,
    # EPH
]
ALL_APPROVAL_RULES.sort(key=lambda r: r.ordering_priority)

ALL_TRICHOTOMOUS_RULES = [
    TriPAVILPKraiczy2025,
    TriPAVILPTalmonPage2021,
    TriPAVILPHervounin2025,
    TriSeqPhrag,
    TriTaxSeqPhrag,
    TriTaxMESKPPS2025,
    TriMaxSatisfaction,
    TriChamberlinCourant,
]

ALL_RULES = ALL_TRICHOTOMOUS_RULES + ALL_APPROVAL_RULES

def get_rule_by_id(rule_id):
    for rule in ALL_RULES:
        if rule.short_name == rule_id:
            return rule
    raise ValueError(f"No rule with id {rule_id} has been found in the ALL_RULES list.")

# All committee sizes that are computed
ALL_SELECTION_SIZES = [3, 5, 8, 10]

# General settings for the website generation
BASE_URL = "/"
STATIC_URL = "static/"
OUTPUT_DIR = "_site"
TEMPLATES_DIR = "templates"
INPUT_STATIC_DIR = "static"

# Set the type of ballots to consider, all the rest is automatically adapted.
BALLOT_MODE = BallotModeEnum.APPROVAL_ONLY

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


OUTPUTS = [
    {
        "output_dir_path": os.path.join("_site", "approval"),
        "ballot_mode": BallotModeEnum.APPROVAL_ONLY,
        "highlighted_articles": [
            "newminimumwageinseattle15hour",
            "ernhrungundlandnutzungde",
            "mobilittde",
            "operationmarchingorders",
            "canadianelectoralreform"
        ],
        "default_selection_size": 5,
        "default_popularity_rule": AV,
        "default_representation_rule": EqualSharesWithIncrementCompletion,
        "default_diversity_rule": CC,
        "rule_set": ALL_APPROVAL_RULES,
    },
    {
        "output_dir_path": os.path.join("_site", "trichotomous"),
        "ballot_mode": BallotModeEnum.TRICHOTOMOUS_ONLY,
        "highlighted_articles": [
        ],
        "default_selection_size": 5,
        "default_popularity_rule": TriMaxSatisfaction,
        "default_representation_rule": TriTaxMESKPPS2025,
        "default_diversity_rule": TriChamberlinCourant,
        "rule_set": ALL_TRICHOTOMOUS_RULES,
    },
    {
        "output_dir_path": os.path.join("_site", "all"),
        "ballot_mode": BallotModeEnum.TRICHOTOMOUS_ONLY,
        "highlighted_articles": [
        ],
        "default_selection_size": 5,
        "default_popularity_rule": TriMaxSatisfaction,
        "default_representation_rule": TriTaxMESKPPS2025,
        "default_diversity_rule": TriChamberlinCourant,
        "rule_set": ALL_RULES,
    },
]