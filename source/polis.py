from __future__ import annotations

import csv
import os
from collections.abc import Iterable
from datetime import datetime

import markdown

from article import Article, Comment


class PolisComment:
    """
    Represents a single comment in a Polis poll.

    Attributes:
        comment (str): The text of the comment.
        timestamp (str): The timestamp when the comment was created.
        comment_id (str): Unique identifier for the comment.
        author_id (str): Unique identifier of the comment's author.
        num_agrees (int): Number of participants who agreed with the comment.
        num_disagrees (int): Number of participants who disagreed with the comment.
        extra (dict): Optional dictionary for storing additional metadata.
    """

    def __init__(self, comment: str, timestamp: str, comment_id: str, author_id: str, num_agrees: int, num_disagrees: int, extra: dict = None):
        """
        Initialize a PolisComment instance.

        Args:
            comment (str): The comment text.
            timestamp (str): The time the comment was posted.
            comment_id (str): Unique ID for the comment.
            author_id (str): ID of the participant who wrote the comment.
            num_agrees (int): Number of agrees the comment received.
            num_disagrees (int): Number of disagrees the comment received.
            extra (dict, optional): Additional metadata (default: empty dict).
        """
        self.comment = comment
        self.timestamp = timestamp
        self.comment_id = comment_id
        self.author_id = author_id
        self.num_agrees = num_agrees
        self.num_disagrees = num_disagrees
        if extra is None:
            extra = dict()
        self.extra = extra

    def __str__(self):
        return f"Comment [{self.comment_id}]: {self.comment}"

class PolisParticipant:
    """
    Represents a participant in a Polis poll.

    Attributes:
        participant_id (str): Unique identifier of the participant.
        votes (dict[str, int | None]): Mapping of comment IDs to votes: 1 = agree, -1 = disagree, None = pass/skip.
    """

    def __init__(self, participant_id: str, votes: dict[str, int | None] = None):
        """
        Initialize a PolisParticipant instance.

        Args:
            participant_id (str): Unique ID for the participant.
            votes (dict[str, int | None], optional): Votes cast by the participant.
                Defaults to an empty dict.
        """
        self.participant_id = participant_id
        if votes is None:
            votes = dict()
        self.votes = votes

    def __str__(self):
        return f"Participant [{self.participant_id}]"

class PolisPoll:
    """
    Represents a full Polis poll with comments and participants.

    Attributes:
        name (str): Name of the poll.
        url (str): URL of the poll.
        comments (list[PolisComment]): List of comments in the poll.
        participants (list[PolisParticipant]): List of participants in the poll.
        description (str): Optional description of the poll.
    """

    def __init__(self, name: str = None, url: str = None, comments: Iterable[PolisComment] = None, participants: Iterable[PolisParticipant] = None, description: str = None):
        """
        Initialize a PolisPoll instance.

        Args:
            name (str, optional): The poll's name (default: empty string).
            url (str, optional): The poll's URL (default: empty string).
            comments (Iterable[PolisComment], optional): Comments in the poll.
                Defaults to an empty list.
            participants (Iterable[PolisParticipant], optional): Participants in the poll.
                Defaults to an empty list.
            description (str, optional): Description of the poll.
        """

        if name is None:
            name = ""
        self.name = name
        if url is None:
            url = ""
        self.url = url
        if comments is None:
            comments = []
        self.comments = list(comments)
        if participants is None:
            participants = []
        self.participants = list(participants)
        self.description = description

    @property
    def num_comments(self) -> int:
        """Return the number of comments in the poll."""
        return len(self.comments)

    @property
    def num_participants(self) -> int:
        """Return the number of participants in the poll."""
        return len(self.participants)

    def __str__(self):
        return f"Poll {self.name}"

def read_polis_summary(file_path: str) -> PolisPoll:
    """
    Read the `summary.csv` file and construct a `PolisPoll` object
    with basic metadata (topic, URL, description).

    Args:
        file_path (str): Path to the summary CSV file.

    Returns:
        PolisPoll: A poll with metadata fields populated, but without
        comments or participants yet.
    """
    poll = PolisPoll()
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue  # skip malformed rows
            key = row[0].strip()
            # join rest of row columns if any, since value can contain commas and newlines
            value = ','.join(row[1:]).strip()
            if key == "topic":
                poll.name = value
            elif key == "url":
                poll.url = value
            elif key == "conversation-description":
                poll.description = value
    return poll

