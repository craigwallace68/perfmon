from datetime import datetime
import sys

# Set search variables - file path (with a sorted timestamp field)
file_path = '/var/log/syslog'
field_delimeter = ','
field_index = 1
search_ts = sys.argv[1]  # Temporary test, pass in last recorded timestamp in database

# Binary search file for target timestamp
def record_search(path, delim, field, ts):
    # Initialize list for indexing
    rows_timestamps = []

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
                except ValueError as e01:
                    print(f"Invalid date format: {e01}")
                rows_timestamps.append({'line_number': line_number, 'timestamp': time_record})
                line_number += 1
            else:
                line_number += 1

    # Set records lines range (0 indexed)
    low = 0
    high = len(rows_timestamps) - 1

    # Divide records, search, find and set file entry point to process db records from
    while low <= high:
        mid_record = (low + high) // 2
        if rows_timestamps[mid_record]['timestamp'] > ts:
            high = mid_record - 1
        elif rows_timestamps[mid_record]['timestamp'] < ts:
            low = mid_record + 1
        elif rows_timestamps[mid_record]['timestamp'] == ts:
            return mid_record
        else:
            # This should not happen if the timestamps are sorted correctly
            raise ValueError("Timestamps are not in order, or not in range")
    # Timestamp was not found
    return None


# Main
#db_insert

record_search(file_path, field_delimeter, field_index, search_ts)

if __name__ == "__main__":
    record_search