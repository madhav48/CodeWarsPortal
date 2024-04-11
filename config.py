import os, random, string

class Config(object):

    DEBUG = True # According to our requirement..

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Set up the App SECRET_KEY
    SECRET_KEY  = os.getenv('SECRET_KEY', None)
    if not SECRET_KEY:
        SECRET_KEY = ''.join(random.choice( string.ascii_lowercase  ) for i in range( 32 ))    

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DB_ENGINE   = "mysql" 
    DB_USERNAME = "root"
    DB_PASS     = None
    DB_HOST     = "localhost"
    DB_PORT     = 3306
    DB_NAME     = "cw_users"


    # try to set up a Relational DBMS
    if DB_ENGINE and DB_NAME and DB_USERNAME:

        try:
            
            # Relational DBMS: PSQL, MySql
            SQLALCHEMY_DATABASE_URI = '{}://{}@{}:{}/{}'.format(         # Not using password..
                DB_ENGINE,
                DB_USERNAME,
                DB_HOST,
                DB_PORT,
                DB_NAME
            ) 

        except Exception as e:

            print('> Error: DBMS Exception: ' + str(e) )
            print('> Fallback to SQLite ')    



    # Assets Management
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')    
    





config_dict = Config