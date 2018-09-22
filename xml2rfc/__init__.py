

# Static values
__version__  = '2.10.3'
NAME         = 'xml2rfc'
VERSION      = [ int(i) if i.isdigit() else i for i in __version__.split('.') ]
CACHES       = ['/var/cache/xml2rfc', '~/.cache/xml2rfc']  # Ordered by priority
CACHE_PREFIX = ''
NET_SUBDIRS  = ['bibxml', 'bibxml2', 'bibxml3', 'bibxml4', 'bibxml5']

from xml2rfc.parser import  XmlRfcError, CachingResolver, XmlRfcParser, XmlRfc
from xml2rfc.writers import BaseRfcWriter, RawTextRfcWriter, PaginatedTextRfcWriter
from xml2rfc.writers import HtmlRfcWriter, NroffRfcWriter, ExpandedXmlWriter
from xml2rfc.writers import RfcWriterError, V2v3XmlWriter, PrepToolWriter, TextWriter

__all__ = ['XmlRfcError', 'CachingResolver', 'XmlRfcParser', 'XmlRfc',
           'BaseRfcWriter', 'RawTextRfcWriter', 'PaginatedTextRfcWriter',
           'HtmlRfcWriter', 'NroffRfcWriter', 'ExpandedXmlWriter',
           'RfcWriterError', 'V2v3XmlWriter', 'PrepToolWriter', 'TextWriter', ]

