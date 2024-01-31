#!/usr/bin/env python
import re
import requests
from bs4 import BeautifulSoup
import flask
import os
import git
from prometheus_flask_exporter import PrometheusMetrics


app = flask.Flask(__name__)
metrics = PrometheusMetrics(app)

metrics.info("app_info", "Galaxy OEmbed Server", version="1.0.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GTN_URL = "https://training.galaxyproject.org/"
GIT_REV = git.commit(BASE_DIR)

INDEX_CONTENTS = ""
with open("index.html") as f:
    INDEX_CONTENTS = f.read().replace("GIT_REV", GIT_REV)


# Server a / route
@app.route("/")
def index():
    return INDEX_CONTENTS


@app.route("/index.html")
def home():
    return INDEX_CONTENTS


@app.route("/oembed")
@metrics.counter(
    "oembed",
    "Number of oembed loads",
    labels={
        "url": lambda: flask.request.args.get("url"),
        "user_agent": lambda: flask.request.headers.get("User-Agent"),
    },
)
@metrics.histogram(
    "requests_by_status_and_path",
    "Request latencies by status and path",
    labels={
        "status": lambda r: r.status_code,
        "path": lambda: flask.request.args.get("url"),
    },
)
def oembed():
    # Get url + format from url params:
    url = flask.request.args.get("url")
    fmt = flask.request.args.get("format", "json")
    # Get user agent
    user_agent = flask.request.headers.get("User-Agent")

    if not user_agent:
        return flask.jsonify({"error": "Unsupported User Agent, returning an error message to ensure you get a more sensible link preview."}), 400

    # Currently we're targetting two platforms: slack and discourse.
    # Mastodon is showing it as a video which is hilarious and not helpful.
    if not ('Discourse Forum Onebox' in user_agent or 'Slackbot-LinkExpanding' in user_agent):
        return flask.jsonify({"error": "Unsupported User Agent."}), 400

    if not re.match(r"^https://training.galaxyproject.org/training-material/", url):
        return flask.jsonify({"error": "Invalid url parameter provided."}), 400

    if url is None:
        return flask.jsonify({"error": "No url parameter provided."}), 400

    gtn_data = requests.get(url)
    if gtn_data.status_code != 200:
        return flask.jsonify({"error": "Could not fetch GTN page."}), 500

    soup = BeautifulSoup(gtn_data.text, "html.parser")
    # itemprop="acceptedAnswer"
    answer = soup.find("div", {"itemprop": "acceptedAnswer"})
    # Find the col-md-8 child
    answer = answer.find("div", {"class": "col-md-8"})
    # get the page <title>
    answer_title = soup.find("title").text
    og_desc = soup.find("meta", {"property": "og:description"})["content"]

    # Find ALL of the DC.creator entries
    creators = ", ".join(
        [
            creator.attrs["content"]
            for creator in soup.find_all("meta", {"name": "DC.creator"})
        ]
    )

    # Need to rewrite every A
    for a in answer.find_all("a"):
        if a["href"].startswith("/"):
            a["href"] = GTN_URL + a["href"]
        elif a["href"].startswith("#"):
            a["href"] = url + a["href"]
        elif a["href"].startswith(".."):
            print(f"Found a relative path, {url} - {a['href']}")
        elif a["href"].startswith("http"):
            pass

        # Add some tracking, why not
        a["href"] = (
            a["href"] + "?utm_source=galaxy-help&utm_medium=oembed&utm_campaign=oembed"
        )
        # Open in a new tab?
        a["target"] = "_blank"

    # Need to rewrite every IMG
    for img in answer.find_all("img"):
        if img["src"].startswith("/"):
            img["src"] = GTN_URL + img["src"]
        elif img["src"].startswith(".."):
            print(f"Found a relative path, {url} - {img['src']}")
        elif img["src"].startswith("http"):
            pass

        # Set style max-width: 100%
        if "style" in img:
            img["style"] = img["style"] + "; max-width: 100%;"
        else:
            img["style"] = "max-width: 100%;"

    data = {
        "author_name": creators,
        "author_url": "https://galaxy.training",
        "description": og_desc,
        "html": f"""
            <section style="border: 1px solid #2c3143; box-shadow: 5px 6px #b2b2b2;margin:1rem 0;">
            <div style="border-bottom: 3px solid #2c3143; padding:0.8rem;display: flex; justify-content: space-between; align-items: center;">
                <span>
                    Content from
                    <a href="{url}?utm_source=galaxy-help&utm_medium=oembed&utm_campaign=oembed">{answer_title}</a>
                </span>
                <span>
                    <img src="https://training.galaxyproject.org/training-material/assets/images/GTN-60px.png" style="height: 30px; width: 30px;" alt="Galaxy Training Network logo"> <a href="https://training.galaxyproject.org/training-material/?utm_source=galaxy-help&utm_medium=oembed&utm_campaign=oembed">Galaxy Training!</a>
                </span>
            </div>
            <div style="padding: 0.8rem;">
            {answer}
            </div>
            <iframe width="1" height="1" sandbox="allow-same-origin allow-scripts" title="min" src="https://training.galaxyproject.org/" frameborder="0" allowfullscreen></iframe></section>
        """,
        "width": 560,
        "height": 1,
        "provider_name": "Galaxy Training Network (GTN)",
        "provider_url": "https://galaxy.training",
        "title": answer_title,
        "type": "video",
        "version": "1.0",
    }
    return flask.jsonify(data)


if __name__ == "__main__":
    app.run()
