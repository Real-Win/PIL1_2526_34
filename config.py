import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuration MySQL
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'Christ'
    MYSQL_DB = 'ifri_mentorlink'
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Christ@localhost/ifri_mentorlink'
    SQLALCHEMY_TRACK_MODIFICATIONS = False