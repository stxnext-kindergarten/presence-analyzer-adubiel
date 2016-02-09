# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest


from presence_analyzer import main, utils, views


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data',
    'test_data.csv'
)

TEST_BROKEN_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data',
    'test_broken_data.csv'
)

TEST_BROKEN_DATA2_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data',
    'test_broken_data2.csv'
)


# pylint: disable=maybe-no-member, too-many-public-methods, undefined-variable
# pylint: disable=invalid-name
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_mean_time_weekday_view_negative(self):
        """
        Test mean presence time grouped by weekday for given user.
        Part with incorrect data - user_id doesn't exists.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/666')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.content_type, 'text/html')

    def test_mean_time_weekday_view_positive(self):
        """
        Test mean presence time grouped by weekday for given user.
        Part with correct data - user_id exists.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        self.assertEqual(len(data[0]), 2)
        self.assertEqual(type(data[0][0]), unicode)
        self.assertEqual(type(data[0][1]), int)

    def test_presence_weekday_view_negative(self):
        """
        Test total presence time for given user grouped by weekday.
        Part with incorrect data - user_id doesn't exists.
        """
        resp = self.client.get('/api/v1/presence_weekday/666')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.content_type, 'text/html')

    def test_presence_weekday_view_positive(self):
        """
        Test mean presence time grouped by weekday for given user.
        Part with correct data - user_id exists.
        """
        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        self.assertEqual(len(data[0]), 2)
        # skip first row because it contains labels not the data
        self.assertEqual(type(data[1][0]), unicode)
        self.assertEqual(type(data[1][1]), int)

    def test_presence_start_end_view_negative(self):
        """
        Test presence mean time start/end for given user grouped by weekday.
        Part with incorrect data - user_id doesn't exists.
        """
        resp = self.client.get('/api/v1/presence_start_end/666')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.content_type, 'text/html')

    def test_presence_start_end_view_positive(self):
        """
        Test mean presence time grouped by weekday for given user.
        Part with correct data - user_id exists.
        """
        resp = self.client.get('/api/v1/presence_start_end/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        self.assertEqual(len(data[0]), 3)
        self.assertEqual(type(data[0][0]), unicode)
        self.assertEqual(type(data[0][1]), int)
        self.assertEqual(type(data[0][2]), int)


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5)
        )

    def test_get_data_broken_datasource(self):
        """
        Test parsing of CSV file - testing broken data (bad types).
        """
        main.app.config.update({'DATA_CSV': TEST_BROKEN_DATA_CSV})
        data_broken = utils.get_data()
        self.assertEqual(len(data_broken[11]), 5)

    def test_get_data_broken_datasource2(self):
        """
        Test parsing of CSV file - testing broken data (additional column).
        """
        main.app.config.update({'DATA_CSV': TEST_BROKEN_DATA2_CSV})
        data_broken2 = utils.get_data()
        self.assertEqual(len(data_broken2), 0)

    def test_group_by_weekday_list(self):
        """
        Test grouping by weekday.
        Checks if the result is a list.
        """
        data = utils.get_data()
        grouped_by_weekday = utils.group_by_weekday(data[10])
        self.assertIsInstance(grouped_by_weekday, list)

    def test_group_by_weekday_incorrect_input(self):
        """
        Test grouping by weekday.
        Incorrect input type.
        """
        with self.assertRaises(TypeError):
            utils.group_by_weekday({'first': 123, 'second': '123'})

    def test_group_start_end_list(self):
        """
        Test grouping starts and ends by weekday.
        Checks if the result is a list.
        """
        data = utils.get_data()
        grouped_by_weekday = utils.group_start_end(data[10])
        self.assertIsInstance(grouped_by_weekday, list)

    def test_group_start_end_incorrect_input(self):
        """
        Test grouping starts and ends by weekday.
        Incorrect input type.
        """
        with self.assertRaises(TypeError):
            utils.group_by_weekday({'first': 123, 'second': '123'})

    def test_mean_start_stop_list(self):
        """
        Test counting starts and ends by weekday.
        Checks if the result is a list.
        """
        data = utils.get_data()
        counted_by_weekday = utils.mean_start_stop(data[10])
        self.assertIsInstance(counted_by_weekday, list)

    def test_mean_start_stop_incorrect_input(self):
        """
        Test counting starts and ends by weekday.
        Incorrect input type.
        """
        with self.assertRaises(TypeError):
            utils.mean_start_stop({'first': 123, 'second': '123'})

    def test_seconds_since_midnight(self):
        """
        Test calculating seconds since midnight.
        Checks if the result is correct.
        """
        example_times = [
            [datetime.time(17, 30, 15), 63015],  # 17*3600 + 30*60 + 15 = 63015
            [datetime.time(11, 20, 0), 40800],   # 11*3600 + 20*60 + 0  = 40800
        ]

        for example_time in example_times:
            self.assertEqual(
                utils.seconds_since_midnight(example_time[0]),
                example_time[1]
            )

    def test_seconds_since_midnight_incorrect_input(self):
        """
        Test calculating seconds since midnight.
        Incorrect input type.
        """
        with self.assertRaises(AttributeError):
            utils.seconds_since_midnight('some string')

    def test_interval(self):
        """
        Test calculating amount of time between two datetime.time objects.
        Checks if the result is correct.
        """
        self.assertEqual(
            utils.interval(
                datetime.time(11, 20, 0),
                datetime.time(17, 30, 15),
            ),
            22215
        )

    def test_interval_incorrect_input(self):
        """
        Test calculating amount of time between two datetime.time objects.
        Incorrect input type.
        """
        with self.assertRaises(AttributeError):
            utils.interval('not a datetime.time', 'object')

    def test_mean(self):
        """
        Test returning arithmetic mean or zero if empty.
        Check if the result is correct.
        """
        self.assertEqual(utils.mean([1, 39, 22, 2]), 16)
        self.assertEqual(utils.mean([]), 0)

    def test_mean_incorrect_input(self):
        """
        Test returning arithmetic mean or zero if empty.
        Incorrect input type.
        """
        with self.assertRaises(TypeError):
            utils.mean('not a list')


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