def read_polis_comments(file_path: str) -> list[PolisComment]:
    """
    Read the `comments.csv` file and return a list of `PolisComment` objects.

    Args:
        file_path (str): Path to the comments CSV file.

    Returns:
        list[PolisComment]: A list of all comments in the poll.
    """
    all_comments = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Extract required fields
            comment = row.pop("comment-body")
            timestamp = row.pop("timestamp")
            comment_id = row.pop("comment-id")
            author_id = row.pop("author-id")
            num_agrees = int(row.pop("agrees"))
            num_disagrees = int(row.pop("disagrees"))

            # Any remaining columns are stored in "extra"
            extra = row
            all_comments.append(PolisComment(comment, timestamp, comment_id, author_id, num_agrees, num_disagrees, extra))
    return all_comments

def read_polis_participants(file_path: str, comment_ids: list[str]) -> list[PolisParticipant]:
    """
    Read the `participants-votes.csv` file and return a list of `PolisParticipant` objects.

    Args:
        file_path (str): Path to the participants CSV file.
        comment_ids (list[str]): List of comment IDs for which votes should be recorded.

    Returns:
        list[PolisParticipant]: A list of participants with their votes.
    """
    all_participants = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            participant_id = row.pop("participant")
            participant = PolisParticipant(participant_id)

            # Fill in votes for each known comment ID
            for comment_id in comment_ids:
                vote = row.get(comment_id)
                if vote:
                    participant.votes[comment_id] = int(vote)
                else:
                    participant.votes[comment_id] = None
            all_participants.append(participant)
    return all_participants

def read_polis_poll(dir_path: str) -> PolisPoll:
    """
    Read a full Polis poll from a directory containing:
      - `summary.csv`
      - `comments.csv`
      - `participants-votes.csv`

    Args:
        dir_path (str): Path to the directory with Polis poll CSV files.

    Returns:
        PolisPoll: A complete poll object with metadata, comments, and participants.
    """

    print("Reading polis poll raw_data from: " + dir_path)

    # Load poll summary (name, url, description)
    summary_path = os.path.join(dir_path, "summary.csv")
    poll = read_polis_summary(summary_path)

    # Load poll comments
    comments_path = os.path.join(dir_path, 'comments.csv')
    poll.comments = read_polis_comments(comments_path)

    # Load poll participants (requires comment IDs to map votes)
    participants_path = os.path.join(dir_path, 'participants-votes.csv')
    comment_ids = [str(c.comment_id) for c in poll.comments]
    poll.participants = read_polis_participants(participants_path, comment_ids)

    return poll

def polis_poll_to_article(poll: PolisPoll, ignore_not_seen: bool = True) -> Article:
    """
    Converts a PolisPoll object to an Article object.

    Args:
        poll (PolisPoll): The Polis poll.
        ignore_not_seen (bool, optional): If ture, comments not seen by the participants are not explicitely stored. This saves space. Defaults to True.

    Returns:
        Article: An article representing the Polis poll.
    """
    article_title = poll.name or "Untitled Polis Poll"
    if poll.description:
        article_body = f'<p>{markdown.markdown(poll.description)}</p>'
    else:
        article_body = '<p>This article has been automatically fetched from a Polis poll that did not include a description.</p>'

    article_sources = {"Original Polis poll": poll.url}

    article = Article(
        title=article_title,
        text=article_body,
        category="",
        sources=article_sources,
        participant_ids=[pp.participant_id for pp in poll.participants],
    )

    for pc_index, pc in enumerate(sorted(poll.comments, key=lambda c: c.timestamp)):
        dt = datetime.fromtimestamp(int(pc.timestamp) / 1000)  # It is probably Unix Epoch in ms
        formatted_dt = dt.strftime("%Y-%m-%d %H:%M")

        # Retrieving the votes of the participants for the comment
        agreeing_ids = []
        disagreeing_ids = []
        passed_ids = []
        not_seen_ids = []
        for pp in poll.participants:
            vote = pp.votes.get(pc.comment_id)
            if vote is None and not ignore_not_seen:
                not_seen_ids.append(pp.participant_id)
            elif vote == 0:
                passed_ids.append(pp.participant_id)
            elif vote == 1:
                agreeing_ids.append(pp.participant_id)
            elif vote == -1:
                disagreeing_ids.append(pp.participant_id)

        # Registering the comment
        article.comments.append(
            Comment(
                comment_id=pc.comment_id,
                text=pc.comment,
                timestamp=pc.timestamp,
                author=f"User {pc_index + 1}",
                agreeing_ids=agreeing_ids,
                disagreeing_ids=disagreeing_ids,
                passed_ids=passed_ids,
                not_seen_ids=not_seen_ids,
                beautified_timestamp=formatted_dt
            )
        )
    article.comments.sort(key=lambda c: c.timestamp, reverse=True)

    return article

