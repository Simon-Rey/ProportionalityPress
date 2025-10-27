from __future__ import annotations

import os
import shutil
from collections import defaultdict

from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined, Template

from article import Article
from settings import TEMPLATES_DIR, INPUT_STATIC_DIR, STATIC_URL, BallotModeEnum


def render_template(template_obj: Template, **kwargs) -> str:
    return template_obj.render(
        static_url=STATIC_URL,
        **kwargs,
    )

def copy_static(static_dir: str, output_dir_path: str):
    dst = os.path.join(output_dir_path, "static")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(static_dir, dst)

def generate_site(articles: list[Article], output_setting: dict):
    # Delete (if needed) and create output dir
    base_path = os.path.dirname(os.path.realpath(__file__))
    output_dir_path = output_setting['output_dir_path']
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
        highlighted_articles= [a for a in articles if a.slugified_title in output_setting["highlighted_articles"]],
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
            default_size_selection=output_setting["default_selection_size"],
            default_rule_popularity=output_setting["default_popularity_rule"],
            default_rule_representation=output_setting["default_representation_rule"],
            default_rule_diversity=output_setting["default_diversity_rule"],
            max_comment_approval=max(c.num_agrees for c in article.comments),
            all_rules=output_setting["rule_set"],
            display_thumbs_down=output_setting["ballot_mode"] in [BallotModeEnum.TRICHOTOMOUS_ONLY, BallotModeEnum.APPROVAL_AND_TRICHOTOMOUS]
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
    static_dir_path = os.path.join(base_path, INPUT_STATIC_DIR)
    copy_static(static_dir_path, output_dir_path)
