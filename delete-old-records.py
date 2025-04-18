# Script that rotates old SQL records ('keepdays' variable) in order to keep only a rollind x number of days

import psycopg2
import configparser
import os
from datetime import datetime, timedelta
import logging

# Set paths
path = '/home/nx2/perfmon_scripts'
db_config_file = '/home/nx2/perfmon_scripts/config.ini'

# Set retension number of days
keepdays = 30

# Suggested crontab entry to run this cleanup script
# 10 2 * * * python3 /home/nx2/perfmon_scripts/delete-old-records.py



os.chdir(path)

def setup_logging():
    logger = logging.getLogger()

    # Create a handler that writes log messages to a file
    file_handler = logging.FileHandler('/var/log/nx2-perfmon.log')

    # Include 'as current time' and log message into log format
    formatter = logging.Formatter('%(asctime)s - nx2-perfmon: %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)

# Set os file_path from test function
def file_exists(file_path):
    return os.path.exists(file_path)

# Test if file is present
def db_config_exists(db_config_file):
    if file_exists(db_config_file):
        logging.info("config.ini file exists")
    else:
        logging.error("unable to locate config.ini file")

# Get config.ini file parameters
def get_db_params():
    logging.info("get_db_params start")
    
    config = configparser.ConfigParser()
    try:
        config.read('config.ini')

        db_params = {
            'dbname': config['database']['dbname'],
            'user': config['database']['user'],
            'password': config['database']['password'],
            'host': config['database']['host'],
            'port': config['database']['port']
        }
        filter_params = {key:value for key, value in db_params.items() if key != 'password'}
        logging.info(', '.join(f"{key}: {value}" for key, value in filter_params.items()))
    except Exception as e:
        logging.error(f"get_db_params result: An error occurred: {e}")
        raise
    else:
        logging.info("get_db_params result: Success")

    return db_params

def delete_old_records(db_params):
    connection = None
    cursor = None

    try:
        # Open DB Connection
        logging.info("open db connection start")

        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        logging.info("open db connection result: Success")

        # Set old_date
        logging.info("set old_date start")

        old_date = datetime.now() - timedelta(days=keepdays)

        logging.info(f"set old_date result: {old_date}")

        # Execute the query
        logging.info("execute delete query start")

        delete_query = "DELETE FROM perfmon WHERE time_stamp < %s;"
        cursor.execute(delete_query, (old_date,))

        connection.commit()

        logging.info("execute delete query result: Success")

    except Exception as e:
        logging.error(f"An error occurred during record deletion: {e}")

    finally:
        if connection:
            try:
                # Close Cursor
                logging.info("close cursor start")

                cursor.close()

                logging.info("close cursor result: Success")

                # Close Connection
                logging.info("close db connection start")

                connection.close()

                logging.info("close db connection result: Success")

            except Exception as e:
                logging.error(f"An error occurred while closing resources: {e}")

def main():
    # Test for config.ini file
    db_config_exists(db_config_file)
    
    try:
        db_params = get_db_params()
        delete_old_records(db_params)
    except Exception as e:
        logging.error(f"main execution failed: {e}")

if __name__ == "__main__":
    setup_logging()  # Initialize logging to a file
    main()
