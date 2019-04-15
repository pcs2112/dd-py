import mysql.connector as mysql
from .config import get_config

config = get_config()
db_connections = {}


def get_db_connection(db_conn):
    """ Returns the DB connection for the specified db connection name. """
    db_conn = db_conn.upper()
    
    if db_conn != 'CORE' and db_conn != 'PROFILE':
        raise Exception(f'{db_conn} is an invalid connection. CORE and PROFILE are valid connections.')
    
    if db_conn not in db_connections:
        try:
            conn = mysql.connect(
                host=config[f'{db_conn}_DB_HOST'],
                user=config[f'{db_conn}_DB_USER'],
                passwd=config[f'{db_conn}_DB_PASSWORD'],
                database=config[f'{db_conn}_DB_NAME']
            )
            
            db_connections[db_conn] = conn
        except Exception as e:
            print("Error while connecting to MySQL", e)
            raise e
    
    return db_connections[db_conn]


def close_db_connections():
    """ Closes all active db connections. """
    for db_conn in db_connections:
        db_connections[db_conn].close()
