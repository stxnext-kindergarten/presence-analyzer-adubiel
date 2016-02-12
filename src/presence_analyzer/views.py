# -*- coding: utf-8 -*-
"""
Defines views.
"""
# pylint: disable=unused-wildcard-import, wildcard-import
import calendar
import logging
from flask import redirect, abort, render_template
from jinja2 import TemplateNotFound

from presence_analyzer.main import app
from presence_analyzer import utils

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect('/presence_weekday.html')


@app.route('/api/v1/users', methods=['GET'])
@utils.jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = utils.get_xml_data()

    return [
        {'user_id': i, 'name': data[i]['name']}
        for i in data.keys()
    ]


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@utils.jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = utils.get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = utils.group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], utils.mean(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@utils.jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = utils.get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = utils.group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], sum(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@utils.jsonify
def presence_start_end(user_id):
    """
    Return presence mean start and end times for given user grouped by weekday.
    """
    data = utils.get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = utils.mean_start_stop(data[user_id])
    result = [
        (calendar.day_abbr[weekday], day['Start'], day['End'])
        for weekday, day in enumerate(weekdays)
    ]
    return result


@app.route('/<string:temp_name>', methods=['GET'])
def render_all(temp_name):
    """
    Render templates.
    """
    try:
        return render_template(temp_name, selected=temp_name)
    except TemplateNotFound:
        return render_template('notFound.html')


@app.route('/api/v1/user_avatar/<int:user_id>', methods=['GET'])
@utils.jsonify
def user_avatar(user_id):
    """
    Return path to users avatar.
    """
    data = utils.get_xml_data()
    user_id = str(user_id)
    return data[user_id]['avatar']
