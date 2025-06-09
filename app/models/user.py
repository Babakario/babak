# Placeholder for User model (e.g., using SQLAlchemy)
# from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy()

class User: # db.Model
    # id = db.Column(db.Integer, primary_key=True)
    # username = db.Column(db.String(80), unique=True, nullable=False)
    # instagram_user_id = db.Column(db.String(120), unique=True, nullable=True)
    # access_token = db.Column(db.String(255), nullable=True) # For Instagram API

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return f'<User {self.username}>'
