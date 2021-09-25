
from flask import Flask, render_template, redirect, url_for, session, flash
from datetime import datetime
import forms
from flask_script import Shell, Manager
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail


import os


app = Flask(__name__)
manager = Manager(app)


mail = Mail(app)

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
migrate = Migrate(app, db)
#manager.add_command('db', MigrateCommand)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command("shell", Shell(make_context=make_shell_context))


@app.route("/", methods=["GET", "POST"])
def index():

    form = forms.NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.uname.data).first()
        if user is None:
            flash('Looks like you are new')
            user = User(username=form.uname.data)
            db.session.add(user)

            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'],
                           'New User', 'mail/new_user', user=user)

        else:
            session['known'] = True
        session['name'] = form.uname.data

        form.uname.data = ''
        return redirect(url_for('index'))
    return render_template("index.html", form=form, name=session.get('name'), curent_time=datetime.utcnow(), known=session.get('known', False))


@app.route("/user/<name>")
def user(name):
    form = forms.NameForm()
    return render_template("user.html", form=form, name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


@app.route('/')
def index1():
    return redirect(url_for("user", name="abd", _external=True))


if __name__ == "__main__":
    manager.run()
