""" Writer classes to output rfc data to various formats """

def justify_inline(left_str, center_str, right_str, width=80):
    """ Takes three string arguments and outputs a single string with the 
        arguments left-justified, centered, and right-justified respectively.
        
        Throws an exception if the combined length of the three strings is 
        greater than the width.
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
    rfc = None

    def __init__(self, rfc):
        self.rfc = rfc
        
    def write(self, filename):
        raise NotImplementedError('write() must be overridden')


class RawTextRfcWriter(XmlRfcWriter):
    """ Writes to a text file, unpaginated, no headers or footers. """
    
    def write(self, filename):
        out = []
        
        # Front page, left heading
        fp_left = [self.rfc.attribs['trad_header']]
        if 'number' in self.rfc.attribs:
            fp_left.append(self.rfc.attribs['number'])
        if 'updates' in self.rfc.attribs:
            fp_left.append(self.rfc.attribs['updates'])
        if 'obsoletes' in self.rfc.attribs:
            fp_left.append(self.rfc.attribs['obsoletes'])
        if 'category' in self.rfc.attribs:
            fp_left.append(self.rfc.attribs['category'])
        
        # Front page, right heading
        fp_right = []
        for author in self.rfc['front']['author']:
            fp_right.append(author.attribs['initials'] + ' ' + \
                            author.attribs['surname'])
            if 'organization' in author:
                fp_right.append(author['organization'].text)
        date = self.rfc['front']['date']
        fp_right.append(date.attribs['month'] + ' ' + date.attribs['year'])
        
        # Construct full heading
        for i in range(max(len(fp_left), len(fp_right))):
            if i < len(fp_left): left = fp_left[i]; 
            else: left = '';
            if i < len(fp_right): right = fp_right[i]; 
            else: right = '';
            out.append(justify_inline(left, '', right))
        out.append('\n' + self.rfc['front']['title'].text.center(80) + '\n')
            
        # Write everything to file
        file = open(filename, 'w')
        for line in out:
            file.write(line)
            file.write('\n')
 