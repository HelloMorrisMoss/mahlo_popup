"""These are tuples, lists, and dicts of column names, arguments, and types for use elsewhere."""

all_args = ('id',
            'source_lot_number',
            'tabcode',
            'recipe',
            'lam_num',
            'file_name',
            'rolls_of_product_post_slit',
            'defect_start_ts',
            'defect_end_ts',
            'length_of_defect_meters',
            'mahlo_start_length',
            'mahlo_end_length',
            'defect_type',
            'rem_l',
            'rem_lc',
            'rem_c',
            'rem_rc',
            'rem_r',
            'entry_created_ts',
            'entry_modified_ts',
            'record_creation_source',
            'marked_for_deletion',
            'operator_saved_time')

editing_required_args = ('source_lot_number', 'tabcode', 'recipe', 'lam_num',
                         'defect_start_ts', 'defect_end_ts', 'length_of_defect_meters')

editing_optional_args = ['id', 'rolls_of_product_post_slit', 'belt_marks', 'bursting', 'contamination', 'curling',
                         'delamination', 'lost_edge', 'puckering', 'shrinkage', 'thickness', 'wrinkles', 'other',
                         'rem_l', 'rem_lc', 'rem_c', 'rem_rc', 'rem_r', 'entry_created_ts', 'entry_modified_ts',
                         'record_creation_source']

# finding_required_args = ('source_lot_number', 'tabcode', 'recipe', 'lam_num',
#                           'defect_start_ts', 'defect_end_ts', 'length_of_defect_meters')
# 
# finding_optional_args = ['defect_id', 'rolls_of_product_post_slit', 'belt_marks', 'bursting', 'contamination',
# 'curling', 'delamination', 'lost_edge', 'puckering', 'shrinkage', 'thickness', 'wrinkles', 'other', 'rem_l',
# 'rem_lc', 'rem_c', 'rem_rc', 'rem_r', 'entry_created_ts', 'entry_modified_ts', 'record_creation_source']

arg_type_dict = {'id': int,
                 'source_lot_number': str,
                 'tabcode': str,
                 'recipe': str,
                 'lam_num': int,
                 'file_name': str,
                 'rolls_of_product_post_slit': int,
                 'defect_start_ts': str,
                 'defect_end_ts': str,
                 'length_of_defect_meters': float,
                 'mahlo_start_length': float,
                 'mahlo_end_length': float,
                 'defect_type': str,
                 'other': bool,
                 'rem_l': bool,
                 'rem_lc': bool,
                 'rem_c': bool,
                 'rem_rc': bool,
                 'rem_r': bool,
                 'entry_created_ts': str,
                 'entry_modified_ts': str,
                 'record_creation_source': str,
                 'marked_for_deletion': bool,
                 'operator_saved_time': str
                 }
