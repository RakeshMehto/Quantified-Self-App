from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'Login_db'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    trackers = db.relationship("Tracker", cascade="delete")

    def get_id(self):
        return self.user_id


class Tracker(db.Model):
    __tablename__ = 'Tracker'
    tracker_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("Login_db.user_id"),
                        nullable=False)
    tracker_name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    t_type = db.Column(db.String, nullable=False)
    logs = db.relationship('Log', cascade="delete")
    settings = db.relationship('Setting', uselist=False, cascade="delete")


class Log(db.Model):
    __tablename__ = 'Logger'
    logger_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    tracker_id = db.Column(db.Integer, db.ForeignKey("Tracker.tracker_id"),
                           nullable=False)
    t_value = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.String)
    timestamp = db.Column(db.String,
                          default=datetime.now().strftime("%Y-%m-%d %H:%M"))


class Setting(db.Model):
    __tablename__ = 'MCQ'
    tracker_id = db.Column(db.Integer, db.ForeignKey("Tracker.tracker_id"),
                           nullable=False, primary_key=True)
    options = db.Column(db.String, nullable=False)
