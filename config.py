
import os


class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql://root:1234@localhost:3307/monitor7'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24).hex()
