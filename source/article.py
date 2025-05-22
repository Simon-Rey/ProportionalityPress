import json
from collections.abc import Iterable, Collection

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

class Article:
    def __init__(self, title: str, text: str, source: str, comments: Iterable[Comment] = None, participant_ids: Iterable[str] = None, representative_comments: dict[str, dict[int, Iterable[Comment]]] = None):
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
        if representative_comments is None:
            representative_comments = dict()
        self.representative_comments = representative_comments
        self.computed_rules = []
        self.computed_sizes = []
        self.sanitize_representative_comments()

    @property
    def num_comments(self):
        return len(self.comments)

    @property
    def num_participants(self):
        return len(self.participant_ids)

    @property
    def link(self):
        return self.slugified_title + ".html"

    def sanitize_representative_comments(self):
        # Map each rules to the sizes computed for the rule
        rules_to_sizes = dict()
        for rule, rule_dict in self.representative_comments.items():
            rules_to_sizes[rule] = []
            for size, res in rule_dict.items():
                rules_to_sizes[rule].append(size)
                assert len(res) == size
        # Select the reference set of sizes as the largest set computed for a rule
        reference_sizes = None
        for sizes in rules_to_sizes.values():
            sizes.sort()
            if reference_sizes is None or len(sizes) > len(reference_sizes):
                reference_sizes = sizes
        self.computed_sizes = reference_sizes
        # Drop all the rules that have not been computed for all sizes
        for rule, rule_sizes in rules_to_sizes.items():
            if rule_sizes != reference_sizes:
                del self.representative_comments[rule]
            else:
                self.computed_rules.append(rule)

    def to_dict(self):
        return {
            "title": self.title,
            "slugified_title": self.slugified_title,
            "text": self.text,
            "source": self.source,
            "link": self.link,
            "comments": [comment.to_dict() for comment in self.comments],
            "participant_ids": self.participant_ids,
            "representative_comments": self.representative_comments,
        }

    @classmethod
    def from_dict(cls, data: dict):
        comments = [Comment.from_dict(c) for c in data.get("comments", [])]

        # Size keys are automatically cast as str, we map them back to int
        raw_rep_comments = data.get("representative_comments", dict())
        rep_comments = {}
        for rule, size_dict in raw_rep_comments.items():
            rep_comments[rule] = {int(size): comment_list for size, comment_list in size_dict.items()}

        return cls(
            title=data["title"],
            text=data["text"],
            source=data["source"],
            comments=comments,
            participant_ids=data.get("participant_ids", []),
            representative_comments=rep_comments,
        )

def dump_article_to_json(article: Article, filepath: str):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(article.to_dict(), f, ensure_ascii=False, indent=2)

def load_article_from_json(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        return Article.from_dict(json.load(f))
