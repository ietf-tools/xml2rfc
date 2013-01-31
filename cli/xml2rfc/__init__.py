
# Static values
NAME         = 'xml2rfc'
VERSION      = (2, 4, 0, )
CACHES       = ['/var/cache/xml2rfc', '~/.cache/xml2rfc']  # Ordered by priority
CACHE_PREFIX = ''
NET_SUBDIRS  = ['bibxml', 'bibxml2', 'bibxml3', 'bibxml4', 'bibxml5']

from xml2rfc.parser import *
from xml2rfc.writers import *

__version__  = '.'.join(map(str, VERSION))
