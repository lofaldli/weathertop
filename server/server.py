import os
from datetime import datetime as dt
from flask import Flask, render_template, request, make_response, abort
from flask_sqlalchemy import SQLAlchemy

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    SQLALCHEMY_DATABASE_URI='sqlite:///' +
                            os.path.join(app.root_path, 'weathertop.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False
))

db = SQLAlchemy(app)


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    temperature = db.Column(db.Float)

    def __init__(self, temperature):
        self.timestamp = dt.utcnow()
        self.temperature = temperature

    def __repr__(self):
        return '<Data %s: %.2f C>' % (self.timestamp.strftime(TIME_FORMAT),
                                      self.temperature)

    def to_dict(self):
        return {'temperature': self.temperature,
                'timestamp': self.timestamp.strftime(TIME_FORMAT)}


@app.cli.command('initdb')
def initdb_command():
    app.logger.debug('initializing database')
    db.drop_all()
    db.create_all()


@app.route('/')
def root():
    try:
        data = map(lambda d: d.to_dict(), Data.query.all())
        return render_template('plot.html', data=data)
    except Exception, e:
        app.logger.error(e)
        return abort(500)


@app.route('/add', methods=['POST'])
def add():
    try:
        temperature = request.form['temperature']
        db.session.add(Data(temperature))
        db.session.commit()

        return make_response('OK')
    except Exception, e:
        app.logger.error(e)
        return abort(400)


if __name__ == '__main__':
    print "use 'flask run' instead"
    # app.run(debug=True)
