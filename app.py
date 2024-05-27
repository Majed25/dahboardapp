import os
from dashboard import dashboard
from flask import (Flask, Markup, redirect, render_template, request,
                   send_from_directory, url_for, jsonify)
from flask_caching import Cache

# Initializing my Flask app
app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Generating
@app.route('/')
@cache.cached(timeout=3600*4)
def index():
    print("Cache Missed: serving from file")
    with open('index.html', 'r') as f:
        content = f.read()
    return Markup(content)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    dashboard()
    app.run(debug=True, host='0.0.0.0', port=5000)

