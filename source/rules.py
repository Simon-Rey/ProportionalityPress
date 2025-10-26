from __future__ import annotations

import warnings
from collections import defaultdict
from collections.abc import Iterable

from abcvoting.preferences import Profile
from abcvoting.abcrules import Rule as ABCVoting_Rule

from trivoting.election import TrichotomousProfile, TrichotomousBallot, Alternative, Selection
from trivoting.rules import thiele_method, PAVILPKraiczy2025, PAVILPHervouin2025, PAVILPTalmonPage2021, TaxKraiczy2025, \
    tax_method_of_equal_shares, sequential_phragmen, tax_sequential_phragmen

from article import Article, RuleResult

class Rule:
    short_name = ""
    long_name = ""
    ordering_priority = 10000  # The lower the better
    approval_explanation = ""

    @classmethod
    def compute_with_abc_voting(cls, profile, size, comment_ids_mapping) -> RuleResult | None:
        abc_rule = ABCVoting_Rule(cls.short_name)

        # We skip Gurobi because it's annoying
        index = 0
        while ("gurobi" in abc_rule.algorithms[index] or "highs" in abc_rule.algorithms[index]) and index < len(abc_rule.algorithms) - 1:
            index += 1
        algorithm = abc_rule.algorithms[index]
        if algorithm == "brute-force":
            warnings.warn(f"For {cls.short_name} I could not find a suitable solver.")
            return None

        # We sort for better comparison, in any case, this is a set so unordered.
        result = abc_rule.compute(profile, committeesize=size, algorithm=algorithm, resolute=True)[0]
        result_repr = sorted([comment_ids_mapping[c] for c in result], key=lambda x: int(x))
        return RuleResult(cls, size, result_repr)

    @classmethod
    def _trivoting_wrapper(cls, profile, size) -> Selection:
        pass

    @classmethod
    def compute_with_trivoting(cls, profile, size, comment_ids_mapping) -> RuleResult | None:
        trivoting_selection = cls._trivoting_wrapper(profile, size)
        selection_repr = sorted([comment_ids_mapping.index(a.name) for a in trivoting_selection.selected], key=lambda x: int(x))
        return RuleResult(cls, size, selection_repr)

class AV(Rule):
    short_name = "av"
    long_name = "Approval Voting"
    ordering_priority = 0
    approval_explanation = "Selects the comments who have the highest number of votes."

class SAV(Rule):
    short_name = "sav"
    long_name = "Satisfaction Approval Voting"
    ordering_priority = 1
    approval_explanation = "Selects a set of comments that maximises the total average satisfaction of the participants. The average satisfaction of a participant is defined here as their satisfaction divided by number of supported comments."

class PAV(Rule):
    short_name = "pav"
    long_name = "Proportional Approval Voting"

class SLAV(Rule):
    short_name = "slav"
    long_name = ""

class CC(Rule):
    short_name = "cc"
    long_name = "Chamberlin–Courant"
    ordering_priority = 8
    approval_explanation = "A participant is considered to be represented if their satisfaction is more than 0. This method selects comments to maximize the number of represented participants."

class LexCC(Rule):
    short_name = "lexcc"
    long_name = ""

class Geom2(Rule):
    short_name = "geom2"
    long_name = ""

class SeqPAV(Rule):
    short_name = "seqpav"
    long_name = "Sequential Proportional Approval Voting"
    ordering_priority = 2
    approval_explanation = "Sequential variant the proportional approval voting method. Selects the comments one by one, each time selecting the best non-selected comment according to the principles of proportional approval voting."

class RevSeqPAV(Rule):
    short_name = "revseqpav"
    long_name = ""

class SeqSLAV(Rule):
    short_name = "seqslav"
    long_name = ""

class SeqCC(Rule):
    short_name = "seqcc"
    long_name = ""

class SeqPhragmen(Rule):
    short_name = "seqphragmen"
    long_name = "Phragmén's Sequential Rule"
    ordering_priority = 7
    approval_explanation = "Sequentially adds comments while balancing the representation load to maintain proportional fairness."

class MinimaxPhragmen(Rule):
    short_name = "minimaxphragmen"
    long_name = ""

class LeximaxPhragmen(Rule):
    short_name = "leximaxphragmen"
    long_name = ""

class MaximinSupport(Rule):
    short_name = "maximin-support"
    long_name = ""

class Monroe(Rule):
    short_name = "monroe"
    long_name = ""

