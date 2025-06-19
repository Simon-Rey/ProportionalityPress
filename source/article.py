import json
from collections import defaultdict
from collections.abc import Iterable, Collection
from functools import total_ordering

from source.utils import slugify, strip_non_basic_characters


class SiteConfig:
    def __init__(self, site_name, base_url, static_url, output_dir, template_dir, static_dir):
        self.site_name = site_name
        self.base_url = base_url
        self.static_url = static_url
        self.output_dir = output_dir
        self.template_dir = template_dir
        self.static_dir = static_dir

def default_config():
    return SiteConfig(
        site_name="Proportionality Press",
        base_url="/",
        static_url="static/",
        output_dir="_site",
        template_dir="templates",
        static_dir= "static"
    )

class Comment:
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
        return len(self.agreeing_ids)

    @property
    def num_disagrees(self):
        return len(self.disagreeing_ids)

    @property
    def render_timestamp(self):
        if self.beautified_timestamp:
            return self.beautified_timestamp
        return self.timestamp

    def to_dict(self):
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

@total_ordering
class RuleResult:
    def __init__(self,
                 rule_id:str,
                 committee_size: int,
                 committee: Iterable[Comment] = None,
                 satisfaction: int=None,
                 max_satisfaction: int=None,
                 coverage: float=None,
                 max_coverage: float=None,):
        self.rule_id = rule_id
        self.committee_size = committee_size
        if committee is None:
            committee = []
        self.committee = committee
        self.satisfaction = satisfaction
        self.max_satisfaction = max_satisfaction
        self.coverage = coverage
        self.max_coverage = max_coverage

    def to_dict(self):
        return {
            "rule_id": self.rule_id,
            "committee_size": self.committee_size,
            "committee": self.committee,
            "max_satisfaction": self.max_satisfaction,
            "satisfaction": self.satisfaction,
            "coverage": self.coverage,
            "max_coverage": self.max_coverage,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            rule_id=data["rule_id"],
            committee_size=data["committee_size"],
            committee=data["committee"],
            max_satisfaction=data["max_satisfaction"],
            satisfaction=data["satisfaction"],
            coverage=data["coverage"],
            max_coverage=data["max_coverage"],
        )

    def _identifier(self):
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

class Article:
    def __init__(self,
                 title: str,
                 text: str,
                 source: str,
                 comments: Iterable[Comment] = None,
                 participant_ids: Iterable[str] = None,
                 rule_results: dict[str, dict[int, RuleResult]] = None,):
        self.title = title
        self.slugified_title = slugify(strip_non_basic_characters(title))
        self.text = text
        if comments is None:
            comments = []
        self.comments = list(comments)
        self.source = source
        if participant_ids is None:
            participant_ids = []
        self.participant_ids = list(participant_ids)
        if rule_results is None:
            rule_results = dict()
        self.rule_results = rule_results
        self.sanitize_rule_results()

    @property
    def num_comments(self):
        return len(self.comments)

    def get_comment(self, comment_id):
        for c in self.comments:
            if c.comment_id == comment_id:
                return c

    @property
    def num_participants(self):
        return len(self.participant_ids)

    @property
    def link(self):
        return self.slugified_title + ".html"

    @property
    def computed_rules(self):
        return sorted(self.rule_results)

    @property
    def computed_sizes(self):
        return sorted(self.rule_results.values().__iter__().__next__())

    def sanitize_rule_results(self):
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
        return {
            "title": self.title,
            "slugified_title": self.slugified_title,
            "text": self.text,
            "source": self.source,
            "link": self.link,
            "comments": [comment.to_dict() for comment in self.comments],
            "participant_ids": self.participant_ids,
            "rule_results": {rule: {s: r.to_dict() for s, r in rule_dict.items()} for rule, rule_dict in self.rule_results.items()},
        }

    @classmethod
    def from_dict(cls, data: dict):
        comments = [Comment.from_dict(c) for c in data.get("comments", [])]

        raw_rule_results = data.get("rule_results", dict())
        rule_results = {}
        for rule, rule_dict in raw_rule_results.items():
            rule_results[rule] = dict()
            for size, res_data in rule_dict.items():
                rule_results[rule][int(size)] = RuleResult.from_dict(res_data)

        return cls(
            title=data["title"],
            text=data["text"],
            source=data["source"],
            comments=comments,
            participant_ids=data.get("participant_ids", []),
            rule_results=rule_results,
        )

    def rule_results_to_json(self):
        return json.dumps([r.to_dict() for d in self.rule_results.values() for r in d.values()])

def dump_article_to_json(article: Article, filepath: str):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(article.to_dict(), f, ensure_ascii=False, indent=2)

def load_article_from_json(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        return Article.from_dict(json.load(f))
