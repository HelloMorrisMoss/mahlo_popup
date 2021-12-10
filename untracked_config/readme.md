# Config files
This directory contains configuration files that are not tracked in version control as they contain information
specific to databases and computers. The values intended to be imported and used elsewhere in the project.

## development_node.py
Contains a variable containing the development system's name. To protect production systems from code only intended for
development.

<code>dev_node = 'development_computer_name'</code>


## db_uri.py
Contains a variable with the string used by sqlalchemy to connect to the database.

<code>DATABASE_URI = 'postgresql+psycopg2://user_name:password@localhost:5432/database_name'</code>