class GreedyMonroe(Rule):
    short_name = "greedy-monroe"
    long_name = ""

class MinimaxAV(Rule):
    short_name = "minimaxav"
    long_name = ""

class LexMinimaxAV(Rule):
    short_name = "lexminimaxav"
    long_name = ""

class EqualShares(Rule):
    short_name = "equal-shares"
    long_name = "Method of Equal Shares"
    ordering_priority = 3
    approval_explanation = "Each participant receives an equal amount of virtual currency to spend on comments they feel positively about. Comments are considered in rounds. A comment is selected if its supporters have enough budget left to collectively afford it."

class EqualSharesWithAVCompletion(Rule):
    short_name = "equal-shares-with-av-completion"
    long_name = "Method of Equal Shares with Approval Voting Completion"
    ordering_priority = 4
    approval_explanation = "Applies the method of equal shares. If fewer than the desired number of comments are selected, the result is completed by using the approval voting selection method."

class EqualSharesWithIncrementCompletion(Rule):
    short_name = "equal-shares-with-increment-completion"
    long_name = "Method of Equal Shares with Increment Completion"
    ordering_priority = 5
    approval_explanation = "Calculates the minimum amount of virtual currency needed for the method of equal shares to select the desired number of comments. Then, applies the method using that amount."

class PhragmenEnestroem(Rule):
    short_name = "phragmen-enestroem"
    long_name = "Eneström–Phragmén"
    ordering_priority = 6
    approval_explanation = "Distributes representation load evenly among participants to select a proportionally representative set of comments."

class ConsensusRule(Rule):
    short_name = "consensus-rule"
    long_name = "Consensus Rule"

class Trivial(Rule):
    short_name = "trivial"
    long_name = ""

class RSD(Rule):
    short_name = "rsd"
    long_name = ""

class EPH(Rule):
    short_name = "eph"
    long_name = ""




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

def article_to_trivoting_profile(article: Article, comment_ids_mapping: list[str]) -> TrichotomousProfile:
    """
    Convert an Article object into an trivoting TrichotomousProfile.

    Each participant's ballot is represented as a set of candidate indices
    (candidates correspond to comments, mapped via `comment_ids_mapping`).

    Args:
        article (Article): The article containing participants and comments.
        comment_ids_mapping (list[str]): Ordered list mapping candidate index → comment_id.

    Returns:
        Profile: abcvoting Profile object representing all participant approvals.
    """
    alternatives = [Alternative(c) for c in comment_ids_mapping]
    profile = TrichotomousProfile(alternatives=alternatives)

    ballots = defaultdict(TrichotomousBallot)
    for comment in article.comments:
        for agree_id in comment.agreeing_ids:
            ballots[agree_id].add_approved(alternatives[comment_ids_mapping.index(comment.comment_id)])
        for disagree_id in comment.disagreeing_ids:
            ballots[disagree_id].add_approved(alternatives[comment_ids_mapping.index(comment.comment_id)])
    profile.add_ballots(ballots.values())
    return profile

def compute_approval_rules_for_article(article: Article, rules: Iterable[Rule], sizes: Iterable[int]) -> None:
    """
    Compute committee selections for all approval rules and committee sizes,
    and store them in the article's `rule_results`.

    Steps:
        1. Build an abcvoting Profile from the Article.
        2. For each rule in ALL_APPROVAL_RULES and each size in ALL_SELECTION_SIZES:
            - Choose a computation algorithm (skip "gurobi", avoid "brute-force").
            - Run the rule to get a winning committee.
            - Convert candidate indices back into comment_ids.
            - Store results in article.rule_results[rule][size].

    Args:
        article (Article): The article containing comments and participants.
        rules (Iterable[Rule]): A collection of rules to be computed
        sizes (Iterable[int]): A collection of selection sizes for the outcome of the rules

    Notes:
        - Skips "gurobi" algorithms (due to solver dependency).
        - Skips "brute-force" (too slow for realistic data).
    """
    print(f"Computing rules for article {article.title} with {article.num_participants} participants and {article.num_comments} comments")

    comment_ids_mapping = [c.comment_id for c in article.comments]

    profile = article_to_abc_profile(article, comment_ids_mapping)
    for rule in rules:
        for size in sizes:
            print("\t", rule, size)
            res = rule.compute_with_abc_voting(profile, size, comment_ids_mapping)
            if rule.short_name in article.rule_results:
                article.rule_results[rule.short_name][size] = res
            else:
                article.rule_results[rule.short_name] = {size: res}


