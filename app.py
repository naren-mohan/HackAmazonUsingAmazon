import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
import pandas as pd
import sqlalchemy
import amazonReporter
from apscheduler.schedulers.background import BackgroundScheduler

def get_df(table):
    engine = sqlalchemy.create_engine('sqlite:///database.db')
    return pd.read_sql('SELECT * FROM '+ table +';', engine)

def new_item(url):
    #df_items = get_df("items")
    price = amazonReporter.new_item(url)
    print(price)
    return (price, price)

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

def get_item_prices():
    df_items = get_df("items")
    item_prices = amazonReporter.get_prices_df(df_items)
    return item_prices

def update_prices(interval=False):
    item_prices = get_item_prices()
    conn = get_db_connection()
    for item in item_prices:
        low_price_temp = conn.execute('SELECT lowprice FROM items WHERE id = ?', 
                                (item["id"], )).fetchone()[0]

        if interval:
            conn.execute("INSERT INTO items_large (id, url, curr_price) VALUES \
                        (?, ?, ?)", (item["id"], item["url"], item["cost"]))
        if item["cost"] is None or low_price_temp is None:
            conn.execute('UPDATE items SET latestprice = ? \
                            WHERE id = ?', (item["cost"], item["id"]))
        elif int(low_price_temp) > item["cost"]:
            conn.execute('UPDATE items SET latestprice = ?, lowprice = ? \
                            WHERE id = ?', (item["cost"], item["cost"], item["id"]))
        else:
            conn.execute('UPDATE items SET latestprice = ? \
                            WHERE id = ?', (item["cost"], item["id"]))

    conn.commit()
    conn.close()

app = Flask(__name__)
app.secret_key = "YtDL5cCLjEvl(8>bC/|(jm`p<~.zE7"

sched = BackgroundScheduler(timezone='EST')
sched.add_job(update_prices, 'interval', id='60_min_updater',args=[True], minutes=60)
sched.start()

@app.route('/')
def index():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)

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
            latestprice, lowprice = new_item(url)
            print(latestprice)
            conn.execute('INSERT INTO items (title, url, notes, latestprice, lowprice) VALUES (?, ?, ?, ?, ?)', 
                            (title, url, notes, latestprice, lowprice))
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


@app.route('/update_all')
def update_all():
    update_prices()
    flash('Prices refreshed!')
    return redirect('/')