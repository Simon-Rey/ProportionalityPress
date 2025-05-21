import os

from source.generate import generate_site
from source.models import default_config
from source.polis import read_polis_poll, polis_poll_to_models


def main():
    source_dir_path = os.path.dirname(os.path.realpath(__file__))
    polis_data_dir_path = os.path.join(source_dir_path, 'data', 'polis_data')

    all_articles = []
    for poll_dir in os.listdir(polis_data_dir_path):
        poll = read_polis_poll(os.path.join(polis_data_dir_path, poll_dir))
        all_articles.append(polis_poll_to_models(poll))

    # poll = read_polis_poll(os.path.join(polis_data_dir_path, "canadian-electoral-reform"))
    # article = polis_poll_to_models(poll)

    config = default_config()
    generate_site(config, all_articles)

if __name__ == '__main__':
    main()