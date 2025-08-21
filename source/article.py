from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Iterable, Collection
from functools import total_ordering

from utils import make_url_friendly


# =============
# Comment Class
# =============

class Comment:
    """
    Represents a comment in an article.

    Attributes:
        comment_id (str): Unique identifier of the comment.
        text (str): The comment text.
        timestamp (str): Raw timestamp string (e.g. from source data).
        beautified_timestamp (str | None): Optional human-readable timestamp
            (e.g. "Jan 5, 2025") for display purposes.
        author (str): Identifier or name of the comment's author.
        agreeing_ids (list[str]): IDs of participants who agreed with this comment.
        disagreeing_ids (list[str]): IDs of participants who disagreed with this comment.
        passed_ids (list[str]): IDs of participants who passed on voting.
        not_seen_ids (list[str]): IDs of participants who did not see this comment.
    """

    def __init__(self, comment_id: str, text: str, timestamp: str, author: str, agreeing_ids: Collection[str] = None, disagreeing_ids: Collection[str] = None, passed_ids: Collection[str] = None, not_seen_ids: Collection[str] = None, beautified_timestamp: str = None):
        self.comment_id = comment_id
        self.text = text
        self.timestamp = timestamp
        self.beautified_timestamp = beautified_timestamp
        self.author = author
        if agreeing_ids is None:
            agreeing_ids = []
        self.agreeing_ids = list(agreeing_ids)
        if disagreeing_ids is None:
            disagreeing_ids = []
        self.disagreeing_ids = list(disagreeing_ids)
        if passed_ids is None:
            passed_ids = []
        self.passed_ids = list(passed_ids)
        if not_seen_ids is None:
            not_seen_ids = []
        self.not_seen_ids = list(not_seen_ids)

    @property
    def num_agrees(self):
        """Return the number of agreeing participants."""
        return len(self.agreeing_ids)

    @property
    def num_disagrees(self):
        """Return the number of disagreeing participants."""
        return len(self.disagreeing_ids)

    @property
    def render_timestamp(self):
        """
        Return the beautified timestamp if available,
        otherwise fall back to the raw timestamp.
        """
        if self.beautified_timestamp:
            return self.beautified_timestamp
        return self.timestamp

    def to_dict(self):
        """Convert this Comment to a serializable dictionary."""
        return {
            "comment_id": self.comment_id,
            "text": self.text,
            "timestamp": self.timestamp,
            "beautified_timestamp": self.beautified_timestamp,
            "author": self.author,
            "agreeing_ids": self.agreeing_ids,
            "disagreeing_ids": self.disagreeing_ids,
            "passed_ids": self.passed_ids,
            "not_seen_ids": self.not_seen_ids,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Construct a Comment from a dictionary representation."""
        return cls(
            comment_id=data["comment_id"],
            text=data["text"],
            timestamp=data["timestamp"],
            beautified_timestamp=data.get("beautified_timestamp"),
            author=data["author"],
            agreeing_ids=data["agreeing_ids"],
            disagreeing_ids=data["disagreeing_ids"],
            passed_ids=data["passed_ids"],
            not_seen_ids=data["not_seen_ids"],
        )


# =================
# Rule Result Class
# =================

@total_ordering
class RuleResult:
    """
    Represents the output of a rule applied to select a committee of comments.

    Attributes:
        rule_id (str): Identifier of the rule (e.g., "greedy", "random").
        committee_size (int): Number of comments in the selected committee.
        committee (Iterable[Comment]): The selected set of comments.
        satisfaction (int | None): Satisfaction score for this result.
        max_satisfaction (int | None): Maximum achievable satisfaction.
        coverage (float | None): Coverage score for this result.
        max_coverage (float | None): Maximum achievable coverage.
        sat_distribution (dict[str, int] | None): Distribution of satisfaction values.
    """
    def __init__(self,
                 rule_id:str,
                 committee_size: int,
                 committee: Iterable[Comment] = None,
                 satisfaction: int=None,
                 max_satisfaction: int=None,
                 coverage: float=None,
                 max_coverage: float=None,
                 sat_distribution: dict[str, int] = None):
        self.rule_id = rule_id
        self.committee_size = committee_size
        if committee is None:
            committee = []
        self.committee = committee
        self.satisfaction = satisfaction
        self.max_satisfaction = max_satisfaction
        self.coverage = coverage
        self.max_coverage = max_coverage
        self.sat_distribution = sat_distribution

    def to_dict(self):
        """Convert this RuleResult into a serializable dictionary."""
        return {
            "rule_id": self.rule_id,
            "committee_size": self.committee_size,
            "committee": self.committee,
            "max_satisfaction": self.max_satisfaction,
            "satisfaction": self.satisfaction,
            "coverage": self.coverage,
            "max_coverage": self.max_coverage,
            "sat_distribution": self.sat_distribution,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Construct a RuleResult from a dictionary representation."""
        return cls(
            rule_id=data["rule_id"],
            committee_size=data["committee_size"],
            committee=data["committee"],
            max_satisfaction=data["max_satisfaction"],
            satisfaction=data["satisfaction"],
            coverage=data["coverage"],
            max_coverage=data["max_coverage"],
            sat_distribution=data["sat_distribution"],
        )

    def _identifier(self) -> tuple[str, int]:
        return self.rule_id, self.committee_size

    def __eq__(self, other):
        if isinstance(other, RuleResult):
            return self._identifier() == other._identifier()
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, RuleResult):
            return self._identifier() < other._identifier()
        return NotImplemented

    def __hash__(self):
        return hash(self._identifier())

    def __repr__(self):
        return f"Res[{self.rule_id}, {self.committee_size}]"


