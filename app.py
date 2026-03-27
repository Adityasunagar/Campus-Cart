from flask import Flask
from config import SECRET_KEY
from utils.db import init_db, close_db
from routes import register_blueprints

app = Flask(__name__, template_folder='template', static_folder='static')
app.config.from_mapping(SECRET_KEY=SECRET_KEY)

register_blueprints(app)
app.teardown_appcontext(close_db)

with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
