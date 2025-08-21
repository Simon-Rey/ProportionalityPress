from __future__ import annotations

import os
import shutil
from collections import defaultdict

from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined, Template

from article import Article
from source.settings import RULE_NAME_MAPPING, OUTPUT_DIR, TEMPLATES_DIR, STATIC_DIR, STATIC_URL, SITE_NAME


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
    highlighted_articles_title = ["newminimumwageinseattle15hour", "ernhrungundlandnutzungde", "mobilittde", "operationmarchingorders", "canadianelectoralreform"]
    index_template = env.get_template("index.html")
    index_html = render_template(
        index_template,
        articles_per_category=articles_per_category,
        all_articles=articles,
        highlighted_articles= [a for a in articles if a.slugified_title in highlighted_articles_title]
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
            default_rule_popularity="av",
            default_rule_representation="equal-shares-with-increment-completion",
            default_rule_diversity="cc",
            rule_name_mapping=RULE_NAME_MAPPING,
            max_comment_approval=max(c.num_agrees for c in article.comments),
            display_thumbs_down=False
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
