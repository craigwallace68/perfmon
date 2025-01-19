from datetime import datetime, timedelta
import sys

# Set search variables - file path (with a sorted timestamp field)
file_path = '/var/log/syslog'
field_delimeter = ','
field_index = 1
search_ts = sys.argv[1]  # Temporary test, pass in last recorded timestamp in database

# Binary search file for target timestamp
def record_search(path, delim, field, ts):

    # Initialize timestamp datatype and list for indexing
    try:
        ts = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    except ValueError as e01:
        print(f"e01: Invalid date format: {e01}")
    rows_timestamps = []

    #Open path/file
    with open(path, 'r') as f:
        line_number = 1

        # Iterate file, set row line numbers and timestamp paired together as dictionary objects stored in list
        while True:
            line = next(f, None)
            if not line:
                break
            current_line = line.split(delim)
            time_str = current_line[field]
            # Check for relevent row with timestamp prefix to process, else skip row and continue
            if time_str.startswith('timestamp='):
                time_str = time_str[10:]
                try:
                    time_record = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                except ValueError as e02:
                    print(f"e02: Invalid date format: {e02}")
                rows_timestamps.append({'line_number': line_number, 'timestamp': time_record})
                line_number += 1
            else:
                line_number += 1

    # Set records range (0 indexed)
    low_record = 0
    high_record = len(rows_timestamps) - 1

    # Initialize and set range of seconds to include for match (cover 1 minute resolution)
    ts_start = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
    ts_end = ts_start
    ts_start = ts.replace(seconds=0)  # start of search minute
    ts_end = ts_end.replace(second=59)  # end of search minute

    # Divide records, search, find and set file entry point to process db records from
    while low_record <= high_record:
        mid_list = (low_record + high_record) // 2
        if rows_timestamps[mid_list]['timestamp'] > ts:
            high_record = mid_list - 1
        elif rows_timestamps[mid_list]['timestamp'] < ts:
            low_record = mid_list + 1
        elif (
            rows_timestamps[mid_list]['timestamp'] >= ts_start
            and rows_timestamps[mid_list]['timestamp'] <= ts_end
        ):
            return mid_list
        else:
            # This should not happen if the timestamps are sorted correctly
            raise ValueError("Timestamps are not in order, at 1 minute interval, or not in range")
    # Timestamp was not found
    return None


# Main
#db_insert

record_search(file_path, field_delimeter, field_index, search_ts)

if __name__ == "__main__":
    record_search
