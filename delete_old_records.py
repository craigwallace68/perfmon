import psycopg2
import configparser
from datetime import datetime, timedelta

# Add a crontab setting to run this file every day (0 12 * * * python3 /home/nx2/perfmon_scripts/delete_old_records.py)

# Read database config from file
config = configparser.ConfigParser()
config.read('config.ini')


def get_db_params():
    db_params = {
    'dbname': config['database']['dbname'],
    'user': config['database']['user'],
    'password': config['database']['password'],
    'host': config['database']['host'],
    'port': config['database']['port']
}
    return db_params


def delete_old_records(db_params):
# Connect to the database
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        # Query to delete older records
        delete_query = "DELETE FROM perfmon WHERE time_stamp < %s;"

        # Calculate the cutoff date (e.g., 30 days ago)
        old_date = datetime.now() - timedelta(days=60)

        # Execute the query
        cursor.execute(delete_query, (old_date))
        connection.commit()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()


def main():
    db_params = get_db_params()
    delete_old_records(db_params)


if __name__ == "__main__":
    main()
