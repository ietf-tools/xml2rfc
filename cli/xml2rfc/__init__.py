

# Static values
__version__  = '2.4.2.rc1'
NAME         = 'xml2rfc'
VERSION      = [ int(i) if i.isdigit() else i for i in __version__.split('.') ]
CACHES       = ['/var/cache/xml2rfc', '~/.cache/xml2rfc']  # Ordered by priority
CACHE_PREFIX = ''
NET_SUBDIRS  = ['bibxml', 'bibxml2', 'bibxml3', 'bibxml4', 'bibxml5']

from xml2rfc.parser import *
from xml2rfc.writers import *

