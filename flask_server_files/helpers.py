import contextlib
import datetime
import errno
import os
from typing import Any, Callable

from sqlalchemy.types import TIMESTAMP, TypeDecorator


class Timestamp(TypeDecorator):
    impl = TIMESTAMP

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        if isinstance(value, datetime.datetime):
            return value.isoformat()

        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        return datetime.datetime.fromisoformat(value)


def jsonize_sqla_model(model):
    """Get a json serializable representation of the SQLAlchemy Model instance.

    This is needed due to datetimes, they are converted to ISO 8601 format strings.

    :return: dict
    """

    jdict = {}
    for key in model.__table__.columns.keys():
        this_val = getattr(model, key)
        if isinstance(this_val, datetime.datetime):
            try:
                this_val = this_val.isoformat()
            except AttributeError as er:
                this_val = str(this_val)

        jdict[key] = this_val
    return jdict


def remove_empty_parameters(data):
    """Accepts a dictionary and returns a dict with only the key, values where the values are not None."""

    return {key: value for key, value in data.items() if value is not None}


@contextlib.contextmanager
def single_instance(filename: str) -> Callable[[], Any]:
    """A context manager that ensures only one instance of the program is running at a time.

    :param filename: A string representing the location of the lock file.
    :type filename: str

    :yields: None

    :raises OSError: If the lock file cannot be created exclusively, or if the lock cannot be obtained.
    """

    try:
        # Open the lock file in exclusive mode
        handle = os.open(filename, os.O_CREAT | os.O_EXCL | os.O_RDWR)
    except OSError as e:
        # Another instance is already running
        if e.errno == errno.EEXIST:
            raise OSError('Another instance of the program is already running.') from e
        else:
            # Reraise the exception for other OSError types
            raise
    try:
        yield
    finally:
        # Release the lock and delete the file
        os.close(handle)
        os.remove(filename)
