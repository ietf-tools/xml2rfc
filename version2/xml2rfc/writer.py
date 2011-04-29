""" Writer classes to output rfc data to various formats """

def justify_inline(left_str, center_str, right_str, width=80):
    """ Takes three string arguments and outputs a single string with
        the arguments left-justified, centered, and right-justified
        respectively.
        
        Throws an exception if the combined length of the three strings
        is greater than the width.
    """

    if (len(left_str) + len(center_str) + len(right_str)) > width:
        raise ValueError("The given strings are greater than a width of: "\
                                                            + str(width))
    else:
        str = left_str + ' '*((width/2)-len(center_str)/2-len(left_str)) \
          + center_str + ' '*((width/2)-len(center_str)/2-len(right_str)) \
          + right_str
        return str


class XmlRfcWriter:
    """ Base class for all writers """
    rfctree = None
    
    def __init__(self, rfctree):
        self.rfctree = rfctree
        
    def write(self, filename):
        raise NotImplementedError('write() must be overridden')

class RawTextRfcWriter(XmlRfcWriter):
    pass