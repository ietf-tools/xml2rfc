# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

# Internal utitlity functions.  Not meant for public usage.

import re
import textwrap
try:
    from urllib.request import FancyURLopener
except ImportError:
    from urllib import FancyURLopener
try:
    import debug
    assert debug
except ImportError:
    pass

import xml2rfc.log


class StrictUrlOpener(FancyURLopener):
    """ Override urllib opener to throw exceptions on 404s """
    def __init__(self, *args, **kwargs):
        FancyURLopener.__init__(self, *args, **kwargs)
      
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
            r'(?<=[\w\!\"\'\&\.\,\?])-{2,}(?=\w))'    # em-dash
            r'(?!&#8288;)')                           # UNLESS &wj;

        self.wordsep_re_uni = re.compile(self.wordsep_re.pattern, re.U)

        # Override end of line regex, double space after '].'
        self.sentence_end_re = re.compile(r'[A-Za-z0-9\>\]\)\"\']'  # letter, end parentheses
                            r'[\.\!\?]'     # sentence-ending punct.
                            r'[\"\'\)\]]?'  # optional end-of-quote, end parentheses
                            r'\Z'           # end of chunk
                            )

        # Exceptions which should not be treated like end-of-sentence
        self.not_sentence_end_re = re.compile(
            # start of string or non-alpha character
            r'(^|[^A-Za-z])'
            r'('
            # Single uppercase letter, dot, enclosing parentheses or quotes
            r'[A-Za-z]\.[\]\)\'"]*'
            # Tla with leading uppercase, and special cases
            # (Note: v1 spelled out Fig, Tbl, Mrs, Drs, Rep, Sen, Gov, Rev, Gen, Col, Maj and Cap,
            #  but those are redundant with the Tla regex.)
            r'|([A-Z][a-z][a-z]|Eq|[Cc]f|vs|resp|viz|ibid|[JS]r|M[rs]|Messrs|Mmes|Dr|Profs?|St|Lt)\.'
            r')\Z' # trailing dot, end of group and end of chunk
            )

        # Start of next sentence regex
        self.sentence_start_re = re.compile("^[\"'([]*[A-Z]")

        # XmlCharRef replacements that occur AFTER line breaking logic
        self.post_break_replacements = {
            '&#160;': ' ',   # nbsp
            '&#8209;': '-',  # nbhy
            '&#8288;': '',   # wj
        }

        self.break_on_hyphens = True


    def _fix_sentence_endings(self, chunks):
        """_fix_sentence_endings(chunks : [string])

        Correct for sentence endings buried in 'chunks'.  Eg. when the
        original text contains "... foo.\nBar ...", munge_whitespace()
        and split() will convert that to [..., "foo.", " ", "Bar", ...]
        which has one too few spaces; this method simply changes the one
        space to two.
        """
        i = 0
        patsearch = self.sentence_end_re.search
        skipsearch = self.not_sentence_end_re.search
        startsearch = self.sentence_start_re.search
        while i < len(chunks)-2:
            if (chunks[i+1] == " " and patsearch(chunks[i])
                                  and skipsearch(chunks[i])==None
                                  and startsearch(chunks[i+2])):
                chunks[i+1] = "  "
                i += 2
            else:
                i += 1

    def replace(self, text):
        """ Replace control entities with the proper character 
            after breaking has occured.
        """
        for key, val in self.post_break_replacements.items():
            text = re.sub(re.escape(key), val, text)
        return text

    def wrap(self, text, initial_indent='', subsequent_indent='',
        fix_doublespace=True, fix_sentence_endings=True, drop_whitespace=True):
        """ Mirrored implementation of wrap which replaces characters properly
            also lets you easily specify indentation on the fly
        """
        # Set indentation
        self.initial_indent = initial_indent
        self.subsequent_indent = subsequent_indent
        self.fix_sentence_endings = fix_sentence_endings
        self.drop_whitespace = drop_whitespace

        # Original implementation
        text = self._munge_whitespace(text)

        # Maybe remove double (and more) spaces, except when they might be between sentences
        if fix_doublespace:
            text = re.sub("([^].!?])  +", r"\1 ", text)
            text = re.sub("([.!?])   +", r"\1  ", text)

        # prevent breaking "Section N.N" and "Appendix X.X"
        text = re.sub("(Section|Appendix) ", r"\1&#160;", text)

        # Replace some characters after splitting has occured
        parts = [ self.replace(s) for s in self._split(text) ]
        chunks = []
        max_word_len = self.width - len(subsequent_indent)
        for chunk in parts:
            if len(chunk) > max_word_len:
                bits = self._split(chunk)
                chunks += bits
            else:
                chunks += [ chunk ]
        
        # Original implementation
        if self.fix_sentence_endings:
            self._fix_sentence_endings(chunks)
        return self._wrap_chunks(chunks)

    def fill(self, *args, **kwargs):
        return "\n".join(self.wrap(*args, **kwargs))