# =============
# Article Class
# =============

class Article:
    """
    Represents an article on the website, derived from PolisPoll or other sources.

    Attributes:
        title (str): Title of the article.
        slugified_title (str): URL-friendly version of the title.
        category (str): Category of the article (e.g., "Politics").
        text (str): Main body text of the article.
        sources (dict[str, str]): Mapping of source names to URLs.
        html_include_file (str | None): Optional HTML include file for custom snippets.
        comments (list[Comment]): Comments associated with the article.
        participant_ids (list[str]): IDs of participants included in this article.
        rule_results (dict[str, dict[int, RuleResult]]): Nested mapping of
            {rule_id → {committee_size → RuleResult}}.
    """
    def __init__(self,
                 title: str,
                 category: str,
                 text: str,
                 sources: dict[str, str],
                 html_include_file: str=None,
                 comments: Iterable[Comment] = None,
                 participant_ids: Iterable[str] = None,
                 rule_results: dict[str, dict[int, RuleResult]] = None, ):
        self.title = title
        self.category = category
        self.text = text
        if comments is None:
            comments = []
        self.comments = list(comments)
        self.sources = sources
        self.html_include_file = html_include_file
        if participant_ids is None:
            participant_ids = []
        self.participant_ids = list(participant_ids)
        if rule_results is None:
            rule_results = dict()
        self.rule_results = rule_results
        self.sanitize_rule_results()

    @property
    def slugified_title(self) -> str:
        return make_url_friendly(self.title)

    @property
    def num_comments(self) -> int:
        """Return the number of comments in this article."""
        return len(self.comments)

    def get_comment(self, comment_id: str) -> Comment | None:
        """Return a comment by ID, or None if not found."""
        return next((c for c in self.comments if c.comment_id == comment_id), None)

    @property
    def num_participants(self) -> int:
        """Return the number of participants for this article."""
        return len(self.participant_ids)

    @property
    def link(self) -> str:
        """Return the filename for this article's HTML page."""
        return self.slugified_title + ".html"

    @property
    def computed_rules(self) -> list[str]:
        """Return a sorted list of rule IDs computed for this article."""
        return sorted(self.rule_results)

    @property
    def computed_sizes(self) -> list[int]:
        """
        Return a sorted list of committee sizes computed (using the first rule as reference).
        """
        return sorted(next(iter(self.rule_results.values())))

    @property
    def html_include_file_path(self) -> str | None:
        """Return the relative path to the include file if set, otherwise None."""
        if self.html_include_file is None:
            return None
        return f"includes/articles/{self.html_include_file}"

    def sanitize_rule_results(self):
        """
        Ensure all rules only keep committee sizes that are common to all rules.

        This guarantees comparability between rules (i.e. each rule has results
        for the same set of sizes).
        """
        # Map each rules to the sizes computed for the rule
        rules_to_sizes = defaultdict(set)
        for rule, rule_dict in self.rule_results.items():
            for size, res in rule_dict.items():
                rules_to_sizes[rule].add(size)
                assert len(res.committee) == size
        # Reference set of sizes is the intersection of the sizes set of each rule
        if len(rules_to_sizes) > 0:
            reference_sizes = set.intersection(*rules_to_sizes.values())
            # Drop all non-reference sizes
            for rule, rule_sizes in rules_to_sizes.items():
                for size in rule_sizes:
                    if size not in reference_sizes:
                        del self.rule_results[rule][size]

    def to_dict(self):
        """Convert this Article into a serializable dictionary."""
        return {
            "title": self.title,
            "slugified_title": self.slugified_title,
            "category": self.category,
            "text": self.text,
            "sources": self.sources,
            "html_include_file": self.html_include_file,
            "link": self.link,
            "comments": [comment.to_dict() for comment in self.comments],
            "participant_ids": self.participant_ids,
            "rule_results": {rule: {s: r.to_dict() for s, r in rule_dict.items()} for rule, rule_dict in self.rule_results.items()},
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Construct an Article from a dictionary representation."""
        comments = [Comment.from_dict(c) for c in data.get("comments", [])]

        raw_rule_results = data.get("rule_results", dict())
        rule_results = {}
        for rule, rule_dict in raw_rule_results.items():
            rule_results[rule] = dict()
            for size, res_data in rule_dict.items():
                rule_results[rule][int(size)] = RuleResult.from_dict(res_data)

        return cls(
            title=data["title"],
            category=data["category"],
            text=data["text"],
            html_include_file=data["html_include_file"],
            sources=data["sources"],
            comments=comments,
            participant_ids=data.get("participant_ids", []),
            rule_results=rule_results,
        )

    def rule_results_to_json(self):
        return json.dumps([r.to_dict() for d in self.rule_results.values() for r in d.values()])

def dump_article_to_json(article: Article, filepath: str) -> None:
    """
    Save an Article object to a JSON file.

    Args:
        article (Article): The article to save.
        filepath (str): Path to the output file.
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(article.to_dict(), f, ensure_ascii=False, indent=2)

def load_article_from_json(filepath: str) -> Article:
    """
    Load an Article object from a JSON file.

    Args:
        filepath (str): Path to the input file.

    Returns:
        Article: The deserialized article object.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return Article.from_dict(json.load(f))
