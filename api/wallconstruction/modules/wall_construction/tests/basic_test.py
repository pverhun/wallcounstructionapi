from ..basic import WallConstruction
import unittest


class TestBasic(unittest.TestCase):
    INPUT_FILES_DIRECTORY = 'wall_construction/tests/inputs'

    def setUp(self) -> None:
        self.wall_construction = WallConstruction(file_input=f'{self.INPUT_FILES_DIRECTORY}/input.txt')

    def test_overview(self):
        _, total_cost = self.wall_construction.get_wall_costs(accumulate=True)
        self.assertEqual(32233500, total_cost)

    def test_overview_day_1(self):
        _, total_cost = self.wall_construction.get_wall_costs(day=1, accumulate=True)
        self.assertEqual(total_cost, 3334500)

    def test_overview_day_2(self):
        _, total_cost = self.wall_construction.get_wall_costs(day=2, accumulate=True)
        self.assertEqual(total_cost, 6669000)

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
        wall_construction = WallConstruction(file_input=f'{self.INPUT_FILES_DIRECTORY}/input.txt')
        ice_volume, _ = self.wall_construction.get_wall_costs(profile_no=2, day=3)
        self.assertEqual(ice_volume, 195)

    def test_daily_profile_1_day_999(self):
        wall_construction = WallConstruction(file_input=f'{self.INPUT_FILES_DIRECTORY}/input.txt')
        ice_volume, _ = self.wall_construction.get_wall_costs(day=999, profile_no=1)
        self.assertEqual(ice_volume, 0)

    def test_daily_profile_day_1(self):
        wall_construction = WallConstruction(file_input=f'{self.INPUT_FILES_DIRECTORY}/input.txt')
        ice_volume, _ = self.wall_construction.get_wall_costs(day=1)
        self.assertEqual(ice_volume, 1755)

    def test_daily_profile_day_999(self):
        wall_construction = WallConstruction(file_input=f'{self.INPUT_FILES_DIRECTORY}/input.txt')
        ice_volume, _ = self.wall_construction.get_wall_costs(day=999)
        self.assertEqual(ice_volume, 0)


if __name__ == '__main__':
    unittest.main()

