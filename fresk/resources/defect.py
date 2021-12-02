from flask_restful import reqparse, Resource

from models.defect import DefectModel

from fresk.defect_args import arg_type_dict, required_args, optional_args


class Defect(Resource):

    parser = reqparse.RequestParser()

    for arg in required_args:
        parser.add_argument(arg, type=arg_type_dict[arg], required=True, help='This argument is required.')

    for arg in optional_args:
        parser.add_argument(arg, type=arg_type_dict[arg], required=False, help='This argument is optional.')

    # def str(self, time_str):
    def get(self, id_):
        defect = DefectModel.find_by_id(id_)

        if defect:
            return defect.json(), 200
        else:
            return {'message': f'Defect not found with id: {id_}'}, 404

    def post(self):
        data = Defect.parser.parse_args()
        defect = DefectModel(**data)
        defect.save_to_database()

        return defect.json(), 201

