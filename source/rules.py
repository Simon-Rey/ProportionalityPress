from collections import defaultdict

from article import Article
from source.article import RuleResult

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

ALL_COMMITTEE_SIZES = [3, 5, 8, 10]

def article_to_abc_profile(article: Article, comment_ids_mapping: list[str]):
    from abcvoting.abcrules import Rule
    from abcvoting.preferences import Profile

    profile = Profile(num_cand=article.num_comments)

    ballots = defaultdict(set)
    for comment in article.comments:
        for agree_id in comment.agreeing_ids:
            ballots[agree_id].add(comment_ids_mapping.index(comment.comment_id))
    profile.add_voters(ballots.values())
    return profile

def compute_rules_for_article(article: Article):
    from abcvoting.abcrules import Rule
    from abcvoting.preferences import Profile

    print(f"Computing rules for article {article.title} with {article.num_participants} participants and {article.num_comments} comments")

    comment_ids_mapping = [c.comment_id for c in article.comments]

    profile = article_to_abc_profile(article, comment_ids_mapping)
    for rule in ALL_RULES:
        for size in ALL_COMMITTEE_SIZES:
            print("\t", rule, size)
            abc_rule = Rule(rule)

            # We skip Gurobi because it's annoying
            index = 0
            while "gurobi" in abc_rule.algorithms[index] and index < len(abc_rule.algorithms) - 1:
                index += 1
            algorithm = abc_rule.algorithms[index]
            if algorithm == "brute-force":
                continue

            # We sort for better comparison, in any cases, this is a set so unordered.
            result = abc_rule.compute(profile, committeesize=size, algorithm=algorithm, resolute=True)[0]
            result_repr = sorted([comment_ids_mapping[c] for c in result], key=lambda x: int(x))
            if rule in article.rule_results:
                article.rule_results[rule][size] = RuleResult(rule, size, result_repr)
            else:
                article.rule_results[rule] = {size: RuleResult(rule, size, result_repr)}
