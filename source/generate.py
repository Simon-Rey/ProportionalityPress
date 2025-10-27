from __future__ import annotations

import os
import shutil
from collections import defaultdict

from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined, Template

from article import Article
from settings import OUTPUT_DIR, TEMPLATES_DIR, STATIC_DIR, STATIC_URL, SITE_NAME, \
    APPROVAL_DEFAULT_RULE_POPULARITY, APPROVAL_DEFAULT_SELECTION_SIZE, APPROVAL_HIGHLIGHTED_ARTICLE_TITLES, \
    APPROVAL_DEFAULT_RULE_REPRESENTATION, APPROVAL_DEFAULT_RULE_DIVERSITY, ABCVOTING_NAME_TO_RULE
from source.settings import ALL_APPROVAL_RULES


def render_template(template_obj: Template, **kwargs) -> str:
    return template_obj.render(
        static_url=STATIC_URL,
        site_name=SITE_NAME,
        **kwargs,
    )

def copy_static(static_dir: str, output_dir: str):
    dst = os.path.join(output_dir, "static")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(static_dir, dst)

def generate_site(articles: list[Article]):
    # Delete (if needed) and create output dir
    base_path = os.path.dirname(os.path.realpath(__file__))
    output_dir_path = os.path.join(base_path, OUTPUT_DIR)
    if os.path.exists(output_dir_path):
        shutil.rmtree(output_dir_path)
    os.makedirs(output_dir_path)

    # Load templates
    template_dir_path = os.path.join(base_path, TEMPLATES_DIR)
    env = Environment(
        loader=FileSystemLoader(template_dir_path),
        autoescape=select_autoescape(['html', 'xml']),
        undefined=StrictUndefined
    )

    articles_per_category = defaultdict(list)
    for article in articles:
        articles_per_category[article.category].append(article)
    articles_per_category = sorted([(c, a) for c, a in articles_per_category.items()], key=lambda x: x[0])

    # Write index page
    index_template = env.get_template("index.html")
    index_html = render_template(
        index_template,
        articles_per_category=articles_per_category,
        all_articles=articles,
        highlighted_articles= [a for a in articles if a.slugified_title in APPROVAL_HIGHLIGHTED_ARTICLE_TITLES]
    )
    with open(os.path.join(output_dir_path, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    # Write each article
    article_template = env.get_template("article.html")
    for article in articles:
        print(f"Writing article {article.title}")
        article.sanitize_rule_results()
        article_html = render_template(
            article_template,
            article=article,
            articles_per_category=articles_per_category,
            all_articles=articles,
            default_size_selection=APPROVAL_DEFAULT_SELECTION_SIZE,
            default_rule_popularity=APPROVAL_DEFAULT_RULE_POPULARITY,
            default_rule_representation=APPROVAL_DEFAULT_RULE_REPRESENTATION,
            default_rule_diversity=APPROVAL_DEFAULT_RULE_DIVERSITY,
            max_comment_approval=max(c.num_agrees for c in article.comments),
            all_rules=ALL_APPROVAL_RULES,
            display_thumbs_down=True
        )

        with open(os.path.join(output_dir_path, article.link), "w", encoding="utf-8") as f:
            f.write(article_html)

    # About page
    about_template = env.get_template("about.html")
    about_html = render_template(
        about_template,
        articles_per_category=articles_per_category,
        all_articles=articles,
    )
    with open(os.path.join(output_dir_path, "about.html"), "w", encoding="utf-8") as f:
        f.write(about_html)

    # Copy the static files to the output folder
    static_dir_path = os.path.join(base_path, STATIC_DIR)
    copy_static(static_dir_path, output_dir_path)
