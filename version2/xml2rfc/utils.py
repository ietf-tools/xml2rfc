# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

# Internal utitlity functions.  Not meant for public usage.

import re
import textwrap
import string
import urllib

import xml2rfc.log


class StrictUrlOpener(urllib.FancyURLopener):
    """ Override urllib opener to throw exceptions on 404s """
    def __init__(self, *args, **kwargs):
        urllib.FancyURLopener.__init__(self, *args, **kwargs)
      
    def http_error_default(self, url, fp, errcode, errmsg, headers):
        raise IOError('Document not found')


class MyTextWrapper(textwrap.TextWrapper):
    """ Subclass that overrides a few things in the standard implementation """
    def __init__(self, **kwargs):
        textwrap.TextWrapper.__init__(self, **kwargs)

        # Override wrapping regex, preserve '/' before linebreak
        self.wordsep_re = re.compile(
            r'(/|'                                    # a forward slash  
            r'\s+|'                                   # any whitespace
            r'[^\s\w]*\w+[^0-9\W]-(?=\w+[^0-9\W])|'   # hyphenated words
            r'(?<=[\w\!\"\'\&\.\,\?])-{2,}(?=\w))')   # em-dash

        self.wordsep_re_uni = re.compile(self.wordsep_re.pattern, re.U)

        # Override end of line regex, double space after '].'
        self.sentence_end_re = \
                  re.compile(r'[%s|\]|"]'      # lowercase, bracket, or quote
                             r'[\.\!\?]'       # sentence-ending punct.
                             r'[\"\']?'        # optional end-of-quote
                             r'\Z'             # end of chunk
                             % string.lowercase)

    def wrap(self, text, initial_indent='', subsequent_indent=''):
        """ Wrapper method to dynamically change indentation strings """
        self.initial_indent = initial_indent
        self.subsequent_indent = subsequent_indent
        return textwrap.TextWrapper.wrap(self, text)      

    def fill(self, text, initial_indent='', subsequent_indent=''):
        """ Wrapper method to dynamically change indentation strings """
        self.initial_indent = initial_indent
        self.subsequent_indent = subsequent_indent
        return textwrap.TextWrapper.fill(self, text)


def parse_pi(text):
    """ Parse the text from a processing instruction into key-value pairs """
    # Split text in the format 'key="val"'
    chunks = re.split(r'=[\'"]([^\'"]*)[\'"]', text)
    # Create pairs from this flat list, discard last element if odd
    return zip(chunks[::2], chunks[1::2])


def justify_inline(left_str, center_str, right_str, width=72):
    """ Takes three string arguments and outputs a single string with the
        arguments left-justified, centered, and right-justified respectively.

        Raises a warning if the combined length of the three strings is
        greater than the width, and trims the longest string
    """
    strings = [left_str, center_str, right_str]
    sumwidth = sum(map(len, strings))
    if sumwidth > width:
        # Trim longest string
        longest_index = strings.index(max(strings, key=len))
        xml2rfc.log.warn('The inline string was truncated because it was ' \
                         'too long:\n  ' + strings[longest_index])
        strings[longest_index] = strings[longest_index][:-(sumwidth - width)]

    center = strings[1].center(width)
    right = strings[2].rjust(width)
    output = list(strings[0].ljust(width))
    for i, char in enumerate(output):
        if center[i] != ' ':
            output[i] = center[i]
        elif right[i] != ' ':
            output[i] = right[i]
    return ''.join(output)


def replace_unicode(str):
    for key, val in unicode_replacements.items():
        str = re.sub(re.escape(key), val, str)
    try:
        str = str.encode('ascii')
    except UnicodeEncodeError:
        str = str.encode('ascii', 'xmlcharrefreplace')
        xml2rfc.log.warn('Unicode character(s) not replaced in string:\n  ' + \
                         str)
    return str


