import os

class Config(object):
    APP_TITLE = 'Blog of books'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'very_secret_key!'
    API_ROOT_URL = 'http://localhost:5000/api'

    LOG_FILE_NAME = 'logs/app.log'
    LOG_MAX_SIZE = 10240000
    LOG_BACKUP_COUNT = 10
    
