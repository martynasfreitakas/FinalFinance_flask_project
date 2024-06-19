from flask import Flask
from config import Config
from routes import my_routes
from database import my_db

app = Flask(__name__)
app.config.from_object(Config)

with app.app_context():
    my_db(app)
    my_routes(app)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
