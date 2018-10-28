# Copyright The IETF Trust 2018, All Rights Reserved
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

# ----------------------------------------------------------------------
# Date operations

import calendar
import datetime
import xml2rfc


def normalize_month(month):
    if len(month) < 3:
        xml2rfc.log.error("Expected a month name with at least 3 letters, found '%s'" % (month, ))
    for i, m in enumerate(calendar.month_name):
        if m and m.lower().startswith(month.lower()):
            month = '%02d' % (i)
    if not month.isdigit():
        xml2rfc.log.error("Expected a month name, found '%s'" % (month, ))
    return month


def extract_date(e, today):
    day = e.get('day')
    month = e.get('month')
    year = e.get('year', str(today.year))
    #
    if not year.isdigit():
        xml2rfc.log.warn("Expected a numeric year, but found '%s'" % year)
        year = today.year
    year = int(year)
    if not month:
        if year == today.year:
            month = today.month
    else:
        if not month.isdigit():
            month = normalize_month(month)
        month = int(month)
    if day:
        if not day.isdigit():
            xml2rfc.log.warn("Expected a numeric day, but found '%s'" % day)
            day = today.day
        day = int(day)
    return year, month, day

def format_date_iso(year, month, day):
    if   year and month and day:
        return '%4d-%02d-%02d' % (year, month, day)
    elif year and month:
        return '%4d-%02d' % (year, month)
    elif year:
        return '%4d' % (year)

def format_date(year, month, day, legacy=False):
    if month:
        month = calendar.month_name[month]
        if day:
            if legacy:
                date = '%s %s, %s' % (month, day, year)
            else:
                date = '%s %s %s' % (day, month, year)
        else:
            date = '%s %s' % (month, year)
    else:
        date = '%s' % year
    return date


def get_expiry_date(tree, today):
    year, month, day = extract_date(tree.find('./front/date'), today)
    if not day:
        day = today.day
    exp = datetime.date(year=year, month=month, day=day) + datetime.timedelta(days=185)
    return exp
    
