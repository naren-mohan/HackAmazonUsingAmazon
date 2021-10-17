import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
import pandas as pd
import sqlalchemy

def get_df(table):
    engine = sqlalchemy.create_engine('sqlite3:/database_db')
    return pd.read_sql('SELECT * FROM'+ table +';', engine)


def new_item(pid, title, url, notes):
    df_items = get_df("items")
    


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM items WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

app = Flask(__name__)
app.config['SECRET_KEY'] = '1EBCaUip1DuoJYH03t97H22aPGeLMe1u'

@app.route('/')
def index():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post = post)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        url = request.form['url']
        notes = request.form['notes']
        # print(url)
        if not title:
            flash('Title is required!')
        if not url:
            flash('URL is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO items (title, url, notes) VALUES (?, ?, ?)',
                         (title, url, notes))
            pid = conn.execute('SELECT id FROM items WHERE title = (?)', title)
            latestprice, lowprice = new_item(pid, title, url, notes)
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        url = request.form['url']
        notes = request.form['notes']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE items SET title = ?, notes = ?'
                         ' WHERE id = ?',
                         (title, notes, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM items WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/clear')
def clear():
    conn = get_db_connection()
    conn.execute('DELETE FROM items')
    conn.commit()
    conn.close()
    flash('All the items were successfully deleted!')
    return render_template('index.html')
