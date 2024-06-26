import sqlite3
import logging

from flask import (
    Flask,
    jsonify,
    json,
    render_template,
    request,
    url_for,
    redirect,
    flash,
)
from werkzeug.exceptions import abort

# Global variable to track connection count
connection_count = 0

# Define the Flask application
app = Flask(__name__)
app.config["ENV"] = "development"

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    connection.close()
    return post


# Function to get the total post count from the database
def get_db_post_count():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM posts")
    post_count = cursor.fetchone()[0]
    connection.close()
    return post_count


# Define the main route of the web application
@app.route("/")
def index():
    connection = get_db_connection()
    posts = connection.execute("SELECT * FROM posts").fetchall()
    connection.close()
    return render_template("index.html", posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route("/<int:post_id>")
def post(post_id):
    post = get_post(post_id)
    if post is None:
        logging.info(f"Article with ID {post_id} not found!")
        return render_template("404.html"), 404
    else:
        logging.info(f'Article "{post.title}" retrieved!')
        return render_template("post.html", post=post)


# Define the About Us page
@app.route("/about")
def about():
    logging.info("About Us page retrieved!")
    return render_template("about.html")


# Define the post creation functionality
@app.route("/create", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title:
            flash("Title is required!")
        else:
            connection = get_db_connection()
            connection.execute(
                "INSERT INTO posts (title, content) VALUES (?, ?)", (title, content)
            )
            connection.commit()
            connection.close()

            logging.info(f'New article "{title}" created!')

            return redirect(url_for("index"))

    return render_template("create.html")


# Healthcheck endpoint
@app.route("/healthz")
def status():
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype="application/json",
    )
    app.logger.info("healthz request successfull")
    return response


# Metric endpoint
@app.route("/metrics")
def metrics():
    global connection_count
    connection_count += 1

    post_count = get_db_post_count()

    metrics_data = {"db_connection_count": connection_count, "post_count": post_count}

    response = app.response_class(
        response=json.dumps(
            {
                "status": "success",
                "code": 0,
                "data": {
                    "db_connection_count": connection_count,
                    "post_count": post_count,
                },
            }
        ),
        status=200,
        mimetype="application/json",
    )
    app.logger.info("Metrics request successfull")
    return response


# start the application on port 3111
if __name__ == "__main__":

    ## stream logs to app.log file
    app.run(host="0.0.0.0", port="3111")
