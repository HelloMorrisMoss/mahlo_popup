from flask_restful import reqparse, Resource

from fresk.helpers import remove_empty_parameters
from fresk.models.lam_operator import OperatorModel


class Operator(Resource):
    defect_parser = reqparse.RequestParser()

    all_args = 'first_name', 'last_name', 'lam_1_certified', 'lam_2_certified'
    arg_type_dict = {'first_name': str, 'last_name': str, 'lam_1_certified': bool, 'lam_2_certified': bool}

    for arg in all_args:
        defect_parser.add_argument(arg, type=arg_type_dict[arg], required=False, help='This argument is optional.')

    # def get(self):
    #
    #     data = self.defect_parser.parse_args()
    #     from pprint import pprint
    #     pprint(data)
    #     id_ = data.get('id')
    #     lg.debug('id from data: %s', id_)
    #     if id_:
    #         defect = DefectModel.find_by_id(id_)
    #
    #         if defect:
    #             return defect.jsonizable(), 200
    #         else:
    #             return {'defect_instance': f'Defect not found with id: {id_}'}, 404
    #
    #     return {'defect_instance': f'An id is required! (?id=###)'}, 400

    def post(self):
        data = self.defect_parser.parse_args()

        # don't pass the Model empty parameters
        data = remove_empty_parameters(data)
        operator = OperatorModel(*data)

        return operator.jsonizable(), 201

    # def remove_empty_parameters(self, data):
    #     """Accepts a dictionary and returns a dict with only the key, values where the values are not None."""
    #
    #     return {key: value for key, value in data.items() if value is not None}
    #
    # # # TODO: once there is an option to edit defects, this may need to be touched up
    # # def put(self):
    # #     data = self.defect_parser.parse_args()
    # #     # check if there is an id, if there is, try to get the defect record
    # #     id_ = data.get('id')
    # #     if id_:
    # #         defect = DefectModel
    # #         if defect:
    # #             lg.debug('defect exists, updating')
    # #             # don't pass the Model empty parameters
    # #             data = self.remove_empty_parameters(data)
    # #             lg.debug('put dict %s', data)
    # #             # update the existing
    # #             for key, arg in data.items():
    # #                 lg.debug('updating %s from %s to %s', key, getattr(defect, key), arg)
    # #                 setattr(defect, key, arg)
    # #             defect.save_to_database()
    # #             return_code = 200
    # #     else:
    # #         lg.debug('creating new defect')
    # #         # create a new record
    # #         defect = DefectModel(**data)
    # #         return_code = 201
    # #
    # #     defect.save_to_database()
    #
    #
    #     return fresk.helpers.jsonizable(), return_code
