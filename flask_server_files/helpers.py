import contextlib
import datetime
import errno
import os
import time
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

# todo: move to dev common?
@contextlib.contextmanager
def single_instance(filename: str, timeout: float = 10.0) -> Callable[[], Any]:
    """A context manager that ensures only one instance of the program is running at a time.

    :param filename: A string representing the location of the lock file.
    :type filename: str
    :param timeout: The maximum number of seconds to wait for the lock, defaults to 10.0.
    :type timeout: float

    :yields: None

    :raises OSError: If the lock file cannot be created exclusively, or if the lock cannot be obtained.
    """

    start_time = time.monotonic()
    while True:
        try:
            # Open the lock file in exclusive mode
            handle = os.open(filename, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        except OSError as e:
            # Another instance is already running
            if e.errno == errno.EEXIST:
                # Check if the lock has timed out
                if time.monotonic() - start_time > timeout:
                    os.remove(filename)
                else:
                    time.sleep(0.1)
                    continue
            else:
                # Reraise the exception for other OSError types
                raise
        break

    try:
        yield
    finally:
        # Release the lock and delete the file
        os.close(handle)
        os.remove(filename)
