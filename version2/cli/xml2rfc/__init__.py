
# Static values
NAME         = 'xml2rfc'
VERSION      = (2, 2, 8)
CACHES       = ['/var/cache/xml2rfc', '~/.cache/xml2rfc']  # Ordered by priority
CACHE_PREFIX = '_HTTP_CACHE'
NET_SUBDIRS  = ['bibxml', 'bibxml2', 'bibxml3', 'bibxml4', 'bibxml5']

from xml2rfc.parser import *
from xml2rfc.writers import *
