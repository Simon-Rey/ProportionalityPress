from source.article import Article, RuleResult

def satisfaction_vector(article: Article, rule_result: RuleResult) -> dict[str, int]:
    """
    Compute a participant-level satisfaction vector for a given rule result.

    Each participant starts with satisfaction = 0.
    For each comment in the committee, satisfaction increases by 1 for
    every participant who agreed with that comment.

    Args:
        article (Article): The article containing participants and comments.
        rule_result (RuleResult): The rule result with a committee of comments.

    Returns:
        dict[str, int]: Mapping from participant_id → satisfaction score.
    """
    sat_vector = {p: 0 for p in article.participant_ids}
    for comment_id in rule_result.committee:
        c = article.get_comment(comment_id)
        for voter_id in c.agreeing_ids:
            sat_vector[voter_id] += 1
    return sat_vector

def analyse_satisfaction_vector(article: Article, rule_result: RuleResult) -> None:
    """
    Analyse satisfaction metrics for a given rule result and update the rule_result it in place.

    Sets:
        - `satisfaction`: Total satisfaction across all participants.
        - `coverage`: Fraction of participants with satisfaction > 0.
        - `sat_distribution`: Distribution of satisfaction scores, stored as {score: count}.

    Args:
        article (Article): The article containing participants and comments.
        rule_result (RuleResult): The rule result to update.
    """
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

def analyse_max_satisfaction(article: Article, rule_result: RuleResult) -> None:
    """
    Set the maximum satisfaction achievable for this committee size in the rule_result.

    Looks up the "av" rule (approval voting) as the benchmark for max satisfaction.

    Args:
       article (Article): The article containing rule results.
       rule_result (RuleResult): The rule result to update.

    Raises:
       ValueError: If the "av" rule result is missing or not analysed yet.
    """
    max_sat_res = article.rule_results.get("av", dict()).get(rule_result.committee_size)
    if max_sat_res is None or max_sat_res.satisfaction is None:
        raise ValueError("I cannot find the satisfaction of av and thus cannot get the max satisfaction. Ask for "
                         "max satisfaction only after the satisfaction has been computed for all rules and sizes.")
    rule_result.max_satisfaction = max_sat_res.satisfaction

def analyse_max_coverage(article: Article, rule_result: RuleResult) -> None:
    """
        Set the maximum coverage achievable for this committee size in the rule_result.

        Looks up the "cc" rule (Chamberlin–Courant) as the benchmark for max coverage.

        Args:
            article (Article): The article containing rule results.
            rule_result (RuleResult): The rule result to update.

        Raises:
            ValueError: If the "cc" rule result is missing or not analysed yet.
        """
    max_cov_res = article.rule_results.get("cc", dict()).get(rule_result.committee_size)
    if max_cov_res is None or max_cov_res.coverage is None:
        raise ValueError("I cannot find the coverage of cc and thus cannot get the max coverage. Ask for "
                         "max coverage only after the coverage has been computed for all rules and sizes.")
    rule_result.max_coverage = max_cov_res.coverage

def add_analysis_to_article(article: Article) -> None:
    """
    Enrich all rule results in an article with satisfaction/coverage analysis.

    Steps:
        1. Compute satisfaction, coverage, and distribution for each rule result.
        2. Compute maximum satisfaction (from 'av') and maximum coverage (from 'cc')
           for each committee size.

    Args:
        article (Article): The article to update.
    """
    # First pass for satisfaction
    for rule, rule_dict in article.rule_results.items():
        for size, rule_result in rule_dict.items():
            analyse_satisfaction_vector(article, rule_result)
    # Second pass for max satisfaction and max coverage
    for rule, rule_dict in article.rule_results.items():
        for size, rule_result in rule_dict.items():
            analyse_max_satisfaction(article, rule_result)
            analyse_max_coverage(article, rule_result)