def remove_demographic_comments(article: Article) -> None:
    """
    For an article object representing a Polis poll, removes the demographic comments that interfere with the analysis.
    Do so in place.

    Args:
        article (Article): An article object representing a Polis poll.
    """
    comment_ids_to_remove = None
    if article.slugified_title == "auniversalbasicincomeforaotearoanz":
        comment_ids_to_remove = {
            "32", "33", "34", "35", "36", "39", "40", "38", "42", "41"
        }
    elif article.slugified_title == ["taxhivemindwindow", "fairenoughhowshouldnewzealandersbetaxed"]:
        comment_ids_to_remove = {
            "10", "0", "1", "2", "9", "5", "4", "3", "8", "7", "6", "14", "13", "12", "11"
        }
    elif article.slugified_title == ["hivemind-freshwaterqualityinnz", "freshwaterqualityinnewzealand"]:
        comment_ids_to_remove = {
            "24", "25", "26", "27", "29", "28", "35", "34", "33", "32", "31", "30", "36"
        }
    elif article.slugified_title == ["jointhediscussionbelowlanduseandconservationinthesanjuanislands", "landuseandconservationinthesanjuanislands"]:
        comment_ids_to_remove = {
            "53", "192", "54", "55", "67", "66", "65", "64", "69", "68", "70",
        }
    elif article.slugified_title == "protectingandrestoringnewzealandsbiodiversity":
        comment_ids_to_remove = {
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16",
        }
    elif article.slugified_title == "canadianelectoralreform":
        comment_ids_to_remove = {
            "5", "152", "151", "150", "154", "124", "112", "113", "89", "77",
        }
    elif article.slugified_title == "cantherebeconsensusonbrexit":
        comment_ids_to_remove = {
            "0", "1", "10", "11", "15"
        }
    elif article.slugified_title == "operationmarchingorders":
        comment_ids_to_remove = {
            "31", "1715", "1047", "680", "32", "33", "34", "35", "36", "37", "38", "39", "41", "42", "43", "44", "45",
            "46", "47", "48", "49", "73", "76", "95", "24", "715", "818", "1321", "1322", "228", "1320", "473", "226",
            "202", "751", "505", "599", "151", "1323", "365", "1047", "95", "549",
        }
    elif article.slugified_title == "whatisthebestwaytoengagemoreyoungpeopleinlocalscrutinyofpolicing":
        comment_ids_to_remove = {
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"
        }
    elif article.slugified_title == ["scoopnzhivemindonaffordablehousing", "affordablehousinginnewzealand"]:
        comment_ids_to_remove = {
            "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40"
        }

    if comment_ids_to_remove:
        article.comments = [c for c in article.comments if c.comment_id not in comment_ids_to_remove]


