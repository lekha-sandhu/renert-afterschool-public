from flask import url_for
from jinja2.utils import markupsafe
from root import app
from math import floor
from datetime import datetime
from random import randint
from itertools import groupby
import timeago
import pytz
MST = pytz.timezone('America/Edmonton')
tz = MST

# Example of a custom jinja2 template.
# can be used from inside the HTML templates like so:
#   {{ var | foobar }}
@app.template_filter('foobar')
def fooabr_format_filter(s):
    if s is None:
        return ''
    s = float(s)
    return "%.2f" % s


@app.template_filter('ordinal_suffix')
def ordinal_suffix(day):
    if day == 0 or 3 < day < 21 or 23 < day < 31:
        return 'th'
    else:
        return {1: 'st', 2: 'nd', 3: 'rd'}[day % 10]

@app.template_filter('presentable_date')
def presentable_date(d):
    dow = d.strftime("%A")
    month = d.strftime("%B")
    s = "%s, %s %d%s, %d" % ( dow, month, d.day, ordinal_suffix(d.day), d.year )
    return s


@app.template_filter('time_ago_minutes')
def time_ago_minutes(utc_timestamp):
    delta = datetime.now(MST) - utc_timestamp
    m = floor(delta.seconds/60)
    return m

@app.template_filter('time_ago_days')
def time_ago_minutes(utc_timestamp):
    delta = datetime.now(MST) - utc_timestamp
    if delta.days == 0:
        return "today"
    if delta.days == -1:
        return "yesterday"
    return timeago.format(delta)

@app.template_global('utc_now')
def utc_now():
    return datetime.utcnow()

@app.template_global('local_now')
def local_now():
    return datetime.now().astimezone(tz=MST)


@app.template_filter('flatten')
def flatten(mylist, levels=None):

    def is_sequence(x):
        return isinstance(x,list)

    ret = []
    for element in mylist:
        if element in (None, 'None', 'null'):
            # ignore undefined items
            break
        elif is_sequence(element):
            if levels is None:
                ret.extend(flatten(element))
            elif levels >= 1:
                # decrement as we go down the stack
                ret.extend(flatten(element, levels=(int(levels) - 1)))
            else:
                ret.append(element)
        else:
            ret.append(element)

    return ret

@app.template_global('raise')
def jinja2_raise_error(s):
    raise(RuntimeException("Jinja2 Custom error:" + str(s)))


@app.template_global('to_local_time')
def jinja2_to_local_time(d):
    return d.astimezone(tz=MST)

@app.template_global('randint')
def jinja2_randint(x,y):
    return randint(x,y)


@app.template_global('server_local_time')
def jinaj2_server_local_time():
    return datetime.now(tz)


@app.template_global('birthday_delta')
def jinaj2_birthday_delta(dob):
    today = datetime.now(tz).date()
    bd = date(today.year, dob.month, dob.day)
    return timeago.format( today - bd )


@app.template_filter('date_ago')
def jinaj2_date_ago(d):
    today = datetime.now(tz).date()
    bd = date(d.year, d.month, d.day) # incase 'd' is a datetime, convert to date
    return timeago.format( today - bd )


@app.template_filter('timedelta_to_hh_mm_ss')
def jinaj2_timedelta_to_hh_mm(d):
    if not d:
        return ''
    total_minutes = d.total_seconds() // 60 ;
    hours = total_minutes // 60 ;
    minutes = total_minutes % 60 ;
    seconds = d.total_seconds() % 60 ;
    s = "%02d:%02d:%02d" % ( hours, minutes, seconds )
    return s

@app.template_filter('timedelta_to_pretty_hms')
def jinaj2_timedelta_to_pretty_hms(d):
    if not d:
        return ''
    total_minutes = d.total_seconds() // 60 ;
    hours = total_minutes // 60 ;
    minutes = total_minutes % 60 ;
    seconds = d.total_seconds() % 60 ;
    s = ""
    if hours>0:
        s += "%dh" % hours

    if minutes > 0 or len(s)>0:
        if len(s)>0:
            # Need zero padding
            s += "%02dm" % minutes
        else:
            s += "%dm" % minutes

    if seconds > 0 or len(s)>0:
        if len(s)>0:
            # Need zero padding
            s += "%02ds" % seconds
        else:
            s += "%ds" % seconds

    return s

@app.template_filter('stable_groupby')
def jinaj2_stable_groupby(data, attr):
    """
    'data' must be a list-of-dict .
    """
    result = []

    for k, g in groupby(data, lambda x: x[attr]):
        items = list(g)      # Store group iterator as a list
        result.append( (k, items) )

    return result
