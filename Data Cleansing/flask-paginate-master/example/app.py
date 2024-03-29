
from __future__ import unicode_literals
import sqlite3
from flask import Flask, render_template, g, current_app
from flask_paginate import Pagination, get_page_args
import click
from flask_sqlalchemy import SQLAlchemy


click.disable_unicode_literals_warning = True

app = Flask(__name__)
app.config.from_pyfile('app.cfg')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobDB.db'
db = SQLAlchemy(app)


class Job(db.Model):
    Job_ID = db.Column(db.Integer, primary_key=True)
    Date_Added = db.Column(db.String(20))
    Country_Code = db.Column(db.String(10))
    Job_Board = db.Column(db.String(20))
    Job_Description = db.Column(db.String(254))
    Job_Title = db.Column(db.String(254))
    Job_Type = db.Column(db.String(254))
    City = db.Column(db.String(50))
    State = db.Column(db.String(10))
    Location = db.Column(db.String(50))
    Organization = db.Column(db.String(254))
    Page_URL = db.Column(db.String(254))
    Sector = db.Column(db.String(254))

    def __repr__(self):
        return '<Job %r>' % self.Job_ID


@app.before_request
def before_request():
    g.conn = sqlite3.connect('jobDB.db')
    g.conn.row_factory = sqlite3.Row
    g.cur = g.conn.cursor()


@app.teardown_request
def teardown(error):
    if hasattr(g, 'conn'):
        g.conn.close()


@app.route('/')
def index():
    total = Job.query.count()

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    sql = 'select * from job order by Job_ID limit {}, {}'\
        .format(offset, per_page)
    g.cur.execute(sql)
    jobs = g.cur.fetchall()

    pagination = get_pagination(page=page,
                                per_page=per_page,
                                total=total,
                                record_name='jobs',
                                format_total=True,
                                format_number=True,
                                )
    return render_template('../../../flask_app/dashboard.html',
                           jobs=jobs,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           )


@app.route('/jobs/', defaults={'page': 1})
@app.route('/jobs', defaults={'page': 1})
@app.route('/jobs/page/<int:page>/')
@app.route('/jobs/page/<int:page>')
def jobs(page):
    g.cur.execute('select * from job')
    total = g.cur.fetchone()[0]
    page, per_page, offset = get_page_args()
    sql = 'select * from job order by Job_ID limit {}, {}'\
        .format(offset, per_page)
    g.cur.execute(sql)
    jobs = g.cur.fetchall()
    pagination = get_pagination(page=page,
                                per_page=per_page,
                                total=total,
                                record_name='jobs',
                                format_total=True,
                                format_number=True,
                                )
    return render_template('../../../flask_app/dashboard.html', jobs=jobs,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           active_url='users-page-url',
                           )


# @app.route('/search/<name>/')
# @app.route('/search/<name>')
# def search(name):
#     """The function is used to test multi values url."""
#     sql = 'select count(*) from users where name like ?'
#     args = ('%{}%'.format(name), )
#     g.cur.execute(sql, args)
#     total = g.cur.fetchone()[0]

#     page, per_page, offset = get_page_args()
#     sql = 'select * from users where name like ? limit {}, {}'
#     g.cur.execute(sql.format(offset, per_page), args)
#     users = g.cur.fetchall()
#     pagination = get_pagination(page=page,
#                                 per_page=per_page,
#                                 total=total,
#                                 record_name='users',
#                                 )
#     return render_template('index.html', users=users,
#                            page=page,
#                            per_page=per_page,
#                            pagination=pagination,
#                            )


def get_css_framework():
    return current_app.config.get('CSS_FRAMEWORK', 'bootstrap4')


def get_link_size():
    return current_app.config.get('LINK_SIZE', 'sm')


def get_alignment():
    return current_app.config.get('LINK_ALIGNMENT', '')


def show_single_page_or_not():
    return current_app.config.get('SHOW_SINGLE_PAGE', False)


def get_pagination(**kwargs):
    kwargs.setdefault('record_name', 'records')
    return Pagination(css_framework=get_css_framework(),
                      link_size=get_link_size(),
                      alignment=get_alignment(),
                      show_single_page=show_single_page_or_not(),
                      **kwargs
                      )


@click.command()
@click.option('--port', '-p', default=5001, help='listening port')
def run(port):
    app.run(debug=True, port=port)

if __name__ == '__main__':
    run()
