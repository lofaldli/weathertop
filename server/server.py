import sqlite3
import os
from datetime import datetime as dt
from flask import Flask, render_template, g, redirect, url_for, request, make_response

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'weathertop.db')
))


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    init_db()
    print 'initialized the database'


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def get_data():
    db = get_db()
    cur = db.execute(
        'select timestamp, temperature from entries order by id asc'
    )
    entries = cur.fetchall()
    data = map(lambda e: {'timestamp': e[0], 'temperature': e[1]}, entries)

    return data


@app.route('/')
def root():
    return render_template('plot.html', data=get_data())


@app.route('/add', methods=['POST'])
def add():
    try:
        timestamp = request.form['timestamp']
        temperature = request.form['temperature']

        db = get_db()
        db.execute('insert into entries (timestamp, temperature) values (?, ?)',
                   [timestamp, temperature])
        db.commit()
        return make_response('OK')
    except:
        return make_response(400)


if __name__ == '__main__':
    app.run(debug=True)
