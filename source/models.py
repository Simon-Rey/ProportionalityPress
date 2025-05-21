from collections.abc import Iterable

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
    def __init__(self, text, timestamp, author, num_agrees, num_disagrees):
        self.text = text
        self.timestamp = timestamp
        self.author = author
        self.num_agrees = num_agrees
        self.num_disagrees = num_disagrees

class Article:
    def __init__(self, title, text, comments: Iterable[Comment] = None):
        self.title = title
        self.slugified_title = slugify(strip_non_basic_characters(title))
        self.text = text
        if comments is None:
            comments = []
        self.comments = list(comments)

    @property
    def link(self):
        return self.slugified_title + ".html"
