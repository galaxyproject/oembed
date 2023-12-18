#!/usr/bin/env python
import re
import requests
from bs4 import BeautifulSoup
import flask
import os

app = flask.Flask(__name__)
GTN_URL = "https://training.galaxyproject.org/"


# Server a / route
@app.route("/")
def index():
    return "OK"


@app.route("/index.html")
def home():
    with open("index.html") as f:
        return f.read()


@app.route("/oembed")
def oembed():
    # Get url + format from url params:
    url = flask.request.args.get("url")
    fmt = flask.request.args.get("format", "json")

    if not re.match(r"^https://training.galaxyproject.org/training-material/", url):
        return flask.jsonify({"error": "Invalid url parameter provided."})

    if url is None:
        return flask.jsonify({"error": "No url parameter provided."})

    gtn_data = requests.get(url)
    if gtn_data.status_code != 200:
        return flask.jsonify({"error": "Could not fetch GTN page."})

    soup = BeautifulSoup(gtn_data.text, "html.parser")
    # itemprop="acceptedAnswer"
    answer = soup.find("div", {"itemprop": "acceptedAnswer"})
    # Find the col-md-8 child
    answer = answer.find("div", {"class": "col-md-8"})
    # get the page <title>
    answer_title = soup.find("title").text

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
        a["href"] = a["href"] + "?utm_source=galaxy-help&utm_medium=oembed&utm_campaign=oembed"
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
        if 'style' in img:
            img['style'] = img['style'] + "; max-width: 100%;"
        else:
            img['style'] = "max-width: 100%;"


    data = {
        "author_name": "Galaxy Training Network",
        "author_url": "https://galaxy.training",
        "description": "GTN FAQ Entry",
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
        "provider_name": "GTN",
        "provider_url": "https://galaxy.training",
        "title": "Test Title",
        "type": "video",
        "version": "1.0",
    }
    return flask.jsonify(data)


if __name__ == "__main__":
    app.run()
