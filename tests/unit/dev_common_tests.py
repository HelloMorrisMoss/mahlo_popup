import unittest


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
