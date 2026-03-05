import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-altere-em-producao'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PREFERRED_URL_SCHEME = 'https'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config ):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://igreja_user:SenhaSegura123!@localhost:5433/igreja_system'

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://igreja_user:SenhaSegura123!@localhost/igreja_system'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
