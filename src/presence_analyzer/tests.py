# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

from presence_analyzer import main, views, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


# pylint: disable=maybe-no-member, too-many-public-methods
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
    
    def test_mean_time_weekday_view(self):
        """
        Test mean presence time grouped by weekday for given user.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/666')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.content_type, 'text/html')
        
        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
    
    def test_presence_weekday_view(self):
        """
        Test total presence time for given user grouped by weekday.
        """
        resp = self.client.get('/api/v1/presence_weekday/666')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.content_type, 'text/html')
        
        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        


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
    
    def test_group_by_weekday(self):
        """
        Test grouping by weekday.
        """
        data = utils.get_data()
        grouped_by_weekday = utils.group_by_weekday(data[10])
        self.assertIsInstance(grouped_by_weekday, list)
        with self.assertRaises(TypeError):
            utils.group_by_weekday({'first': 123, 'second': '123'})
    
    def test_seconds_since_midnight(self):
        """
        Test calculating seconds since midnight.
        """
        example_times = [
                         [datetime.time(17, 30, 15), 63015],  # 17 * 3600 + 30 * 60 + 15 = 63015
                         [datetime.time(11, 20, 0), 40800],    # 11 * 3600 + 20 * 60 + 0  = 40800
                         ]
        
        for example_time in example_times:
            self.assertEqual(utils.seconds_since_midnight(example_time[0]),
                             example_time[1])
        
        with self.assertRaises(AttributeError):
            utils.seconds_since_midnight('some string')
    
    def test_interval(self):
        """
        Test calculating amount of time between two datetime.time objects.
        """
        self.assertEqual(utils.interval(
                                        datetime.time(11, 20, 0),
                                        datetime.time(17, 30, 15),
                                        ),
                         22215)
        with self.assertRaises(AttributeError):
            utils.interval('not a datetime.time', 'object')
    
    def test_mean(self):
        """
        Test returning arithmetic mean or zero if empty.
        """
        self.assertEqual(utils.mean([1,39,22,2]), 16)
        self.assertEqual(utils.mean([]), 0)
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
