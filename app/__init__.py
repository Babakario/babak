import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import requests
import random
import string
from app.services.telegram_service import send_telegram_message
# TelegramUser is already imported further down, which is fine.

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Placeholder for config
    app.config['SECRET_KEY'] = 'your_secret_key_should_be_changed' # Changed secret key
    app.config['BOT_TOKEN'] = os.environ.get('BOT_TOKEN')
    app.config['BOT_ID'] = os.environ.get('BOT_ID')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .models.telegram_user import TelegramUser

    with app.app_context():
        db.create_all()

    # Register blueprints if we decide to use them
    # from .routes import main as main_blueprint
    # app.register_blueprint(main_blueprint)

    @app.route('/')
    def home(): # Renamed from hello to home for clarity
        # This route now renders the placeholder HTML page
        return render_template('index.html')

    @app.route('/init_telegram_webhook')
    def init_telegram_webhook():
        bot_token = app.config.get('BOT_TOKEN')
        if not bot_token:
            return jsonify({"error": "BOT_TOKEN not configured"}), 500

        # Construct webhook_url, attempting to use https for development
        # A more robust solution for production might involve a configured BASE_URL
        webhook_base_url = request.url_root
        if webhook_base_url.startswith('http://'):
            webhook_base_url = webhook_base_url.replace('http://', 'https://', 1)
        webhook_url = webhook_base_url + 'telegram_webhook'

        api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}"

        try:
            response = requests.get(api_url, timeout=10)
            if response.ok:
                return jsonify(response.json())
            else:
                return jsonify({
                    "error": "Failed to set webhook",
                    "status_code": response.status_code,
                    "telegram_response": response.text
                }), response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"RequestException during webhook setup: {str(e)}"}), 500
        except Exception as e:
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

    @app.route('/telegram_webhook', methods=['POST'])
    def telegram_webhook():
        data = request.get_json()
        bot_token = app.config.get('BOT_TOKEN')
        bot_id = app.config.get('BOT_ID')

        if not bot_token or not bot_id:
            # This case should ideally not happen if webhook setup was successful
            # and config is correctly loaded.
            return jsonify(status="error", message="BOT_TOKEN or BOT_ID not configured"), 500

        try:
            if not data or 'message' not in data:
                return jsonify(status="ok", message="No message field in data"), 200

            message = data.get('message', {})
            chat_id = message.get('chat', {}).get('id')
            text = message.get('text')

            if not chat_id or not text:
                # Acknowledge non-text messages or messages without chat_id to Telegram
                return jsonify(status="ok", message="Missing chat_id or text"), 200

            chat_id = str(chat_id) # Ensure chat_id is a string for db consistency

            # Handle /start command (no parameters)
            if text == "/start":
                try:
                    rkey = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                    user = TelegramUser.query.filter_by(telegram_user_id=chat_id).first()
                    if user:
                        user.rkey = rkey
                        user.target_user_id = None # Reset target_user_id if they /start again
                    else:
                        user = TelegramUser(telegram_user_id=chat_id, rkey=rkey)

                    db.session.add(user)
                    db.session.commit()

                    link = f"https://t.me/{bot_id}?start={rkey}"
                    msg = f"👋 سلام! این لینک مخصوص تو هست:\n\nباهاش می‌تونی پیام ناشناس دریافت کنی:\n{link}"
                    send_telegram_message(bot_token, chat_id, msg)
                    return jsonify(status="Started")
                except SQLAlchemyError as e:
                    db.session.rollback()
                    # Consider logging the error e
                    send_telegram_message(bot_token, chat_id, "⚠️ یه مشکلی پیش اومد. دوباره سعی کن.")
                    return jsonify(status="Database error during /start"), 500

            # Handle /start <rkey> command
            elif text.startswith("/start "):
                parts = text.split(" ", 1)
                if len(parts) < 2 or not parts[1].strip():
                    send_telegram_message(bot_token, chat_id, "❌ کلید rkey خالی است. لطفا لینک را کامل کپی کنید.")
                    return jsonify(status="Empty rkey")

                rkey = parts[1].strip()

                try:
                    owner_user = TelegramUser.query.filter_by(rkey=rkey).first()
                    if not owner_user:
                        send_telegram_message(bot_token, chat_id, "❌ لینک معتبر نیست.")
                        return jsonify(status="Invalid rkey")

                    if owner_user.telegram_user_id == chat_id:
                        send_telegram_message(bot_token, chat_id, "🤔 نمی‌تونی به خودت پیام ناشناس بدی! این لینک رو به دوستات بده.")
                        return jsonify(status="Self message attempt")

                    target_user_id = owner_user.telegram_user_id
                    current_user = TelegramUser.query.filter_by(telegram_user_id=chat_id).first()
                    if current_user:
                        current_user.target_user_id = target_user_id
                        current_user.rkey = None # Clear rkey if they are now targeting someone
                    else:
                        current_user = TelegramUser(telegram_user_id=chat_id, target_user_id=target_user_id)

                    db.session.add(current_user)
                    db.session.commit()
                    send_telegram_message(bot_token, chat_id, "✉️ پیام ناشناس خودتو بفرست!")
                    return jsonify(status="Ready to send")
                except SQLAlchemyError as e:
                    db.session.rollback()
                    # Consider logging the error e
                    send_telegram_message(bot_token, chat_id, "⚠️ یه مشکلی پیش اومد. دوباره سعی کن.")
                    return jsonify(status="Database error during /start rkey"), 500

            # Handle anonymous message sending (default case)
            else:
                try:
                    sender = TelegramUser.query.filter_by(telegram_user_id=chat_id).first()
                    if not sender or not sender.target_user_id:
                        # This message implies they tried to send a message without first clicking a valid /start <rkey> link
                        send_telegram_message(bot_token, chat_id, "❗️شما ابتدا باید روی لینک یک دوست کلیک کنید تا بتوانید به او پیام دهید یا با دستور /start لینک خودتان را بسازید.")
                        return jsonify(status="No target")

                    target_chat_id = sender.target_user_id

                    # Prevent sending to self if target_user_id somehow ended up being their own id
                    if target_chat_id == chat_id:
                        send_telegram_message(bot_token, chat_id, "🤔 نمی‌تونی به خودت پیام ناشناس بدی!")
                        return jsonify(status="Self message attempt via direct message")

                    anon_msg = f"🕵️ پیام ناشناس برات اومده:\n\n{text}"

                    # Send to target and confirm to sender
                    if send_telegram_message(bot_token, target_chat_id, anon_msg):
                        send_telegram_message(bot_token, chat_id, "✅ پیام فرستاده شد!")
                        return jsonify(status="Sent")
                    else:
                        # If sending to target failed, inform sender
                        send_telegram_message(bot_token, chat_id, "⚠️ ارسال پیام با مشکل مواجه شد. ممکن است کاربر ربات را بلاک کرده باشد.")
                        return jsonify(status="Failed to send to target")
                except SQLAlchemyError as e:
                    db.session.rollback()
                    # Consider logging the error e
                    send_telegram_message(bot_token, chat_id, "⚠️ یه مشکلی در پایگاه داده پیش اومد. دوباره سعی کن.")
                    return jsonify(status="Database error during message sending"), 500

        except Exception as e:
            # Generic error handler for unexpected issues
            # Consider logging the error e
            # Avoid sending a message back via Telegram here if BOT_TOKEN might be the issue or if it's a deeper problem
            return jsonify(status="error", message=f"An unexpected error occurred: {str(e)}"), 500

        # Fallback, should ideally be covered by specific handlers
        return jsonify(status="OK"), 200

    return app
