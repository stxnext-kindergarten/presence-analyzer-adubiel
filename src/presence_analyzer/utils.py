# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""

import csv

from json import dumps
from functools import wraps
from datetime import datetime

import logging

from lxml import etree
from flask import Response
from presence_analyzer.main import app

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        """
        This docstring will be overridden by @wraps decorator.
        """
        return Response(
            dumps(function(*args, **kwargs)),
            mimetype='application/json'
        )
    return inner


def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {})[date] = {'start': start, 'end': end}

    return data


def get_xml_data():
    """
    Extracts data about users from XML.

    It creates structure like this:
    data = {
        'user_id': {
            'avatar': 'https://intranet.stxnext.pl/api/images/users/141',
            'name': 'Adam P.',
        },
        'user_id': {
            'avatar': 'https://intranet.stxnext.pl/api/images/users/176',
            'name': 'Adrian K.',
        },
    }
    """
    data = {}
    with open(app.config['DATA_XML'], 'r') as xmlfile:
        xmldata_tree_object = etree.parse(xmlfile)
        data_xml = xmldata_tree_object.getroot()

        server_data = {server.tag: server.text for server in data_xml[0]}
        base_path = server_data['protocol'] + '://' + server_data['host']

        for user in data_xml[1]:
            user_data = {user_info.tag: user_info.text for user_info in user}
            data[user.attrib['id']] = {
                'avatar': base_path + user_data['avatar'],
                'name': user_data['name'],
            }

    return data


def group_by_weekday(items):
    """
    Groups presence entries by weekday.

    Args:
        items (dict): data structure for user like:
            {
                datetime.date(2013, 10, 1): {
                    'start': datetime.time(9, 0, 0),
                    'end': datetime.time(17, 30, 0),
                },
                datetime.date(2013, 10, 2): {
                    'start': datetime.time(8, 30, 0),
                    'end': datetime.time(16, 45, 0),
                },
            }

    Returns:
        list: intervals (end - start) grouped by weekday.
    """
    result = [[], [], [], [], [], [], []]  # one list for every day in week
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def group_start_end(items):
    """
    Groups presence start and end entries by weekday.

    Args:
        items (dict): data structure for user like:
            {
                datetime.date(2013, 10, 1): {
                    'start': datetime.time(9, 0, 0),
                    'end': datetime.time(17, 30, 0),
                },
                datetime.date(2013, 10, 2): {
                    'start': datetime.time(8, 30, 0),
                    'end': datetime.time(16, 45, 0),
                },
            }

    Returns:
        list: list of weekdays. Each weekday includes two sublists with
            intervals:
            [0] - seconds from midnight to start
            [1] - seconds from midnight to end.
    """
    result = [[[], []] for __ in range(7)]  # one list for every day in week
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()][0].append(seconds_since_midnight(start))
        result[date.weekday()][1].append(seconds_since_midnight(end))
    return result


def mean_start_stop(items):
    """
    Counts mean start and end time by weekday.

    Args:
        items (dict): data structure for user like:
            {
                datetime.date(2013, 10, 1): {
                    'start': datetime.time(9, 0, 0),
                    'end': datetime.time(17, 30, 0),
                },
                datetime.date(2013, 10, 2): {
                    'start': datetime.time(8, 30, 0),
                    'end': datetime.time(16, 45, 0),
                },
            }

    Returns:
        list: list of weekdays. Each weekday includes dict with
            mean time for 'Start' and 'End'.
    """
    items_grouped = group_start_end(items)
    result = []
    for starts, stops in items_grouped:
        start = mean(starts)
        stop = mean(stops)
        result.append({
            'Start': start,
            'End': stop
        })
    return result


def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.

    Args:
        time(datetime.time): just time.

    Returns:
        int: calculated time in seconds.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.

    Args:
        start (datetime.time): time of starting work
        end (datetime.time): time of ending work

    Returns:
        int: time in seconds between end and start.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.

    Args:
        items (list): list of times.

    Returns:
        float: arithmetic mean.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0
