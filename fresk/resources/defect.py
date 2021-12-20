from flask_restful import reqparse, Resource

from fresk.models.defect import DefectModel

from fresk.defect_args import all_args, arg_type_dict
from log_setup import lg
from flask_restful import reqparse, Resource

from fresk.defect_args import all_args, arg_type_dict
from fresk.models.defect import DefectModel
from log_setup import lg


class Defect(Resource):
    defect_parser = reqparse.RequestParser()

    for arg in all_args:
        defect_parser.add_argument(arg, type=arg_type_dict[arg], required=False, help='This argument is optional.')

    def get(self):

        data = self.defect_parser.parse_args()
        from pprint import pprint
        pprint(data)
        id_ = data.get('id')
        lg.debug('id from data: %s', id_)
        if id_:
            defect = DefectModel.find_by_id(id_)

            if defect:
                return defect.jsonizable(), 200
            else:
                return {'defect_instance': f'Defect not found with id: {id_}'}, 404

        return {'defect_instance': f'An id is required! (?id=###)'}, 400

    def post(self):
        data = self.defect_parser.parse_args()

        # don't pass the Model empty parameters
        data = self.remove_empty_parameters(data)
        defect = DefectModel.new_defect(**data)

        return defect.jsonizable(), 201

    def remove_empty_parameters(self, data):
        return {key: value for key, value in data.items() if value is not None}

    def put(self):
        data = self.defect_parser.parse_args()
        # check if there is an id, if there is, try to get the defect record
        id_ = data.get('id')
        if id_:
            defect = DefectModel.find_by_id(id_)
            if defect:
                # don't pass the Model empty parameters
                data = self.remove_empty_parameters(data)
                # update the existing
                for key, arg in data:
                    setattr(defect, key, arg)
                return_code = 200
        else:
            # create a new record
            defect = DefectModel(**data)
            return_code = 201

        defect.save_to_database()

        return defect.jsonizable(), return_code


class DefectList(Resource):
    # parser = reqparse.RequestParser()
    #
    # parser.add_argument('')

    # results = DefectModel.query.filter('entry_created_ts' != 'entry_modified_ts').all()
    def get(self):
        results = DefectModel.query.all()
        result_dict = {}
        for row in results:
            result_dict[row.id] = row.jsonizable()
        return result_dict, 200
