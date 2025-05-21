from __future__ import annotations

import csv
import os
from collections.abc import Iterable

from source.models import Article, Comment


class PolisComment:
    def __init__(self, comment: str, timestamp: str, comment_id: str, author_id: str, num_agrees: int, num_disagrees: int, extra: dict = None):
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
    def __init__(self, participant_id: str, votes: dict[str, int | None] = None):
        self.participant_id = participant_id
        if votes is None:
            votes = dict()
        self.votes = votes

    def __str__(self):
        return f"Participant [{self.participant_id}]"

class PolisPoll:
    def __init__(self, name: str = None, url: str = None, comments: Iterable[PolisComment] = None, participants: Iterable[PolisParticipant] = None, description: str = None):
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
        return len(self.comments)

    @property
    def num_participants(self) -> int:
        return len(self.participants)

    def __str__(self):
        return f"Poll {self.name}"

def read_polis_summary(file_path: str) -> PolisPoll:
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

def read_polis_comments(file_path: str) -> Iterable[PolisComment]:
    all_comments = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            comment = row.pop("comment-body")
            timestamp = row.pop("timestamp")
            comment_id = row.pop("comment-id")
            author_id = row.pop("author-id")
            num_agrees = int(row.pop("agrees"))
            num_disagrees = int(row.pop("disagrees"))
            extra = row
            all_comments.append(PolisComment(comment, timestamp, comment_id, author_id, num_agrees, num_disagrees, extra))
    return all_comments

def read_polis_participants(file_path: str, comment_ids: list[str]) -> Iterable[PolisParticipant]:
    all_participants = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            participant_id = row.pop("participant")
            participant = PolisParticipant(participant_id)
            for comment_id in comment_ids:
                vote = row.get(comment_id)
                if vote:
                    participant.votes[comment_id] = int(vote)
                else:
                    participant.votes[comment_id] = None
            all_participants.append(participant)
    return all_participants

def read_polis_poll(dir_path: str) -> PolisPoll:
    print("Reading polis poll data from: " + dir_path)
    summary_path = os.path.join(dir_path, "summary.csv")
    poll = read_polis_summary(summary_path)

    comments_path = os.path.join(dir_path, 'comments.csv')
    poll.comments = read_polis_comments(comments_path)

    participants_path = os.path.join(dir_path, 'participants-votes.csv')
    comment_ids = [str(c.comment_id) for c in poll.comments]
    poll.participants = read_polis_participants(participants_path, comment_ids)
    return poll

def polis_poll_to_models(poll: PolisPoll) -> Article:
    article_title = poll.name or "Untitled Polis Poll"
    article_body = '<p>This article summarizes the discussion from a Polis poll'
    if poll.description:
        article_body += ' with the following prompt:</p>'
        article_body += f'<p class="polis-poll-prompt">{poll.description}</p>'
    else:
        article_body += ".</p>"
    article_body += f'<p><strong>Original poll link:</strong> <a href="{poll.url}" target="_blank">{poll.url}</a></p>'

    comments = []
    for pc in poll.comments:
        c = Comment(
            text=pc.comment,
            timestamp=pc.timestamp,
            author=pc.author_id,
            num_agrees=pc.num_agrees,
            num_disagrees=pc.num_disagrees
        )
        comments.append(c)

    article = Article(
        title=article_title,
        text=article_body,
        comments=comments
    )
    return article