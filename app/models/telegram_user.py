from app import db

class TelegramUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_user_id = db.Column(db.String(100), unique=True, nullable=False)
    rkey = db.Column(db.String(50), unique=True, nullable=True, index=True)
    target_user_id = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<TelegramUser {self.telegram_user_id}>'
