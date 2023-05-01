import os
import shutil
import tempfile
import unittest

from dev_common import blank_up


class DevCommonTests(unittest.TestCase):
    def test_dt_to_shift(self):
        """Test that the shifts come out as expected. Especially, close to the shift changes."""
        import datetime
        from dev_common import dt_to_shift

        time_tuples = (
            ((0, 0, 0), 3),
            ((3, 15, 0), 3),
            ((7, 14, 59), 3),
            ((7, 15, 0), 1),
            ((12, 30, 0), 1),
            ((15, 14, 59), 1),
            ((15, 15, 0), 2),
            ((18, 30, 0), 2),
            ((23, 14, 59), 2),
            ((23, 15, 0), 3),
            )

        for subt, ((hour, minute, second), control_shift) in enumerate(time_tuples):
            with self.subTest(i=subt):
                test_dt = datetime.datetime(year=2022, month=1, day=1, hour=hour, minute=minute, second=second)
                self.assertEqual(dt_to_shift(test_dt), control_shift)


class TestBlankUp(unittest.TestCase):

    def setUp(self):
        # create a temporary directory
        self.test_dir = tempfile.mkdtemp()

        # create a test file inside the temporary directory
        self.test_file = os.path.join(self.test_dir, 'test.txt')
        with open(self.test_file, 'w') as f:
            f.write('test')

    def tearDown(self):
        # remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)

    def test_blank_up(self):
        # call the function and check that a backup file was created
        blank_up(self.test_file)
        backup_files = [file for file in os.listdir(self.test_dir) if file.startswith('test_BACKUP_')]
        self.assertEqual(len(backup_files), 1)

        # check that the original file was replaced with an empty file
        with open(self.test_file, 'r') as f:
            self.assertEqual(f.read(), '')
