import datetime
from sqlalchemy.types import TypeDecorator, TIMESTAMP

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
