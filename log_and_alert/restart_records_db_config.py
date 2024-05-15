"""Contains configuration strings for the restart records database.

directory: where to create and look for the database file.
db_filename: the file name to use for the database file.
restart_records_table: the name of the table to use for the records.
database_file_path: file path for the database file.
"""

import os
from typing import Final

directory: Final[str] = './untracked_config'
db_filename: Final[str] = '../untracked_config/restart_records.db'
restart_records_table: Final[str] = 'restart_records'
database_file_path: Final[str] = os.path.join(directory, db_filename)
