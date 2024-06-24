from dotenv import load_dotenv
from flask import Flask
from routes.collab import collab_blueprint
from routes.content_base import ContentBase

load_dotenv()

def _register_blueprints(app: Flask):
    app.register_blueprint(collab_blueprint, url_prefix = collab_blueprint.url_prefix)
    app.register_blueprint(ContentBase)

def create_app() -> Flask:
    app = Flask(__name__)
    _register_blueprints(app)

    if __name__ == '__main__':
        app.run(debug=True)
    return app

app = create_app()