class TriPAVILPKraiczy2025(Rule):
    short_name = "tri_pav_KPPS25"
    long_name = "Proportional Trichotomous Voting by Kraiczy, Papasotiropoulos, Pierczyński & Skowron, 2025"

    @classmethod
    def _trivoting_wrapper(cls, profile, size) -> Selection:
        return thiele_method(profile, max_size_selection=size, ilp_builder_class=PAVILPKraiczy2025)

class TriPAVILPTalmonPage2021(Rule):
    short_name = "tri_pav_TP21"
    long_name = "Proportional Trichotomous Voting by Talmon and Page, 2021"

    @classmethod
    def _trivoting_wrapper(cls, profile, size) -> Selection:
        return thiele_method(profile, max_size_selection=size, ilp_builder_class=PAVILPTalmonPage2021)

class TriPAVILPHervounin2025(Rule):
    short_name = "tri_pav_Herv25"
    long_name = "Proportional Trichotomous Voting by Hervouin, 2025"

    @classmethod
    def _trivoting_wrapper(cls, profile, size) -> Selection:
        return thiele_method(profile, max_size_selection=size, ilp_builder_class=PAVILPHervouin2025)

class TriTaxMESKPPS2025(Rule):
    short_name = "tax_MES_KPPS25"
    long_name = "Taxed Method of Equal Shares by Kraiczy, Papasotiropoulos, Pierczyński & Skowron, 2025"

    @classmethod
    def _trivoting_wrapper(cls, profile, size) -> Selection:
        return tax_method_of_equal_shares(profile, max_size_selection=size, tax_function=TaxKraiczy2025)

class TriSeqPhrag(Rule):
    short_name = "tri_seq_phragmen"
    long_name = "Sequential Phragmèn for trichotomous profiles"

    @classmethod
    def _trivoting_wrapper(cls, profile, size) -> Selection:
        return sequential_phragmen(profile, max_size_selection=size)

class TriTaxSeqPhrag(Rule):
    short_name = "tri_tax_seq_phragmen"
    long_name = "Taxed Sequential Phragmèn for trichotomous profiles"

    @classmethod
    def _trivoting_wrapper(cls, profile, size) -> Selection:
        return tax_sequential_phragmen(profile, max_size_selection=size, tax_function=TaxKraiczy2025)

def compute_trichotomous_rules_for_article(article: Article, rules: Iterable[Rule], sizes: Iterable[int]) -> None:
    """
    Compute selections for all trichotomous rules and selection sizes,
    and store them in the article's `rule_results`.

    Steps:
        1. Build a trivoting Profile from the Article.
        2. For each rule in ALL_TRICHOTOMOUS_RULES and each size in ALL_SELECTION_SIZES:
            - Run the trivoting rule to get a selection.
            - Convert candidate indices back into comment_ids.
            - Store results in article.rule_results[rule][size].

    Args:
        article (Article): The article containing comments and participants.
        rules (Iterable[Rule]): A collection of rules to be computed
        sizes (Iterable[int]): A collection of selection sizes for the outcome of the rules
    """
    print(f"Computing rules for article {article.title} with {article.num_participants} participants and {article.num_comments} comments")

    comment_ids_mapping = [c.comment_id for c in article.comments]

    profile = article_to_trivoting_profile(article, comment_ids_mapping)
    for rule in rules:
        for size in sizes:
            print("\t", rule, size)
            res = rule.compute_with_trivoting(profile, size, comment_ids_mapping)
            if rule.short_name in article.rule_results:
                article.rule_results[rule.short_name][size] = res
            else:
                article.rule_results[rule.short_name] = {size: res}

def compute_rules_for_article(article: Article, approval_rules: Iterable[Rule], trichotomous_rules: Iterable[Rule], sizes: Iterable[int]) -> None:
    """
    Compute selections for all approval and trichotomous rules and selection sizes,
    and store them in the article's `rule_results`.

    Args:
        article (Article): The article containing comments and participants.
        approval_rules (Iterable[Rule]): A collection of approval rules to be computed
        trichotomous_rules (Iterable[Rule]): A collection of trichotomous rules to be computed
        sizes (Iterable[int]): A collection of selection sizes for the outcome of the rules
    """
    compute_approval_rules_for_article(article, approval_rules, sizes)
    compute_trichotomous_rules_for_article(article, trichotomous_rules, sizes)
