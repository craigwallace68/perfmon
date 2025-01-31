from datetime import datetime, timedelta
import psycopg2
import configparser
import json
import re

# Set search variables - file path (with a sorted timestamp field)
file_path = '/var/log/syslog'
parsed_logfile = '/home/nx2/perfmon_scripts/parsed_logfile.json'
field_delimeter = ','
field_index = 1
# search_ts = sys.argv[1]  # Temporary test, pass in last recorded timestamp in database
prefix = 'timestamp'
mid_row = 1
start_row = 1
max_ts = None


# Get the last record timestamp from the last insert process
def get_last_db_timestamp(max_ts_str):
    # Read database config from file
    config = configparser.ConfigParser()
    config.read('config.ini')

    db_params = {
        'dbname': config['database']['dbname'],
        'user': config['database']['user'],
        'password': config['database']['password'],
        'host': config['database']['host'],
        'port': config['database']['port']
    }

    # Connect to the database
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        # Query to get the last timestamp from your table
        query_max_timestamp = "SELECT MAX(time_stamp) FROM perfmon;"
        cursor.execute(query_max_timestamp)
        result = cursor.fetchone()
        max_db_timestamp = result[0] if result[0] else None
        max_ts_str = max_db_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return max_ts_str

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()



# Binary search file for target timestamp (search_ts)
def record_search(path, delim, field, max_ts):

    # Initialize timestamp datatype and list for indexing
    try:
        ts_dt = datetime.strptime(max_ts, '%Y-%m-%d %H:%M:%S')
    except ValueError as e01:
        print(f"e01: Invalid date format: {e01}")

    rows_timestamps = []

    #Open path/file
    with open(path, 'r') as f:
        line_number = 1

        # Iterate file, set row line numbers and timestamp paired together as dictionary objects_dt stored in list
        while True:
            line = next(f, None)
            if not line:
                break

            # Check if line includes the delimeter
            if prefix in line and delim in line:
                current_line = line.split(delim)
                try:
                    time_str = current_line[field]
                except IndexError as e02:
                    print(f"e02: Line {line_number}: Field '{field}' not found. {e02}")
                    continue

                # Check for relevent row with timestamp prefix to process, else skip row and continue
                if time_str.startswith('timestamp='):
                    time_str = time_str[10:]
                    try:
                        time_record = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                    except ValueError as e03:
                        print(f"e03: Invalid date format: {e03}")
                        continue
                    # Add relevent row to list of dictionary objects
                    rows_timestamps.append({'line_number': line_number, 'timestamp': time_record})
                    line_number += 1
            else:
                line_number += 1

    # Set records range (0 indexed)
    low_record = 0
    high_record = len(rows_timestamps) - 1

    # Initialize and set range of seconds to include for match (cover 1 minute resolution)
    ts_dt_start = ts_dt
    ts_dt_end = ts_dt_start
    ts_dt_start = ts_dt.replace(second=0)  # start of search minute
    ts_dt_end = ts_dt_end.replace(second=59)  # end of search minute

    # Divide records, search, find and set file entry point to process db records from
    while low_record <= high_record:
        mid_row = (low_record + high_record) // 2
        if (
            rows_timestamps[mid_row]['timestamp'] > ts_dt_start
            and rows_timestamps[mid_row]['timestamp'] > ts_dt_end
        ):
            high_record = mid_row - 1
        elif (
            rows_timestamps[mid_row]['timestamp'] < ts_dt_start
            and rows_timestamps[mid_row]['timestamp'] < ts_dt_end
        ):
            low_record = mid_row + 1
        elif (
            rows_timestamps[mid_row]['timestamp'] >= ts_dt_start
            and rows_timestamps[mid_row]['timestamp'] <= ts_dt_end
        ):
            # Temporary for testing
            # print("list Index=", mid_row, "File Row=", rows_timestamps[mid_row]['line_number'], rows_timestamps[mid_row]['timestamp'], ts_dt, "Final")

            return rows_timestamps[mid_row]['line_number']
        else:
            # This should not happen if the timestamps are sorted correctly
            raise ValueError("Timestamps are not in order, at 1 minute interval, or not in range")


def parse_data(file_path, start_row):
    # Temporary for testing
    # print(f"Start Row is = : {start_row}")

    # Open logfile again to filter and process output format
    with open(file_path, 'r') as raw_file:
        data = []

        # Skip to start row position
        for s in range(start_row):
            next(raw_file)

        #  Begin processing at start row
        for i, line in enumerate(raw_file):
            # Filter out everything up to 'host'
            match = re.search(r'(?:^.*?)?(?=host=)', line)
            if match:
                filtered_line = re.sub(r'^(.*?)(?=host=)', '', line.strip())

            # Check if host and timestamp are present
            if re.search(r'(host|timestamp)=', line.lower()):

                # Temporary for testing
                # print(line)

                key_value_pairs = {}

                # Extract remaining key-value pairs
                for match in re.finditer(r'([^,]+)=([^,]+)', filtered_line):
                    key_value_pairs[match.group(1)] = match.group(2)

                data.append(key_value_pairs)

    # Write the JSON data to the output file
    with open(parsed_logfile, 'w') as parsed_json:
        json.dump(data, indent=4, fp=parsed_json)
    return



def insert_db_records():
    pass




# Main
#db_insert
def main():
    max_ts = get_last_db_timestamp(None)
    print(max_ts, type(max_ts))  #debug
    start_row = record_search(file_path, field_delimeter, field_index, max_ts)
    print(start_row)  # debug
    parse_data(file_path, start_row)
    print(file_path, start_row) #debug
    insert_db_records()


if __name__ == "__main__":
    main()
