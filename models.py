from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class Sequence(db.Model):
    __tablename__ = 'sequences'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    answers = db.Column(db.Text, nullable=False)
    
    def set_answers(self, answers):
        self.answers = json.dumps(answers)

