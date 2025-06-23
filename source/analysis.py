from collections import defaultdict

import numpy as np

from source.article import Article, RuleResult

def satisfaction_vector(article, rule_result):
    sat_vector = {p: 0 for p in article.participant_ids}
    for comment_id in rule_result.committee:
        c = article.get_comment(comment_id)
        for voter_id in c.agreeing_ids:
            sat_vector[voter_id] += 1
    return sat_vector

def analyse_satisfaction_vector(article: Article, rule_result: RuleResult):
    sat_vector = satisfaction_vector(article, rule_result)
    # Satisfaction
    rule_result.satisfaction = sum(sat_vector.values())

    # Coverage
    rule_result.coverage = sum(1 for s in sat_vector.values() if s > 0) / len(sat_vector)

    # Sat distribution
    sat_distribution = [0 for _ in range(rule_result.committee_size + 1)]
    for sat in sat_vector.values():
        sat_distribution[sat] += 1

    # Store as {left_edge: count}
    rule_result.sat_distribution = {str(i): sat for i, sat in enumerate(sat_distribution)}

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
