import unittest
import src.available_slot_finder
from pathlib import Path
from datetime import datetime


class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.duration_in_minutes = 30
        cls.minimum_people = 2

    def test_validate_calendars_path_with_wrong_path_should_return_false(self):
        # given
        wrong_path = Path('wrong_path')

        # then
        self.assertFalse(src.available_slot_finder.validate_calendars_path(wrong_path))

    def test_validate_date_formats_wrong_date_format_should_raise_exception(self):
        # given
        wrong_date_range_format = '2020/10/24 23:56:54'

        # then
        with self.assertRaises(ValueError):
            src.available_slot_finder.validate_date_range_format(wrong_date_range_format)

    def test_validate_date_range_formats_correct_two_part_date_range(self):
        # given
        date_range = '2022-05-14 12:00:00 - 2022-05-14 12:59:59'
        expected_result = (datetime(2022, 5, 14, 12, 0, 0), datetime(2022, 5, 14, 12, 59, 59))

        # then
        self.assertEqual(expected_result, src.available_slot_finder.validate_date_range_format(date_range))

    def test_validate_date_range_formats_correct_one_part_date_range(self):
        # given
        date_range = '2022-05-14'
        expected_result = (datetime(2022, 5, 14, 0, 0, 0), datetime(2022, 5, 14, 23, 59, 59))

        # then
        self.assertEqual(expected_result, src.available_slot_finder.validate_date_range_format(date_range))


if __name__ == '__main__':
    unittest.main()
