import unittest

from _data.data_helper import DataHelper


class TestDataHelper(unittest.TestCase):
    """
    TODO
    Implement tests of all data helper class functions
    """

    def test_init(self):
        dh = DataHelper({"level": "state"}, "./tests/test_data.json")

        # Assert class created with test params
        print("DataHelper created with level=state")
        self.assertEqual(dh.params["level"], "state")

        # Assert class read the election data file
        print("Correctly finds New Mexico data in test class instance")
        self.assertTrue("New Mexico" in dh.election_data)

    def test_county_flatten(self):
        dh = DataHelper({"level": "county"}, "./tests/test_data.json")
        election_data = dh.flatten_county_results(dh.election_data)

        # Assert State names are no longer in data
        print("Assert county name keys are in flattened county election data obj")
        self.assertTrue("Window Rock, New Mexico" in election_data)
        self.assertTrue("Guilford, North Carolina" in election_data)

        # Assert County, State objects contain correct party keys
        print("Assert county name keys each have Republican & Democrat data fields")
        for county in election_data:
            self.assertTrue(len(election_data[county]["Democrats"].keys()))
            self.assertTrue(len(election_data[county]["Republicans"].keys()))
