"""The resource for working on the database table. FOR DEVELOPMENT."""
from fresk.sqla_instance import fsa
from log_setup import lg

from flask_restful import reqparse, Resource


def create_tables():
    """Recreate the database tables."""
    import platform
    from untracked_config.development_node import dev_node

    lg.debug('Rebuilding database tables.')

    # this section is to remove the old database table if the DefectModel table needs to be changed:
    node = platform.node()
    lg.debug(f'node {node=}')

    if node == dev_node:
        fsa.drop_all()  # TODO: this is for model/table development only and SHOULD NOT be used with production

    # this ensures there is a table there
    fsa.create_all()


class Database(Resource):
    defect_parser = reqparse.RequestParser()
    defect_parser.add_argument('action', type=str, required=True, help='This argument is not optional.')

    def post(self):
        data = self.defect_parser.parse_args()
        action = data.get('action')
        if action == 'reset_database':
            create_tables()
