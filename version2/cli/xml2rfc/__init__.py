
NAME    = 'xml2rfc'
VERSION = (2, 0, 8)
CACHES  = ['/var/cache/xml2rfc', '~/.cache/xml2rfc']  # Ordered by priority
CACHE_PREFIX = '_HTTP_CACHE'

from xml2rfc.parser import *
from xml2rfc.writers import *