def justify_inline(left_str, center_str, right_str, width=72):
    """ Takes three string arguments and outputs a single string with the
        arguments left-justified, centered, and right-justified respectively.

        Raises a warning if the combined length of the three strings is
        greater than the width, and trims the longest string
    """
    strings = [left_str.strip(), center_str.strip(), right_str.strip()]
    sumwidth = sum( [len(s) for s in strings] )
    if sumwidth > width:
        # Trim longest string
        longest_index = strings.index(max(strings, key=len))
        xml2rfc.log.warn('The inline string was truncated because it was ' \
                         'too long:\n  ' + strings[longest_index])
        strings[longest_index] = strings[longest_index][:-(sumwidth - width)]

    if len(strings[1]) % 2 == 0:
        center = strings[1].center(width)
    else:
        center = strings[1].center(width+1)        
    right = strings[2].rjust(width)
    output = list(strings[0].ljust(width))
    for i, char in enumerate(output):
        if center[i] != ' ':
            output[i] = center[i]
        elif right[i] != ' ':
            output[i] = right[i]
    return ''.join(output)

def formatXmlWhitespace(tree):
    """ Traverses an lxml.etree ElementTreeand properly formats whitespace
    
        We replace newlines with single spaces, unless it ends with a
        period then we replace the newline with two spaces.
    """
    for element in tree.iter():
        # Preserve formatting on artwork
        if element.tag != 'artwork':
            if element.text is not None:
                element.text = re.sub('\s*\n\s*', ' ', \
                               re.sub('\.\s*\n\s*', '.  ', \
                               element.text.lstrip()))

            if element.tail is not None:
                element.tail = re.sub('\s*\n\s*', ' ', \
                               re.sub('\.\s*\n\s*', '.  ', \
                               element.tail))


# ----------------------------------------------------------------------
# Base conversions.
# From http://tech.vaultize.com/2011/08/python-patterns-number-to-base-x-and-the-other-way/

DEFAULT_DIGITS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
 
def num_to_baseX(num, digits=DEFAULT_DIGITS):
   if num < 0: return '-' + num_to_baseX(-num)
   if num == 0: return digits[0]
   X = len(digits)
   s = ''
   while num > 0:
        s = digits[num % X] + s
        num //= X
 
   return s
 
def baseX_to_num(s, digits=DEFAULT_DIGITS):
   if s[0] == '-': return -1 * baseX_to_num(s[1:])
   ctopos = dict([(c, pos) for pos, c in enumerate(digits)])
   X = len(digits)
   num = 0
   for c in s: num = num * X + ctopos[c]
   return num

# ----------------------------------------------------------------------
# Use the generic base conversion to create list letters

def int2letter(num):
    return num_to_baseX(num, "abcdefghijklmnopqrstuvwxyz")

def int2roman(number):
    numerals = { 
        1 : "i", 
        4 : "iv", 
        5 : "v", 
        9 : "ix", 
        10 : "x", 
        40 : "xl", 
        50 : "l", 
        90 : "xc", 
        100 : "c", 
        400 : "cd", 
        500 : "d", 
        900 : "cm", 
        1000 : "m" 
    }
    result = ""
    for value, numeral in sorted(numerals.items(), reverse=True):
        while number >= value:
            result += numeral
            number -= value
    return result


def urlkeep(text):
    """ Insert word join XML entities on forward slashes and hyphens
        in a URL so that it stays on one line
    """
    wj_char = '&#8288;'
    def replacer(match):
        return match.group(0).replace('/', '/' + wj_char) \
                             .replace('-', '-' + wj_char)
    return re.sub('(?<=http:)\S*', replacer, text)


def safeReplaceUnicode(tree):
    """ Traverses an lxml.etree ElementTree and replaces unicode characters 
        with the proper equivalents specified in rfc2629-xhtml.ent.

        Writers should call this method if the entire RFC document needs to
        be ascii formatted
    """
    for element in tree.iter():
        if element.text:
            try:
                element.text = element.text.encode('ascii')
            except UnicodeEncodeError:
                element.text = _replace_unicode_characters(element.text)
        if element.tail:
            try:
                element.tail = element.tail.encode('ascii')
            except UnicodeEncodeError:
                element.tail = _replace_unicode_characters(element.tail)
        for key in element.attrib.keys():
            try:
                element.attrib[key] = element.attrib[key].encode('ascii')
            except UnicodeEncodeError:
                element.attrib[key] = \
                _replace_unicode_characters(element.attrib[key])


def _replace_unicode_characters(str):
    for key, val in _unicode_replacements.items():
        str = re.sub(re.escape(key), val, str)
    try:
        str = str.encode('ascii')
    except UnicodeEncodeError:
        str = str.encode('ascii', 'xmlcharrefreplace')
        # xml2rfc.log.warn('Unicode character(s) not replaced in string:\n  ' + \
                         # str)
    return str


# Ascii representations of unicode chars from rfc2629-xhtml.ent
# Auto-generated from comments in rfc2629-xhtml.ent
_unicode_replacements = {
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
}
