from flask import Flask
from routes import bp as main_bp
from db import init_db

app = Flask(__name__)

# Registrar o Blueprint
app.register_blueprint(main_bp)



if __name__ == '__main__':
    init_db()
    app.run(debug=True)
