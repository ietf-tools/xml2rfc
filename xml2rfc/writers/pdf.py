# Copyright The IETF Trust 2018, All Rights Reserved
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

import datetime
import os

import weasyprint

from xml2rfc.writers.base import default_options, BaseV3Writer
from xml2rfc.writers.html import HtmlWriter

try:
    from xml2rfc import debug, log
    debug.debug = True
except ImportError:
    pass

class PdfWriter(BaseV3Writer):

    def __init__(self, xmlrfc, quiet=None, options=default_options, date=datetime.date.today()):
        super(PdfWriter, self).__init__(xmlrfc, quiet=quiet, options=options, date=date)

    def get_serif_fonts(self):
        """

        This translates from the official unicode script names to the fonts
        actually available in the Noto font family.  The set of fonts known
        to have serif versions is up-to-date as of 05 Dec 2018, for the
        Noto font pack built on 2017-10-24, available as
        https://noto-website-2.storage.googleapis.com/pkgs/Noto-unhinted.zip
        
        """
        noto_serif = "'Noto Serif'"
        fontname = {
            'Latin':    'Noto Serif',
            'Common':   'Noto Serif',
            'Greek':    'Noto Serif',
            'Hebrew':   'Noto Serif',
            'Cyrillic': 'Noto Serif',
            'Tai_Viet': 'Noto Serif',
            # Script names that don't match font names
            'Han':      'Noto Serif CJK SC',
            'Hangul':   'Noto Serif CJK KR',
            'Hiragana': 'Noto Serif CJK JP',
            'Katakana': 'Noto Serif CJK JP',
            # Script names available in Serif
            'Armenian':	'Noto Serif Armenian',
            'Bengali':	'Noto Serif Bengali',
            'Devanagari':'Noto Serif Devanagari',
            'Display':	'Noto Serif Display',
            'Ethiopic':	'Noto Serif Ethiopic',
            'Georgian':	'Noto Serif Georgian',
            'Gujarati':	'Noto Serif Gujarati',
            'Hebrew':	'Noto Serif Hebrew',
            'Kannada':	'Noto Serif Kannada',
            'Khmer':	'Noto Serif Khmer',
            'Lao':	'Noto Serif Lao',
            'Malayalam':'Noto Serif Malayalam',
            'Myanmar':	'Noto Serif Myanmar',
            'Sinhala':	'Noto Serif Sinhala',
            'Tamil':	'Noto Serif Tamil',
            'Telugu':	'Noto Serif Telugu',
            'Thai':	'Noto Serif Thai',
            # Other names may be available in Sans
        }
        fonts = set()
        scripts = self.root.get('scripts').split(',')
        for script in scripts:
            if script in fontname:
                fonts.add("'%s'" % fontname[script])
            else:
                script = script.replace('_', ' ')
                fonts.add("'Noto Sans %s'" % script)
        fonts -= set([ noto_serif, ])
        fonts = [ noto_serif, ] + list(fonts)
        return fonts

    def write(self, filename):
        self.filename = filename

        self.options.no_css = True
        htmlwriter = HtmlWriter(self.xmlrfc, quiet=True, options=self.options, date=self.date)
        html = htmlwriter.html()

        writer = weasyprint.HTML(string=html)

        cssin  = self.options.css or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'xml2rfc.css')
        font_config = weasyprint.fonts.FontConfiguration()
        css = weasyprint.CSS(cssin, font_config=font_config)

        # page info
        fonts = self.get_serif_fonts()
        page_info = {
            'top-left': self.page_top_left(),
            'top-center': self.page_top_center(),
            'top-right': self.page_top_right(),
            'bottom-left': self.page_bottom_left(),
            'bottom-center': self.page_bottom_center(),
            'fonts': ', '.join(fonts),
        }
        page_css_text = page_css_template.format(**page_info)
        page_css = weasyprint.CSS(string=page_css_text, font_config=font_config)

        res = writer.write_pdf(filename, stylesheets=[ css, page_css ])

        if not self.options.quiet:
            log.write('Created file', filename)


page_css_template = """
@media print {{
  body {{
    font-family: {fonts}, 'Times New Roman', Times, serif;
    width: 100%;
  }}
  @page {{
    size: A4;
    font-size: 12px;

    border-top: solid 1px #ccc;
    padding-top: 18px;

    padding-bottom: 24px;
    border-bottom: solid 1px #ccc;
    margin-bottom: 45mm;

    @top-left {{
      content: '{top-left}';
      vertical-align: bottom;
      border-bottom: 0px;
      margin-bottom: 1em;
    }}
    @top-center {{
      content: '{top-center}';
      vertical-align: bottom;
      border-bottom: 0px;
      margin-bottom: 1em;
    }}
    @top-right {{
      content: '{top-right}';
      vertical-align: bottom;
      border-bottom: 0px;
      margin-bottom: 1em;
    }}
    @bottom-left {{
      content: '{bottom-left}';
      vertical-align: top;
      border-top: 0px;
      margin-top: 1em;
    }}
    @bottom-center {{
      content: '{bottom-center}';
      vertical-align: top;
      border-top: 0px;
      margin-top: 1em;
    }}
    @bottom-right {{
      content: 'Page ' counter(page);
      vertical-align: top;
      border-top: 0px;
      margin-top: 1em;
    }}
  }}
}}
"""
