import threading
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
from flask_mail import Message
from threading import Thread


import os
basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
manager = Manager(app)
app.config["SECRET_KEY"] = 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'appdata.sqlite')

app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <khassal.test@gmail.com>'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')

# qivtbtffdkjrrhqx
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
migrate = Migrate(app, db)
#manager.add_command('db', MigrateCommand)


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template+'.txt', **kwargs)
    msg.html = render_template(template+'.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    mail.send(msg)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


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
