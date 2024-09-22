from flask import Flask
from flask_login import LoginManager
import pymysql

app = Flask(__name__)
app.secret_key = 'SUPERSEGREDO'  

login_manager = LoginManager(app)
login_manager.login_view = 'login'  

def get_db_connection():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='hotel_campus_db',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

from app.models import User  

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

from app import routes
from app import models
