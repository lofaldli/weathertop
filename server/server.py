#!/usr/bin/env python2
import os
from datetime import datetime as dt
from flask import Flask, render_template, request, make_response, abort
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    SQLALCHEMY_DATABASE_URI='sqlite:///' +
                            os.path.join(app.root_path, 'weathertop.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False
))

db = SQLAlchemy(app)
api = Api(app)


def central_moving_average(data, M, N=10):
    sum = 0
    n = 0

    for i in range(max(0, M-N), min(len(data), M+N)):
        sum += data[i]['temperature']
        n += 1

    return 1.0 * sum / n


class RESTData(Resource):
    def get(self):
        '''
        calculate CMA on the fly (!) and return list of time/temp objects
        '''
        data = [d.to_dict() for d in Data.query.all()]

        cma_data = []
        for M in range(len(data)):
            cma_data.append({
                'timestamp': data[M]['timestamp'],
                'temperature': central_moving_average(data, M)
            })
        return cma_data

    def post(self):
        try:
            data = request.get_json()
            db.session.add(Data(data['temperature']))
            db.session.commit()
            return make_response('OK')
        except Exception, e:
            app.logger.error(e)
            return abort(400)


api.add_resource(RESTData, '/data')


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
        # data = map(lambda d: d.to_dict(), Data.query.all())
        # return render_template('plot.html', data=data)
        return render_template('plot.html')
    except Exception, e:
        app.logger.error(e)
        return abort(500)


if __name__ == '__main__':
    print "use 'flask run' instead"
    # app.run(debug=True)
