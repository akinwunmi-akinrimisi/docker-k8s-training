"""
As a user of this app,
when I open the root homepage (/)
then I get a simple html page (templates/default.html)

As a user of this app,
when I open the author page (/author)
then I get the value of the AUTHOR environment variable (or "No author set" if the variable is not set")
"""

import logging
import os

from flask import Flask, render_template, render_template_string

logger = logging.getLogger()
log_level = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=log_level)
logger.setLevel(log_level)

app = Flask(__name__)


@app.route('/')
def home_page():
    logger.info("Rendering home page")

    # Return the templates/default.html template
    return render_template("default.html")


@app.route('/author')
def author_page():
    logger.info("Rendering author page")

    # The value of the AUTHOR environment variable is returned under /author
    author = os.environ.get("AUTHOR", "No author set")
    logger.debug(f"The Author is set to: {author}")
    return render_template_string(author)


if __name__ == '__main__':
    logger.info(
        "Starting Flask app. This will be available on http://localhost:9900\n"
        "PLEASE DO NOT TRY TO ACCESS BY THE URL BELOW as it will not work"
    )
    app.run(port=9900, host="0.0.0.0")
