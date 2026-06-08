
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuration MySQL
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'ton_mot_de_passe_mysql'
    MYSQL_DB = 'ifri_mentorlink'
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://root:ton_mot_de_passe_mysql@localhost/ifri_mentorlink'
    SQLALCHEMY_TRACK_MODIFICATIONS = False