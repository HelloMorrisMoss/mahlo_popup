all_args = ('source_lot_number', 'tabcode', 'recipe', 'lam_num', 'rolls_of_product_post_slit',
                'defect_start_ts', 'defect_end_ts', 'length_of_defect_meters', 'belt_marks', 'bursting',
                'contamination', 'curling', 'delamination', 'lost_edge', 'puckering', 'shrinkage', 'thickness',
                'wrinkles', 'other', 'rem_l', 'rem_lc', 'rem_c', 'rem_rc', 'rem_r', 'entry_created_ts',
                'entry_modified_ts', 'record_creation_source')

required_args = ('source_lot_number', 'tabcode', 'recipe', 'lam_num',
                     'defect_start_ts', 'defect_end_ts', 'length_of_defect_meters')

optional_args = ['rolls_of_product_post_slit', 'belt_marks', 'bursting', 'contamination', 'curling', 'delamination', 'lost_edge', 'puckering', 'shrinkage', 'thickness', 'wrinkles', 'other', 'rem_l', 'rem_lc', 'rem_c', 'rem_rc', 'rem_r', 'entry_created_ts', 'entry_modified_ts', 'record_creation_source']

arg_type_dict = {'defect_id': int,
                     'source_lot_number': str,
                     'tabcode': str,
                     'recipe': str,
                     'lam_num': int,
                     'rolls_of_product_post_slit': int,
                     'defect_start_ts': str,
                     'defect_end_ts': str,
                     'length_of_defect_meters': float,
                     'belt_marks': bool,
                     'bursting': bool,
                     'contamination': bool,
                     'curling': bool,
                     'delamination': bool,
                     'lost_edge': bool,
                     'puckering': bool,
                     'shrinkage': bool,
                     'thickness': bool,
                     'wrinkles': bool,
                     'other': bool,
                     'rem_l': bool,
                     'rem_lc': bool,
                     'rem_c': bool,
                     'rem_rc': bool,
                     'rem_r': bool,
                     'entry_created_ts': str,
                     'entry_modified_ts': str,
                     'record_creation_source': str}