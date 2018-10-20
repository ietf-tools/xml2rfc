 # Copyright The IETF Trust 2017, All Rights Reserved
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

try:
    import debug
    debug.debug = True
except ImportError:
    pass

def short_author_name(a):
    initials = a.get('initials')
    surname  = a.get('surname')
    if initials or surname:
        if initials and not initials.endswith('.'):
            initials += '.'
        short = ' '.join( n for n in [initials, surname] if n )
    else:
        fullname = a.get('fullname') or ''
        if fullname and len(fullname.split())>1:
            parts = fullname.split()
            initials = ' '.join([ "%s."%n[0].upper() for n in parts[:-1] ])
            surname  = parts[-1]
            short = "%s %s" % (initials, surname)
        else:
            short = fullname
    return short

def short_author_ascii_name(a):
    initials = a.get('asciiInitials')
    surname  = a.get('asciiSurname')
    if initials or surname:
        if initials and not initials.endswith('.'):
            initials += '.'
        short = ' '.join( n for n in [initials, surname] if n )
    else:
        fullname = a.get('asciiFullname')
        if fullname and len(fullname.split())>1:
            parts = fullname.split()
            initials = ' '.join([ "%s."%n[0].upper() for n in parts[:-1] ])
            surname  = parts[-1]
            short = "%s %s" % (initials, surname)
        else:
            short = fullname
    return short or short_author_name(a)

def full_author_name(a):
    fullname = a.get('fullname')
    if fullname:
        return fullname
    else:
        initials = a.get('initials')
        surname  = a.get('surname')
        if initials and not initials.endswith('.'):
            initials += '.'
        return ' '.join( n for n in [initials, surname] if n )

def full_author_ascii_name(a):
    fullname = a.get('asciiFullname')
    if fullname:
        full = fullname
    else:
        initials = a.get('asciiInitials') or a.get('initials')
        surname  = a.get('asciiSurname')  or a.get('surname')
        if initials and not initials.endswith('.'):
            initials += '.'
        full = ' '.join( n for n in [initials, surname] if n )
    return full or full_author_name(a)

def short_org_name(a):
    org = a.find('organization')
    return org.get('abbrev') or org.text or '' if org != None else ''

def short_org_ascii_name(a):
    org = a.find('organization')
    if org == None:
        return ''
    org_name = (a.get('asciiAbbrev') or org.get('ascii')
                or org.get('abbrev') or org.text or '')
    return org_name
    
def full_org_name(a):
    org = a.find('organization')
    return org.text or '' if org != None else ''

def full_org_ascii_name(a):
    org = a.find('organization')
    if org == None:
        return ''
    org_name = a.get('ascii') or org.text or ''
    return org_name
    
