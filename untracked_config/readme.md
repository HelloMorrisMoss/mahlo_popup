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

## lam_num.py

Contains a "constant" integer LAM_NUM. It is either 0, 1, or 2. This is a reference to a machine number and is used by
the popup to limit display information to that which is relevant to the machine.

## th_creds.py

Contains a dictionary of parameters for a psycopg2.connect'ion to an Ignition tag history database.

## thickness_specifications.py

Contains a function that will return the minimum and maximum thickness for the provided parameters. The docstring:

    """Get the minimum and maximum thickness specification

    :param adhesive: str, the adhesive type.
    :param target_thickness: int, the target or nominal foam thickness.
    :param specification: str, the specification to use, default is Nitto internal spec.
    :return: tuple, of floats, the minimum and maximum.
    """
