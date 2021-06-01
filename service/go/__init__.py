from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = 'secret'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://u_ecg:2021_ECG@92.242.58.173:1984/db_ecg'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
#log = LoginManager(app)

from go import models, routes

db.create_all()