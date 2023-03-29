from ..mt import WallConstructionMt
import time
import unittest

"""
3
21 25 28
17
17 22 17 19 17
"""


class TestMt(unittest.TestCase):
    INPUT_FILES_DIRECTORY = 'wall_construction/tests/inputs/mt'
    LOG_FILE_DIRECTORY = 'wall_construction/tests/logs/mt'

    def setUp(self) -> None:
        self.wall_construction = WallConstructionMt(file_input=f'{self.INPUT_FILES_DIRECTORY}/input.txt',
                                                    log_file=f'{self.LOG_FILE_DIRECTORY}/{self._testMethodName}_{time.time()}.log')

    def test_overview(self):
        _, total_cost = self.wall_construction.get_wall_costs(accumulate=True)
        self.assertEqual(32233500, total_cost)

    def test_overview_day_1(self):
        _, total_cost = self.wall_construction.get_wall_costs(day=1, accumulate=True)
        self.assertEqual(total_cost, 1111500)

    def test_overview_day_2(self):
        _, total_cost = self.wall_construction.get_wall_costs(day=2, accumulate=True)
        self.assertEqual(total_cost, 2223000)

    def test_overview_profile_1_day_1(self):
        _, total_cost = self.wall_construction.get_wall_costs(profile_no=1, day=1, accumulate=True)
        self.assertEqual(total_cost, 1111500)

    def test_overview_profile_1(self):
        _, total_cost = self.wall_construction.get_wall_costs(profile_no=1, accumulate=True)
        self.assertEqual(total_cost, 5928000)

    def test_daily_profile_1_day_1(self):
        ice_volume, _ = self.wall_construction.get_wall_costs(profile_no=1, day=1)
        self.assertEqual(ice_volume, 585)

    def test_daily_profile_1_day_3(self):
        ice_volume, _ = self.wall_construction.get_wall_costs(profile_no=1, day=3)
        self.assertEqual(ice_volume, 390)

    def test_daily_profile_2_day_3(self):
        ice_volume, _ = self.wall_construction.get_wall_costs(profile_no=2, day=3)
        self.assertEqual(ice_volume, 195)

    def test_daily_profile_2_day_1(self):
        ice_volume, _ = self.wall_construction.get_wall_costs(profile_no=2, day=1)
        self.assertEqual(ice_volume, 0)

    # def test_daily_profile_1_day_999(self):
    #     ice_volume, _ = self.wall_construction.get_wall_costs(day=999, profile_no=1)
    #     self.assertEqual(ice_volume, 0)

    def test_daily_profile_day_1(self):
        ice_volume, _ = self.wall_construction.get_wall_costs(day=1)
        self.assertEqual(ice_volume, 585)

    # def test_daily_profile_day_999(self):
    #     ice_volume, _ = self.wall_construction.get_wall_costs(day=999)
    #     self.assertEqual(ice_volume, 0)


if __name__ == '__main__':
    unittest.main()

