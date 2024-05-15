import datetime
import json
import sqlite3
from typing import List, Tuple, Any, Optional

from log_and_alert.log_setup import lg
from log_and_alert.restart_records_db_config import database_file_path, restart_records_table


def create_restart_table_if_not_existing(cursor: sqlite3.Cursor = None) -> None:
    """Create the restart_records_table if it doesn't already exist.

    :param cursor: sqlite3.Cursor, existing database cursor. (optional)

    :return: None
    """
    if cursor is None:  # create a cursor if not provided one
        with sqlite3.connect(database_file_path) as conn:
            cursor = conn.cursor()
            create_restart_table_if_not_existing(cursor)

    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {restart_records_table} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        restart_time TEXT,
        restart_message TEXT,
        additional_information TEXT
    )
    ''')


def record_restart(restart_error):
    """Record a restart event in the SQLite database.

    :param restart_error: Exception, the error that caused the restart.

    :return: None
    """
    restart_message = str(restart_error)
    conn = None
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(database_file_path)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        create_restart_table_if_not_existing(cursor)

        # current timestamp
        restart_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # convert to json string as sqlite doesn't want weird types
        additional_information = json.dumps(getattr(restart_error, 'additional_information', None))

        # insert the record
        cursor.execute(f'''
        INSERT INTO {restart_records_table}
        (restart_time, restart_message, additional_information)
        VALUES (?, ?, ?)
        ''', (restart_time, restart_message, additional_information))

        # Commit the transaction
        conn.commit()

    except Exception as e:
        lg.error(f"Error while recording restart event: {e}")
        raise e from restart_error
    finally:
        # Close the database connection
        if conn:
            conn.close()


def get_all_restart_records() -> List[Tuple[Any, ...]]:
    """Read and return all restart records from the SQLite database.

    :return: List of tuples, where each tuple contains a row from the error_log table.
    """
    try:
        with sqlite3.connect(database_file_path) as conn:
            cursor = conn.cursor()
            create_restart_table_if_not_existing(cursor)

            # Query to select all records from the error_log table
            cursor.execute(f'SELECT * FROM {restart_records_table} ORDER BY restart_time DESC;')
            rows = cursor.fetchall()

            return rows

    except Exception as e:
        lg.error(f"Error while reading restart logs: {e}")
        raise
    finally:
        # Close the database connection
        if conn:
            conn.close()


def get_last_restart_record() -> Optional[Tuple[Any, ...]]:
    """Read and return the last restart record entry from the SQLite database.

    :return: A tuple containing the last restart log or None if no records are present.
    """
    try:
        # Connect to the SQLite database
        with sqlite3.connect(database_file_path) as conn:
            cursor = conn.cursor()
            create_restart_table_if_not_existing(cursor)

            # query to select the last record from the error_log table
            cursor.execute(f'SELECT * FROM {restart_records_table} ORDER BY restart_time DESC LIMIT 1;')
            row = cursor.fetchone()

            return row

    except Exception as e:
        lg.error(f"Error while reading the last restart log: {e}")
        raise
    finally:
        # Close the database connection
        if conn:
            conn.close()


def get_restart_record_table_headers() -> List[str]:
    """Read and return the column headers of the restart log table.

    :return: List of strings, where each string is a column header name.
    """
    try:
        # Connect to the SQLite database
        with sqlite3.connect(database_file_path) as conn:
            cursor = conn.cursor()
            create_restart_table_if_not_existing(cursor)

            # query to get the column headers from the error_log table
            tbl_info = cursor.execute(f'PRAGMA table_info("{restart_records_table}");')
            tbl_info_fetch_happened = tbl_info.fetchall()
            column_headers = [col[1] for col in tbl_info_fetch_happened]

            return column_headers

    except Exception as e:
        lg.error(f"Error while reading the restart log headers: {e}")
        raise
    finally:
        # Close the database connection
        if conn:
            conn.close()


def print_restart_record_records():
    """Print all restart logs from the SQLite database to the console in a formatted manner.

    :return: None
    """
    try:
        rows = get_all_restart_records()
        if rows:
            # # working on dynamic headers - but pandas will do all of this already
            # headers = get_restart_log_headers()
            # display_string = ' | '.join([f'{ch.replace("_", " ").title():<25}' for ch in headers])
            # print(display_string)
            print(f"{'ID':<5} | {'Restart Initialized':<25} | {'Restart Message':<35} | {'Additional Information':<25}")
            print("-" * 120)
            for log in rows:
                print(f"{log[0]:<5} | {log[1]:<25} | {log[2]:<35} | {log[3]:<}")
        else:
            print("No records found.")
    except Exception as e:
        lg.error(f"Error while printing restart logs: {e}")
