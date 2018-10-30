 # Copyright The IETF Trust 2017, All Rights Reserved
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import i18naddress
import lxml.etree
import pycountry
import re
import xml2rfc.log

from xml2rfc.util.name import full_author_name, full_author_ascii_name, full_org_name, full_org_ascii_name

address_hcard_properties = {
        'name':             'fn',
        'company_name':     'org',
        'street_address':   'street-address',
        'postal_code':      'postal-code',
        'city':             'locality',
        'city_area':        'region',
        'country_area':     'region',
        'sorting_code':     'postal-code',
        'country_name':     'country-name'
}

def get_value(e, latin=True):
    if latin:
        value = e.get('ascii') or e.text or ''
    else:
        value = e.text or ''
    return value

def get_iso_country_info(e):
    country_info = None
    ascii = e.get('ascii')
    if ascii:
        name = ascii.strip()
    elif e.text:
        name = e.text.strip()
    else:
        return None
    # Special case, this is used bu unknown to pycountry
    if name == 'UK':
        name = 'United Kingdom'
    try:
        country_info = pycountry.countries.lookup(name)
    except LookupError:
        xml2rfc.log.note("Country lookup failed for %s" % (lxml.etree.tostring(e), ))
        pass
    return country_info

def get_normalized_address_info(x, latin=True):
    author = x.getparent()
    name = full_author_ascii_name(author) if latin else full_author_name(author)
    company = full_org_ascii_name(author) if latin else full_org_name(author)
    children = list(x.getchildren())
    country_info = None
    country_element = x.find('country')
    if country_element != None and country_element.text:
        country_info = get_iso_country_info(country_element)
    if not country_info:
        for i, c in enumerate(children):
            country_info = get_iso_country_info(c)
            if country_info:
                del children[i]
                country_element = c
                break
    if country_info:
        country_name = get_value(country_element, latin=latin)
        if re.match('[A-Z]{2,3}', country_name):
            country_name = country_info.name
        adr = {
                'name': name,
                'company_name': company,
                'street_address': [],
                'sorting_code': '',
                'postal_code': '',
                'city_area': '',
                'city': '',
                'country_area': '',
                'country_code': country_info.alpha_2,
                'country_name': country_name,
            }
        for c in children:
            # Some of these will overwrite data if there are multiple elements
            value = get_value(c, latin=latin)
            if   c.tag == 'street':
                adr['street_address'].append(value)
            elif c.tag == 'ext':
                adr['street_address'].append(value)
            elif c.tag == 'postalLine':
                adr['street_address'].append(value)
            elif c.tag == 'cityarea':
                adr['city_area'] = value
            elif c.tag == 'city':
                adr['city'] = value
            elif c.tag == 'region':
                adr['country_area'] = value
            elif c.tag == 'code':
                adr['postal_code'] = value
    else:
        adr = None
    return adr

# These are copied from i18address in order to remove uppercasing

def _format_address_line(line_format, address, rules):
    def _get_field(name):
        value = address.get(name, '')
        return value

    replacements = {
        '%%%s' % code: _get_field(field_name)
        for code, field_name in i18naddress.FIELD_MAPPING.items()}

    fields = re.split('(%.)', line_format)
    fields = [replacements.get(f, f) for f in fields]
    return ''.join(fields).strip()

def format_address(address, latin=False):
    rules = i18naddress.get_validation_rules(address)
    address_format = (
        rules.address_latin_format if latin else rules.address_format)
    address_line_formats = address_format.split('%n')
    address_lines = [
        _format_address_line(lf, address, rules)
        for lf in address_line_formats]
    address_lines.append(address['country_name'])
    address_lines = filter(None, address_lines)
    return '\n'.join(address_lines)
