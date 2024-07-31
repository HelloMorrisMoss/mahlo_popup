
from flask_restful import reqparse, Resource

from flask_server_files.helpers import remove_empty_parameters
from flask_server_files.models.lam_operator import OperatorModel
from log_and_alert.log_setup import lg


class Operator(Resource):
    defect_parser = reqparse.RequestParser()
    # todo: is there a reason this isn't using arg_type_dict.items()?
    all_args = 'id', 'first_name', 'last_name', 'lam_1_certified', 'lam_2_certified', 'lam_num'
    arg_type_dict = {'id': int, 'first_name': str, 'last_name': str, 'lam_1_certified': bool, 'lam_2_certified': bool,
                     'lam_num': int}

    for arg in all_args:
        defect_parser.add_argument(arg, type=arg_type_dict[arg], required=False, help='This argument is optional.')

    def get(self):
        """Get a response with the json representation of the operators."""
        try:
            data = self.defect_parser.parse_args()
            lam_num = data.get('lam_number')
        except Exception:  # this is to handle 415: Unsupported Media Type
            lam_num = None  # though it should be unnecessary

        with OperatorModel.session() as session:
            if lam_num:
                ops = OperatorModel.get_active_operators(lam_num)
            else:
                ops = OperatorModel.get_active_operators()
                print(f'{ops=}')

            if ops:
                ops_list = []
                for op in ops:
                    ops_list.append(op.jsonizable())
                response = ops_list, 200
            else:
                response = {'operator': 'No operators found'}, 404
            OperatorModel.session.remove()
        print(f'{response=}')
        return response

    def post(self):
        data = self.defect_parser.parse_args()
        # don't pass the Model empty parameters
        data = remove_empty_parameters(data)
        with OperatorModel.session() as session:
            try:
                operator = OperatorModel.new_operator(**data)
                session.add(operator)
                response_dict = operator.jsonizable()
                OperatorModel.session.remove()
            except TypeError as tyerr:
                return {'exception': str(tyerr)}, 400
            except Exception as uhe:
                return {'exception': str(uhe)}, 500
        return response_dict, 201

    def put(self):
        print('operator put')
        data = remove_empty_parameters(self.defect_parser.parse_args())
        print(data)
        id_ = data.get('id')
        if id_ is not None:
            with OperatorModel.session() as session:
                existing_op = OperatorModel.find_by_id(id_=id_, wrap_model=False)
                print(f'{existing_op=}')
                if existing_op is not None:
                    op_changes = 0
                    for key, arg in data.items():
                        current_val = getattr(existing_op, key)
                        if current_val != arg:
                            lg.debug('updating %s from %s to %s', key, current_val, arg)
                            setattr(existing_op, key, arg)
                            op_changes += 1
                        else:
                            lg.debug('%s is the same: %s', key, arg)
                    # if op_changes:
                    session.add(existing_op)
                    session.commit()
                    response = existing_op.jsonizable(), 201
                    print(f'{response=}')
                    return response
                else:
                    return self.post()


class Operators(Operator):
    defect_parser = reqparse.RequestParser(bundle_errors=True)
    arg_type_dict = {'lam_number': int, 'records': list[dict[str: any]]}
    # todo: ids parameter, get operators with those id numbers - not needed right now

    for arg, arg_type in arg_type_dict.items():
        defect_parser.add_argument(arg, type=arg_type, required=False, help='This argument is optional.',
                                   location='json')  # location json required for the list of records in post

    def get(self):
        """Get a response with the json representation of the operators."""
        try:
            data = self.defect_parser.parse_args()
            lam_num = data.get('lam_number')
        except Exception:  # this is to handle 415: Unsupported Media Type
            lam_num = None  # though it should be unnecessary

        with OperatorModel.session() as session:
            if lam_num:
                ops = OperatorModel.get_active_operators(lam_num)
            else:
                ops = OperatorModel.get_active_operators()

            if ops:
                ops_list = []
                for op in ops:
                    ops_list.append(op.jsonizable())
                response = ops_list, 200
            else:
                response = {'operator': 'No operators found'}, 404
            OperatorModel.session.remove()
        return response

    def post(self):
        # todo: don't know why postman sending a list of ops as records is getting back the
        #  help message 'This argument is optional.' from the argument parser? 400 status
        #  the operators.post print below is going off, but nothing else seems to be
        print('operators.post')
        data = self.defect_parser.parse_args()
        new_ops_data = data.get('records')
        print(f'{new_ops_data=}')
        if new_ops_data:
            responses = []
            with OperatorModel.session() as session:
                for op_data in new_ops_data:
                    new_op_data = remove_empty_parameters(op_data)
                    operator = OperatorModel.new_operator(**new_op_data)
                    session.add(operator)
                    responses.append(operator.jsonizable())
                OperatorModel.session.remove()
            return responses, 201
        else:
            return {'error': 'No records received.'}, 400

    def put(self):
        # todo: multiple rows update similar to Operators.post is now
        print('operator put')
        data = remove_empty_parameters(self.defect_parser.parse_args())
        print(data)
        id_ = data.get('id')
        if id_ is not None:
            with OperatorModel.session() as session:
                existing_op = OperatorModel.find_by_id(id_=id_, wrap_model=False)
                print(f'{existing_op=}')
                if existing_op is not None:
                    op_changes = 0
                    for key, arg in data.items():
                        current_val = getattr(existing_op, key)
                        if current_val != arg:
                            lg.debug('updating %s from %s to %s', key, current_val, arg)
                            setattr(existing_op, key, arg)
                            op_changes += 1
                        else:
                            lg.debug('%s is the same: %s', key, arg)
                    # if op_changes:
                    session.add(existing_op)
                    session.commit()
                    response = existing_op.jsonizable(), 201
                    print(f'{response=}')
                    return response
                else:
                    return self.post()
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
    #     return flask_server_files.helpers.jsonizable(), return_code
