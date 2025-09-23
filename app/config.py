import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "supersecretkey")
    SQLALCHEMY_DATABASE_URI = os.getenv("MYSQL_URI", "")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
