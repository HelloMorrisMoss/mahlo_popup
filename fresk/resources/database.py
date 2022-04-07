"""The resource for working on the database table. FOR DEVELOPMENT."""
import datetime

from flask_restful import reqparse, Resource

from fresk.sqla_instance import fsa
from log_setup import lg


def create_tables():
    """Recreate the database tables."""
    from untracked_config.development_node import dev_node

    lg.debug('Rebuilding database tables.')

    # this section is to remove the old database table if the DefectModel table needs to be changed:

    if dev_node:
        fsa.drop_all()  # TODO: this is for model/table development only and SHOULD NOT be used with production

    # this ensures there is a table there
    fsa.create_all()


class Database(Resource):
    defect_parser = reqparse.RequestParser()
    defect_parser.add_argument('action', type=str, required=True, help='This argument is not optional.')

    def post(self):
        data = self.defect_parser.parse_args()
        action = data.get('action')
        if action:
            if action == 'reset_database':
                create_tables()

                return {'database reset': f'successful at {datetime.datetime.now().isoformat()}'}, 200
            # elif action == 'create_operators_table':
            #     OperatorModel.__table__.create(checkfirst=True)
            #     return {'operator table creation': f'successful at {datetime.datetime.now().isoformat()}'}, 200
            else:
                return {'no valid command': f'at {datetime.datetime.now().isoformat()}'}, 400
        return {'No action specified': f'at {datetime.datetime.now().isoformat()}'}, 400
