import datetime

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


def jsonizable(model):
    """Get a json serializable representation of the SQLAlchemy Model instance.

    This is needed due to datetimes, they are converted to ISO 8601 format strings.

    :return: dict
    """
    from sqlalchemy.orm.state import InstanceState

    jdict = {}
    for key, this_val in model.__dict__.items():
        # this_val = getattr(model, key)
        if isinstance(this_val, datetime.datetime):
            try:
                this_val = this_val.isoformat()
            except AttributeError as er:
                this_val = str(this_val)
        elif not isinstance(this_val, InstanceState):
            jdict[key] = this_val
    return jdict


def remove_empty_parameters(data):
    """Accepts a dictionary and returns a dict with only the key, values where the values are not None."""

    return {key: value for key, value in data.items() if value is not None}
