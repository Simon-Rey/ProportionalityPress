from collections import defaultdict

from source.article import load_article_from_json, Article, RuleResult


def analyse_satisfaction_vector(article: Article, rule_result: RuleResult):
    sat_vector = defaultdict(int)
    for comment_id in rule_result.committee:
        c = article.get_comment(comment_id)
        for voter_id in c.agreeing_ids:
            sat_vector[voter_id] += 1
    rule_result.satisfaction = sum(sat_vector.values())
    rule_result.coverage = len(sat_vector) / article.num_participants

def analyse_max_satisfaction(article: Article, rule_result: RuleResult):
    max_sat_res = article.rule_results.get("av", dict()).get(rule_result.committee_size)
    if max_sat_res is None or max_sat_res.satisfaction is None:
        raise ValueError("I cannot find the satisfaction of av and thus cannot get the max satisfaction. Ask for "
                         "max satisfaction only after the satisfaction has been computed for all rules and sizes.")
    rule_result.max_satisfaction = max_sat_res.satisfaction

def analyse_max_coverage(article: Article, rule_result: RuleResult):
    max_cov_res = article.rule_results.get("cc", dict()).get(rule_result.committee_size)
    if max_cov_res is None or max_cov_res.coverage is None:
        raise ValueError("I cannot find the coverage of cc and thus cannot get the max coverage. Ask for "
                         "max coverage only after the coverage has been computed for all rules and sizes.")
    rule_result.max_coverage = max_cov_res.coverage

def add_analysis_to_article(article: Article):
    # First pass for satisfaction
    for rule, rule_dict in article.rule_results.items():
        for size, rule_result in rule_dict.items():
            analyse_satisfaction_vector(article, rule_result)
    # Second pass for max satisfaction
    for rule, rule_dict in article.rule_results.items():
        for size, rule_result in rule_dict.items():
            analyse_max_satisfaction(article, rule_result)
            analyse_max_coverage(article, rule_result)
