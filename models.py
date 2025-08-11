from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src import listing_metrics_config

db = SQLAlchemy()

type_map = {
    'Boolean':db.Boolean,
    'Integer':db.Integer,
}

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255))
    list_price = db.Column(db.Integer)
    total_monthly_payment = db.Column(db.Integer)
    monthly_hoa = db.Column(db.Integer)
    annual_property_tax = db.Column(db.Integer)

    cost_score = db.Column(db.Integer)
    av_score = db.Column(db.Integer)
    # sp_score = db.Column(db.Integer)

    comments = db.relationship('Comment', backref='listing', lazy=True)
    for _, row in listing_metrics_config.iterrows():
        col_name = row['col']
        col_type = type_map[row['db.type']]
        vars()[col_name] = db.Column(col_type)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    user = db.relationship('User')
