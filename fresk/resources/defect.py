from flask_restful import reqparse, Resource

from fresk.models.defect import DefectModel

from fresk.defect_args import all_args, arg_type_dict, editing_required_args, editing_optional_args
from log_setup import lg




class Defect(Resource):
    edit_parser = reqparse.RequestParser()

    for arg in editing_required_args:
        edit_parser.add_argument(arg, type=arg_type_dict[arg], required=True, help='This argument is required.')

    for arg in editing_optional_args:
        edit_parser.add_argument(arg, type=arg_type_dict[arg], required=False, help='This argument is optional.')

    def get(self):
        parser = reqparse.RequestParser()
        for arg in all_args:
            parser.add_argument(arg, type=arg_type_dict[arg], required=False, help='This argument is optional.')

        data = parser.parse_args()
        from pprint import pprint, pformat
        pprint(data)
        id_ = data.get('defect_id')
        lg.debug('id from data: %s', id_)
        if id_:
            defect = DefectModel.find_by_id(id_)

            if defect:
                return defect.json(), 200
            else:
                return {'message': f'Defect not found with id: {id_}'}, 404

        return {'message': f'An id is required! (?id=###)'}, 400

    def post(self):
        data = self.edit_parser.parse_args()
        defect = DefectModel(**data)
        defect.save_to_database()

        return defect.json(), 201

    def put(self):
        data = self.edit_parser.parse_args()

        # check if there is an id, if there is, try to get the defect record
        id_ = data.get('defect_id')
        if id_:
            defect = DefectModel.find_by_id(id_)
            if defect:
                # update the existing
                for key, arg in data:
                    # TODO: should this filter for Nones?
                    setattr(defect, key, arg)
                return_code = 200
        else:
            # create a new record
            defect = DefectModel(**data)
            return_code = 201

        defect.save_to_database()

        return defect.json(), return_code


class DefectList(Resource):
    # parser = reqparse.RequestParser()
    #
    # parser.add_argument('')

    # results = DefectModel.query.filter('entry_created_ts' != 'entry_modified_ts').all()
    def get(self):
        results = DefectModel.query.all()
        result_dict = {}
        for row in results:
            result_dict[row.id] = row.json()
        return result_dict, 200