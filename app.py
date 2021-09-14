import json

from flask import Flask, request

from _data.data_helper import DataHelper

app = Flask(__name__)


@app.route("/api/winner", methods=["GET"])
def index():
    """
    /api/winner endpoint
    url query can accept criteria:

    &level=

    with values "state" or "local", otherwise returns integrated view
    of state and local primary winners

    TODO
    Ran out of time to figure out how to properly format displayed JSON
    """

    params = request.args
    endpoint_display_name = "/api/winner"

    # conditional logic to display content filters
    if params and "level" in params:
        endpoint_display_name += f"?level={params['level']}"

    # data helper function contains more involved logic for filtering winners
    try:
        election_data = {
            "statusCode": 200,
            "status": "OK",
            "data": DataHelper(
                params, "./_data/data.json"
            ).get_filtered_election_data(),
        }
    except Exception as e:
        election_data = {
            "statusCode": 500,
            "status": "Internal server error",
        }

    # interpolates JSON to basic HTML skeleton for API styling
    return f"""
    <!DOCTYPE html>
    <html>
        <head>
            <link rel="stylesheet" href="https://unpkg.com/wingcss"/>
            <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/highlight.js/11.2.0/styles/default.min.css">
            <script src="//cdnjs.cloudflare.com/ajax/libs/highlight.js/11.2.0/highlight.min.js"></script>
        </head>
        <body style="margin:10%">
            <h3>{endpoint_display_name}</h3>
                <pre>
                    <code class="prettyprint" id="json" style="white-space: pre-line;"></code>
                </pre>
        </body>
        <script>
          document.getElementById('json').textContent = JSON.stringify({election_data});
          hljs.highlightAll();
        </script>
    </html>
    """
