from flask_restful import reqparse, Resource

from flask_server_files.defect_args import all_args, arg_type_dict
from flask_server_files.helpers import jsonize_sqla_model, remove_empty_parameters
from flask_server_files.models.defect import DefectModel, DefectQueryLogModel, DefectInsertionLogModel
from log_and_alert.log_setup import lg


class Defect(Resource):
    defect_parser = reqparse.RequestParser()

    for arg in all_args:
        defect_parser.add_argument(arg, type=arg_type_dict[arg], required=False, help='This argument is optional.')

    def get(self):

        data = self.defect_parser.parse_args()
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
        data = remove_empty_parameters(data)
        defect = DefectModel(**data)

        return defect.jsonizable(), 201

    # TODO: once there is an option to edit defects, this may need to be touched up
    def put(self):
        data = self.defect_parser.parse_args()
        # check if there is an id, if there is, try to get the defect record
        id_ = data.get('id')
        if id_:
            defect = DefectModel
            if defect:
                lg.debug('defect exists, updating')
                # don't pass the Model empty parameters
                data = remove_empty_parameters(data)
                lg.debug('put dict %s', data)
                # update the existing
                for key, arg in data.items():
                    lg.debug('updating %s from %s to %s', key, getattr(defect, key), arg)
                    setattr(defect, key, arg)
                defect.save_to_database()
                return_code = 200
        else:
            lg.debug('creating new defect')
            # create a new record
            defect = DefectModel(**data)
            return_code = 201

        defect.save_to_database()

        return defect.jsonizable(), return_code


class DefectList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('confirm_all', type=bool, required=False, help='This argument is optional.')
    parser.add_argument('start_date', type=str, required=False, location=['json', 'values', 'args'], help='Defects with start dates after this. (optional)')
    parser.add_argument('end_date', type=str, required=False, location=['json', 'values', 'args'], help='Defects with end dates before this. (optional)')
    parser.add_argument('lam_num', type=str, required=False, location=['json', 'values', 'args'], help='Defects from this laminator number only. (optional)')
    parser.add_argument('source', type=str, required=False, location=['json', 'values', 'args'], help='The source of the request. (optional)')

    def get(self):
        pargs = self.parser.parse_args()
        start_date = pargs.get('start_date')
        end_date = pargs.get('end_date')
        lam_num = pargs.get('lam_num')
        source = pargs.get('source')
        lam_num = int(lam_num) if lam_num is not None else None
        lg.info('Request for defects data received. Start: %s End: %s Source: %s', start_date, end_date, source)
        with DefectModel.session() as session:
            if start_date and end_date:
                results = DefectModel.get_defects_between_dates(start_date, end_date, lam_num)
            else:
                results = DefectModel.query.order_by(
                    DefectModel.id.desc()).all()
            result_dict = {}
            if source:
                new_logs = []
                for row in results:
                    result_dict[row.id] = jsonize_sqla_model(row)
                    new_logs.append(DefectQueryLogModel(defect_id=row.id, source=source))
                
                if new_logs:
                    try:
                        session.add_all(new_logs)
                        session.commit()
                    except Exception as exc:
                        lg.error("Failed to batch save query logs: %s", exc)
                        session.rollback()
            else:
                for row in results:
                    result_dict[row.id] = jsonize_sqla_model(row)

            DefectModel.session.remove()
        lg.debug('Returning %s defects data results response.', len(result_dict.keys()))
        return {'results_dict': result_dict, 'default_column_order': DefectModel.__table__.columns.keys()}, 200

    def put(self):
        data = self.parser.parse_args()
        if data.get('confirm_all'):
            DefectModel.mark_all_confirmed()

        return {'completed': True}, 201


class DefectInsertion(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('defect_ids', type=int, action='append', required=True, location='json', help='List of defect IDs inserted.')
    parser.add_argument('report_name', type=str, required=True, location='json', help='The name of the report.')

    def post(self):
        data = self.parser.parse_args()
        defect_ids = data.get('defect_ids')
        report_name = data.get('report_name')

        lg.info('Reporting insertion of defects %s into report %s', defect_ids, report_name)

        new_logs = [DefectInsertionLogModel(defect_id=defect_id, report_name=report_name) for defect_id in defect_ids]
        
        with DefectModel.session() as session:
            try:
                session.add_all(new_logs)
                session.commit()
            except Exception as exc:
                lg.error("Failed to batch save insertion logs: %s", exc)
                session.rollback()
                return {'status': 'failed', 'message': str(exc)}, 500

        return {'status': 'success', 'inserted_count': len(defect_ids)}, 201
