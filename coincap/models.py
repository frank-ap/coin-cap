from coincap import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    #posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Listings(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    percent_change_24h = db.Column(db.Float(), unique=True, nullable=False)
    percent_change_7d = db.Column(db.Float(), nullable=False)
    percent_change_30d = db.Column(db.Float(), nullable=False)
    percent_change_90d = db.Column(db.Float(), nullable=False)
    price = db.Column(db.Float(), nullable=False)
    date = db.Column(db.Date(), nullable=False)

    def __repr__(self):
        return f"Listings('{self.name}')"

class Alerts(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    crypto1 = db.Column(db.String(50), nullable=False)
    crypto2 = db.Column(db.String(50), nullable=True)
    crypto3 = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    alert_dt = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f"Listings('{self.name}')"
