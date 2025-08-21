from collections import defaultdict

from abcvoting.preferences import Profile
from abcvoting.abcrules import Rule


from article import Article, RuleResult
from settings import ALL_RULES, ALL_COMMITTEE_SIZES


def article_to_abc_profile(article: Article, comment_ids_mapping: list[str]) -> Profile:
    """
    Convert an Article object into an abcvoting Profile.

    Each participant's ballot is represented as a set of candidate indices
    (candidates correspond to comments, mapped via `comment_ids_mapping`).

    Args:
        article (Article): The article containing participants and comments.
        comment_ids_mapping (list[str]): Ordered list mapping candidate index → comment_id.

    Returns:
        Profile: abcvoting Profile object representing all participant approvals.
    """
    profile = Profile(num_cand=article.num_comments)

    ballots = defaultdict(set)
    for comment in article.comments:
        for agree_id in comment.agreeing_ids:
            ballots[agree_id].add(comment_ids_mapping.index(comment.comment_id))
    profile.add_voters(ballots.values())
    return profile

def compute_rules_for_article(article: Article) -> None:
    """
    Compute committee selections for all rules and committee sizes,
    and store them in the article's `rule_results`.

    Steps:
        1. Build an abcvoting Profile from the Article.
        2. For each rule in ALL_RULES and each size in ALL_COMMITTEE_SIZES:
            - Choose a computation algorithm (skip "gurobi", avoid "brute-force").
            - Run the rule to get a winning committee.
            - Convert candidate indices back into comment_ids.
            - Store results in article.rule_results[rule][size].

    Args:
        article (Article): The article containing comments and participants.

    Notes:
        - Skips "gurobi" algorithms (due to solver dependency).
        - Skips "brute-force" (too slow for realistic data).
    """
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

            # We sort for better comparison, in any case, this is a set so unordered.
            result = abc_rule.compute(profile, committeesize=size, algorithm=algorithm, resolute=True)[0]
            result_repr = sorted([comment_ids_mapping[c] for c in result], key=lambda x: int(x))
            if rule in article.rule_results:
                article.rule_results[rule][size] = RuleResult(rule, size, result_repr)
            else:
                article.rule_results[rule] = {size: RuleResult(rule, size, result_repr)}
