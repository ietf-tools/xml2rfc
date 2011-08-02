
NAME    = 'xml2rfc'
VERSION = (2, 0, 1)
CACHES  = ['/var/cache/xml2rfc', '~/.cache/xml2rfc']  # Ordered by priority

from xml2rfc.parser import *
from xml2rfc.writers import *
