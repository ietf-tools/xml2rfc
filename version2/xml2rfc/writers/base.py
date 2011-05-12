class XmlRfcWriter:
    """ Base class for all writers """
    
    def __init__(self, xmlrfc):
        # We will refer to the XmlRfc document root as 'r'
        self.r = xmlrfc.getroot()

    def write(self, filename):
        raise NotImplementedError('write() must be overridden')