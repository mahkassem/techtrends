from datetime import date
import datetime
import logging
import sqlite3
import sys

from flask import Flask, json, render_template, request, url_for, redirect, flash

# Function to get a database connection.
# This function connects to database with the name `database.db`

# define database connection count
connectionCount = int()


def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global connectionCount
    connectionCount += 1
    return connection

# Function to get a post using its ID


def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post

# define /metrics endpoint: metrics


def getPostsCount():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return len(posts)


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application


@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown


@app.route('/<int:post_id>')
def post(post_id):
    datetimeUtc = datetime.datetime.utcnow()
    post = get_post(post_id)
    if post is None:
        app.logger.info(
            '%s, Article with post_id: %s was not found!' % (datetimeUtc, post_id))
        return render_template('404.html'), 404
    else:
        app.logger.info(
            '%s, Article "%s" retrieved!' % (datetimeUtc, post['title']))
        return render_template('post.html', post=post)

# Define the About Us page


@app.route('/about')
def about():
    datetimeUtc = datetime.datetime.utcnow()
    app.logger.info(
        '%s, About page is retrieved!' % (datetimeUtc))
    return render_template('about.html')

# Define the post creation functionality


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()

            datetimeUtc = datetime.datetime.utcnow()
            app.logger.info(
                '%s, Article "%s" is created!' % (datetimeUtc, title))
            return redirect(url_for('index'))

    return render_template('create.html')

# define /healthz endpoint: health check


@app.route('/healthz')
def healthcheck():
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    return response

# define /metrics endpoint: metrics


@app.route('/metrics')
def metrics():
    global connectionCount
    postsCount = getPostsCount()
    response = app.response_class(
        response=json.dumps(
            {"db_connection_count": connectionCount, "post_count": postsCount}),
        status=200,
        mimetype='application/json'
    )
    return response


# start the application on port 3111
if __name__ == "__main__":
    # logs to a STDOUT, DEBUG level
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.basicConfig(stream=sys.stderr, level=logging.ERROR)
    # run the application
    app.run(host='0.0.0.0', port='3111')
