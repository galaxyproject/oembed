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


def generate_embed(url, response_type=False, css=False):
    gtn_data = requests.get(url)
    if gtn_data.status_code != 200:
        return flask.jsonify({"error": "Could not fetch GTN page."}), 500

    soup = BeautifulSoup(gtn_data.text, "html.parser")
    if '/faqs/' in url:
        # itemprop="acceptedAnswer"
        answer = soup.find("div", {"itemprop": "acceptedAnswer"})
        # Find the col-md-8 child
        answer = answer.find("div", {"class": "col-md-8"})
    else:
        answer = soup.find("div", {"class": "main-content"})

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
            a["href"] = '/'.join(url.split('/')[0:-1]) + '/' + a["href"]
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
            img["src"] = '/'.join(url.split('/')[0:-1]) + '/' + img["src"]
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
        "width": 560,
        "height": 1,
        "provider_name": "Galaxy Training Network (GTN)",
        "provider_url": "https://galaxy.training",
        "title": answer_title,
        "type": "video",
        "version": "1.0",
    }

    if response_type == "iframe":
        data["html"] = f'<iframe width="560" height="400" scrolling="yes" sandbox="allow-same-origin allow-scripts" title="{answer_title}" src="{url}?utm_source=galaxy-help&utm_medium=oembed&utm_campaign=oembed" frameborder="0" allowfullscreen></iframe>'
        data['height'] = 400
        data['thumbnail_url'] = "https://training.galaxyproject.org/training-material/assets/images/GTNLogo1000.png"
        data['thumbnail_width'] = 560
        data['thumbnail_height'] = 400
    else:
        data["html"] =  f"""
            <style>
            a[target="_blank"]::after { '{' }content: "" !important; { '}' }
            </style>
            <section style="border: 1px solid #2c3143; box-shadow: 5px 6px #b2b2b2;margin:1rem 0;">
            <div style="border-bottom: 3px solid #2c3143; padding:0.8rem;display: flex; justify-content: space-between; align-items: center;">
                <span>
                    Content from
                    <a href="{url}?utm_source=galaxy-help&utm_medium=oembed&utm_campaign=oembed">{answer_title}</a>
                </span>
                <span>
                    <a href="https://training.galaxyproject.org/training-material/?utm_source=galaxy-help&utm_medium=oembed&utm_campaign=oembed">
                        <img src="https://training.galaxyproject.org/training-material/assets/images/GTN-60px.png" style="height: 30px; width: 30px;" alt="GTN logo">
                    </a>
                </span>
            </div>
            <div style="padding: 0.8rem;">
            {answer}
            </div>
            <iframe width="1" height="1" sandbox="allow-same-origin allow-scripts" title="min" src="https://training.galaxyproject.org/" frameborder="0" allowfullscreen></iframe></section>
        """

    if response_type == "iframe-embed":
        if css:
            return "<html><link rel=\"stylesheet\" href=\"https://training.galaxyproject.org/training-material/assets/css/main.css\"><body>" + data['html'] + "</body></html>"
        else:
            return "<html><body>" + data['html'] + "</body></html>"

    return data


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

    if not re.match(r"^https://training.galaxyproject.org/training-material/", url):
        return flask.jsonify({"error": "Invalid url parameter provided, only the GTN is supported."}), 400

    if url is None:
        return flask.jsonify({"error": "No url parameter provided."}), 400

    # NON STANDARD
    css = flask.request.args.get("style", "")

    # NON STANDARD RESPONSE.
    if fmt == "iframe-embed":
        return generate_embed(url, response_type="iframe-embed", css=css.lower() == "gtn")

    # Currently we're targetting two platforms: slack and discourse.
    # Mastodon is showing it as a video which is hilarious and not helpful.
    if ('Discourse Forum Onebox' in user_agent or 'Slackbot-LinkExpanding' in user_agent):
        data = generate_embed(url)
        return flask.jsonify(data)
    elif 'Mastodon' in user_agent:
        data = generate_embed(url, response_type="iframe")
        return flask.jsonify(data)
    else:
        data = generate_embed(url, response_type="iframe")
        return flask.jsonify(data)

    return flask.jsonify({"error": "Unsupported User Agent."}), 400



if __name__ == "__main__":
    app.run()
