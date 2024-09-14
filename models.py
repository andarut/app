from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Sequence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Integer, default=0)