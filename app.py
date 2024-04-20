import os
from dashboard import dashboard
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

# Initializing my Flask app
app = Flask(__name__)

# Generating
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')  # Navigate one directory up

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    dashboard()
    app.run()

