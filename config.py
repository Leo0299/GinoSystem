class Config:
    SECRET_KEY = 'mysecretkey'

class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '12345'
    MYSQL_DB = 'process'


config = {
    'development':DevelopmentConfig
}