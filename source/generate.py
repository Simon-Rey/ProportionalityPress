import os
import shutil

from jinja2 import Environment, FileSystemLoader, select_autoescape

from source.models import Article, SiteConfig

def copy_static(static_dir: str, output_dir: str):
    dst = os.path.join(output_dir, "static")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(static_dir, dst)

def generate_site(config: SiteConfig, articles: list[Article]):
    # Delete (if needed) and create output dir
    base_path = os.path.dirname(os.path.realpath(__file__))
    output_dir_path = os.path.join(base_path, config.output_dir)
    if os.path.exists(output_dir_path):
        shutil.rmtree(output_dir_path)
    os.makedirs(output_dir_path)

    # Load templates
    template_dir_path = os.path.join(base_path, config.template_dir)
    env = Environment(
        loader=FileSystemLoader(template_dir_path),
        autoescape=select_autoescape(['html', 'xml'])
    )
    article_template = env.get_template("article.html")

    # Write each article
    for article in articles:
        print(f"Writing article {article.title}")
        html = article_template.render(
            article=article,
            all_articles=articles,
            config=config
        )

        with open(os.path.join(output_dir_path, article.link), "w", encoding="utf-8") as f:
            f.write(html)

    # Copy the static files to the output folder
    static_dir_path = os.path.join(base_path, config.static_dir)
    copy_static(static_dir_path, output_dir_path)
