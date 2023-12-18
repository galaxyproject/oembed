#!/usr/bin/env python
import tempfile
import flask
import subprocess
import os

app = flask.Flask(__name__)
TEMPLATE_CACHE = {}

# Server a / route
@app.route('/')
def index():
    return 'OK'



@app.route('/oembed')
def oembed():
    # Get url + format from url params:
    url = flask.request.args.get('url')
    fmt = flask.request.args.get('format', 'json')

    data = {
        'version': '1.0',
        'type': 'rich',
        'title': "Test Title",
        'html': f'<h1>h1</h1><h2>h2</h2><h3>h3</h3><ol><li>Test</li><li>Test</li><li>Test</li><li>Test</li><li>Test</li><li>Test</li><li>Test</li><li>Test</li><li>Test</li><li>Test</li><li>url: {url}</li></ol>',
        'width': 425,
        'height': 350,
        'author_name': 'Helena',
        'author_url': 'https://github.com/hexylena',
        'provider_name': 'GTN',
        'provider_url': 'https://galaxy.training',
    }
    # Return data as json
    return flask.jsonify(data)



# Run the app
if __name__ == '__main__':
    app.run()
