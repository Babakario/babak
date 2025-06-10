from flask import Flask, render_template

def create_app():
    app = Flask(__name__)

    # Placeholder for config
    app.config['SECRET_KEY'] = 'your_secret_key_should_be_changed' # Changed secret key

    # Register blueprints if we decide to use them
    # from .routes import main as main_blueprint
    # app.register_blueprint(main_blueprint)

    @app.route('/')
    def home(): # Renamed from hello to home for clarity
        # This route now renders the placeholder HTML page
        return render_template('index.html')

    return app
