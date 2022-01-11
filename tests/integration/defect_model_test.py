from datetime import datetime

from fresk.models.defect import DefectModel
from tests.base_test import BaseTest


class DefectModelTest(BaseTest):
    def test_create_defect_record_specific_id(self):
        with self.app_context():
            # it does not exist
            self.assertIsNone(DefectModel.find_by_id(0))

            # create it
            defect = DefectModel(id=0)
            defect.save_to_database()

            # it does exist
            self.assertIsNotNone(DefectModel.find_by_id(0))

    def test_defect_class_method_find_all(self):
        with self.app_context():
            # is empty
            self.assertListEqual(DefectModel.find_all(), [])

            for i in range(3):
                di = DefectModel()
                di.save_to_database()

            self.assertEqual(len(DefectModel.find_all()), 3)

    def test_create_defect_record_defaults(self):
        with self.app_context():
            # there are no defects
            self.assertListEqual(DefectModel.find_all(), [])

            # create a defect without parameters
            defect = DefectModel()
            defect.save_to_database()

            print(defect.jsonizable())

            # it exists
            self.assertIsNotNone(DefectModel.find_by_id(defect.id))

            # check the defaults are correct
            dd = {'id': 1,
                  'source_lot_number': '',
                  'tabcode': '',
                  'recipe': '',
                  'lam_num': 0,
                  'file_name': '',
                  'flagger_fire': None,
                  'rolls_of_product_post_slit': 3,
                  'length_of_defect_meters': 0.0,
                  'mahlo_start_length': 0.0,
                  'mahlo_end_length': 0.0,
                  'defect_type': None,
                  'rem_l': False,
                  'rem_lc': False,
                  'rem_c': False,
                  'rem_rc': False,
                  'rem_r': False,
                  'record_creation_source': '',
                  'marked_for_deletion': False,
                  'operator_saved_time': None}

            for column, value in dd.items():
                def_column = getattr(defect, column)
                self.assertEqual(def_column, value)

            # the timestamps will be dynamic, check that they are datetime.datetime
            confirm_iso_timestring = 'entry_created_ts', 'entry_modified_ts', 'defect_start_ts', 'defect_end_ts'
            for tstr in confirm_iso_timestring:
                tstamp = getattr(defect, tstr)
                self.assertIsInstance(tstamp, datetime)

    def test_defect_class_method_find_new(self):
        with self.app_context():
            # the table is empty
            self.assertListEqual(DefectModel.find_all(), [])

            # create defect records
            defect0 = DefectModel()
            defect0.save_to_database()
            self.assertIsNone(defect0.operator_saved_time)

            # this one 'has been confirmed by the operator' and is not new
            defect1 = DefectModel()
            self.assertIsNone(defect1.operator_saved_time)
            defect1.operator_saved_time = datetime.now()
            defect1.entry_modified_ts = datetime.now()
            defect1.save_to_database()
            self.assertIsNotNone(defect1.operator_saved_time)

            defect2 = DefectModel()
            self.assertIsNone(defect2.operator_saved_time)
            defect2.save_to_database()

            # there are now only 2 new defects out of the 3
            new_defects = DefectModel.find_new()
            new_ids = tuple(df.id for df in new_defects)
            self.assertTrue(new_defects[0].id in new_ids)
            self.assertTrue(new_defects[1].id in new_ids)
            self.assertEqual(len(new_defects), 2)