def overwrite_default_content(article: Article) -> None:
    """
    For an article object representing a Polis poll, overwrites some default content. Used to provide extra information
    that is not available in the Polis CSV files.

    Args:
        article (Article): An article object representing a Polis poll.
    """
    if article.slugified_title in ["taxhivemindwindow", "fairenoughhowshouldnewzealandersbetaxed"]:
        article.title = "Fair enough? How should New Zealanders be taxed?"
        article.sources["Soop article"] = "https://www.scoop.co.nz/stories/HL1804/S00054/fair-enough-how-should-new-zealanders-be-taxed.htm"
        article.html_include_file = "new_zealand_tax.html"

    if article.slugified_title == "auniversalbasicincomeforaotearoanz":
        article.title = "A Universal Basic Income for Aotearoa NZ?"
        article.sources["Soop article"] = "https://www.scoop.co.nz/stories/HL1708/S00025/hivemind-universal-basic-income-are-we-up-for-it.htm"
        article.sources["Soop article"] = "https://www.scoop.co.nz/stories/HL1709/S00031/hivemind-report-a-universal-basic-income-for-aotearoa-nz.htm"
        article.html_include_file = "new_zealand_universal_income.html"

    if article.slugified_title == "protectingandrestoringnzsbiodiversity":
        article.title = "Protecting and Restoring New Zealand's Biodiversity"
        article.sources["Soop article"] = "https://www.scoop.co.nz/stories/HL1908/S00014/scoop-hivemind-protecting-and-restoring-biodiversity.htm"
        article.html_include_file = "new_zealand_biodiversity.html"

    if article.slugified_title in ["hivemind-freshwaterqualityinnz", "freshwaterqualityinnewzealand"]:
        article.title = "Freshwater Quality in New Zealand"
        article.sources["Soop article"] = "https://www.scoop.co.nz/stories/HL1707/S00042/opening-the-election-hivemind-freshwater-quality.htm"
        article.html_include_file = "new_zealand_freshwater.html"

    if article.slugified_title in ["scoopnzhivemindonaffordablehousing", "affordablehousinginnewzealand"]:
        article.title = "Affordable Housing in New Zealand"
        article.sources["Soop article"] = "https://www.scoop.co.nz/stories/HL1706/S00034/making-housing-affordable-lets-crack-it.htm"
        article.html_include_file = "new_zealand_affordable_housing.html"

    if article.slugified_title in ["jointhediscussionbelowlanduseandconservationinthesanjuanislands", "landuseandconservationinthesanjuanislands"]:
        article.title = "Land use and conservation in the San Juan Islands"

    if article.slugified_title in ["15hour", "newminimumwageinseattle15hour"]:
        article.title = "New minimum wage in Seattle: $15/hour"

    if article.slugified_title in ["energie", "ernhrungundlandnutzung", "mobilitt", "produktionundkonsum", "wohnen"]:
        article.title += " [DE]"

    if article.slugified_title == "uberxvtaiwantw":
        article.title += " [ZH]"

    title_to_categories = {
        "newminimumwageinseattle15hour": "Economy",
        "auniversalbasicincomeforaotearoanz": "Economy",
        "canadianelectoralreform": "Politics",
        "cantherebeconsensusonbrexit": "Politics",
        "concussionsinthenfl": "Sports",
        "energie": "Environment",
        "energiede": "Environment",
        "ernhrungundlandnutzungde": "Environment",
        "fairenoughhowshouldnewzealandersbetaxed": "Economy",
        "freshwaterqualityinnewzealand": "Environment",
        "improvingbowlinggreenwarrencounty": "Society",
        "landuseandconservationinthesanjuanislands": "Environment",
        "mobilittde": "Environment",
        "operationmarchingorders": "Politics",
        "produktionundkonsumde": "Society",
        "protectingandrestoringnewzealandsbiodiversity": "Environment",
        "affordablehousinginnewzealand": "Society",
        "togetherwellbuildthebgof2050": "Society",
        "uberxvtaiwantw": "Society",
        "uberxvtaiwantwzh": "Society",
        "whatisthebestwaytoengagemoreyoungpeopleinlocalscrutinyofpolicing": "Politics",
        "wohnende": "Society",
    }
    article.category = title_to_categories[article.slugified_title]


def read_polis_dir_as_articles(in_dir_path) -> list[Article]:
    """
    Reads the content of a directory containing Polis poll raw data. Returns a list of articles corresponding to the
    polls.

    Args:
        in_dir_path (str): Path to the directory containing Polis poll raw data.

    Returns:
        list[Article]: List of articles corresponding to the polls.
    """
    res = []
    for poll_dir in os.listdir(in_dir_path):
        poll = read_polis_poll(os.path.join(in_dir_path, poll_dir))
        article = polis_poll_to_article(poll)
        overwrite_default_content(article)
        remove_demographic_comments(article)
        res.append(article)
    return res