# Ascii representations of unicode chars from rfc2629-xhtml.ent
# Auto-generated from comments in rfc2629-xhtml.ent
unicode_replacements = {'\xa0': ' ',
                        '\xa1': '!',
                        '\xa2': '[cents]',
                        '\xa3': 'GBP',
                        '\xa4': '[currency units]',
                        '\xa5': 'JPY',
                        '\xa6': '|',
                        '\xa7': 'S.',
                        '\xa9': '(C)',
                        '\xaa': 'a',
                        '\xab': '<<',
                        '\xac': '[not]',
                        '\xae': '(R)',
                        '\xaf': '_',
                        '\xb0': 'o',
                        '\xb1': '+/-',
                        '\xb2': '^2',
                        '\xb3': '^3',
                        '\xb4': "'",
                        '\xb5': '[micro]',
                        '\xb6': 'P.',
                        '\xb7': '.',
                        '\xb8': ',',
                        '\xb9': '^1',
                        '\xba': 'o',
                        '\xbb': '>>',
                        '\xbc': '1/4',
                        '\xbd': '1/2',
                        '\xbe': '3/4',
                        '\xbf': '?',
                        '\xc0': 'A',
                        '\xc1': 'A',
                        '\xc2': 'A',
                        '\xc3': 'A',
                        '\xc4': 'Ae',
                        '\xc5': 'Ae',
                        '\xc6': 'AE',
                        '\xc7': 'C',
                        '\xc8': 'E',
                        '\xc9': 'E',
                        '\xca': 'E',
                        '\xcb': 'E',
                        '\xcc': 'I',
                        '\xcd': 'I',
                        '\xce': 'I',
                        '\xcf': 'I',
                        '\xd0': '[ETH]',
                        '\xd1': 'N',
                        '\xd2': 'O',
                        '\xd3': 'O',
                        '\xd4': 'O',
                        '\xd5': 'O',
                        '\xd6': 'Oe',
                        '\xd7': 'x',
                        '\xd8': 'Oe',
                        '\xd9': 'U',
                        '\xda': 'U',
                        '\xdb': 'U',
                        '\xdc': 'Ue',
                        '\xdd': 'Y',
                        '\xde': '[THORN]',
                        '\xdf': 'ss',
                        '\xe0': 'a',
                        '\xe1': 'a',
                        '\xe2': 'a',
                        '\xe3': 'a',
                        '\xe4': 'ae',
                        '\xe5': 'ae',
                        '\xe6': 'ae',
                        '\xe7': 'c',
                        '\xe8': 'e',
                        '\xe9': 'e',
                        '\xea': 'e',
                        '\xeb': 'e',
                        '\xec': 'i',
                        '\xed': 'i',
                        '\xee': 'i',
                        '\xef': 'i',
                        '\xf0': '[eth]',
                        '\xf1': 'n',
                        '\xf2': 'o',
                        '\xf3': 'o',
                        '\xf4': 'o',
                        '\xf5': 'o',
                        '\xf6': 'oe',
                        '\xf7': '/',
                        '\xf8': 'oe',
                        '\xf9': 'u',
                        '\xfa': 'u',
                        '\xfb': 'u',
                        '\xfc': 'ue',
                        '\xfd': 'y',
                        '\xfe': '[thorn]',
                        '\xff': 'y',
                        u'\u0152': 'OE',
                        u'\u0153': 'oe',
                        u'\u0160': 'S',
                        u'\u0161': 's',
                        u'\u0178': 'Y',
                        u'\u0192': 'f',
                        u'\u02dc': '~',
                        u'\u2002': ' ',
                        u'\u2003': ' ',
                        u'\u2009': ' ',
                        u'\u2013': '-',
                        u'\u2014': '-\u002D',
                        u'\u2018': "'",
                        u'\u2019': "'",
                        u'\u201a': "'",
                        u'\u201c': '"',
                        u'\u201d': '"',
                        u'\u201e': '"',
                        u'\u2020': '*!*',
                        u'\u2021': '*!!*',
                        u'\u2022': 'o',
                        u'\u2026': '...',
                        u'\u2030': '[/1000]',
                        u'\u2032': "'",
                        u'\u2039': '<',
                        u'\u203a': '>',
                        u'\u2044': '/',
                        u'\u20ac': 'EUR',
                        u'\u2122': '[TM]',
                        u'\u2190': '<-\u002D',
                        u'\u2192': '\u002D->',
                        u'\u2194': '<->',
                        u'\u21d0': '<==',
                        u'\u21d2': '==>',
                        u'\u21d4': '<=>',
                        u'\u2212': '-',
                        u'\u2217': '*',
                        u'\u2264': '<=',
                        u'\u2265': '>=',
                        u'\u2329': '<',
                        u'\u232a': '>',

                        # rfc2629-other.ent
                        u'\u0021': '!',
                        u'\u0023': '#',
                        u'\u0024': '$',
                        u'\u0025': '%',
                        u'\u0028': '(',
                        u'\u0029': ')',
                        u'\u002a': '*',
                        u'\u002b': '+',
                        u'\u002c': ',',
                        u'\u002d': '-',
                        u'\u002e': '.',
                        u'\u002f': '/',
                        u'\u003a': ':',
                        u'\u003b': ';',
                        u'\u003d': '=',
                        u'\u003f': '?',
                        u'\u0040': '@',
                        u'\u005b': '[',
                        u'\u005c': '\\\\',
                        u'\u005d': ']',
                        u'\u005e': '^',
                        u'\u005f': '_',
                        u'\u0060': '`',
                        u'\u007b': '{',
                        u'\u007c': '|',
                        u'\u007d': '}',
                        u'\u017d': 'Z',
                        u'\u017e': 'z',
                        u'\u2010': '-',
                        u'\u2011': '-',
                        u'\u2060': '',
                        }
