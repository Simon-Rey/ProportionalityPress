from __future__ import annotations


# Rules that are computed. Slow and irrelevant rules are commented out.
ALL_RULES = [
    "av",
    "sav",
    "pav",
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


SITE_NAME = "Proportionality Press"
BASE_URL = "/"
STATIC_URL = "/static/"
OUTPUT_DIR = "_site"
TEMPLATES_DIR = "templates"
STATIC_DIR = "static"


