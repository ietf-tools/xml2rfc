# Python libs
import string

class XmlRfcWriter:
    """ Base class for all writers """
    
    def __init__(self, xmlrfc):
        # We will refer to the XmlRfc document root as 'r'
        self.r = xmlrfc.getroot()

    def prepare_top_left(self):
        """ Returns a list of lines for the top left header """
        list = [self.r.attrib['trad_header']]
        if 'number' in self.r.attrib:
            list.append('Request for Comments: ' + self.r.attrib['number'])
        else:
            # No RFC number -- assume internet draft
            list.append('Internet-Draft')
        if 'updates' in self.r.attrib:
            if self.r.attrib['updates'] != '':
                list.append(self.r.attrib['updates'])
        if 'obsoletes' in self.r.attrib:
            if self.r.attrib['obsoletes'] != '':
                list.append(self.r.attrib['obsoletes'])
        if 'category' in self.r.attrib:
            list.append('Category: ' + self.r.attrib['category'])
        return list
            
    def prepare_top_right(self):
        """ Returns a list of lines for the top right header """
        list = []
        for author in self.r.findall('front/author'):
            list.append(author.attrib['initials'] + ' ' + \
                            author.attrib['surname'])
            organization = author.find('organization')
            if organization is not None:
                if 'abbrev' in organization.attrib:
                    list.append(organization.attrib['abbrev'])
                else:  
                    list.append(organization.text)
        date = self.r.find('front/date')
        month = ''
        if 'month' in date.attrib:
            month = date.attrib['month']
        list.append(month + ' ' + date.attrib['year'])
        return list
            
    def write_section_rec(self, section, indexstring, appendix=False):
        """ Recursively writes <section> elements """
        if indexstring:
            # Prepend a neat index string to the title
            self.write_heading(indexstring + ' ' + section.attrib['title'])
            # Write to TOC as well
            if section.attrib['toc'] != 'exclude':
                anchor = None
                if 'anchor' in section.attrib:
                    anchor = section.attrib['anchor']
                self.add_to_toc(indexstring, section.attrib['title'], \
                                anchor=anchor)
        else:
            # Must be <middle> or <back> element -- no title or index.
            indexstring = ''
        
        for element in section:
            # Write elements in XML document order
            if element.tag == 't':
                self.write_t(element)
            elif element.tag == 'figure':
                self.write_figure(element)
            elif element.tag == 'texttable':
                self.write_table(element)
    
        index = 1
        for child_sec in section.findall('section'):
            if appendix == True:
                self.write_section_rec(child_sec, 'Appendix ' + \
                                       string.uppercase[index-1] + '.')
            else:
                self.write_section_rec(child_sec, indexstring + \
                                       str(index) + '.')
            index += 1

        # Set the ending index number so we know where to begin references
        if indexstring == '' and appendix == False:
            self.ref_index = index

    def write(self, filename):
        """ Public method to write an RFC document to a file.
        
            Step through the rfc tree and call writer specific methods.
        """
        # Header
        self.write_top(self.prepare_top_left(), self.prepare_top_right())

        # Title & Optional docname
        title = self.r.find('front/title').text
        if 'docName' in self.r.attrib:
            docName = self.r.attrib['docName']
        self.write_title(title, docName)
        
        # Abstract
        abstract = self.r.find('front/abstract')
        if abstract is not None:
            self.write_heading('Abstract')
            for t in abstract.findall('t'):
                self.write_t(t)

        # Status
        self.write_heading('Status of this Memo')
        self.write_paragraph(self.r.attrib['status'])

        # Copyright
        self.write_heading('Copyright Notice')
        self.write_paragraph(self.r.attrib['copyright'])
        
        # Store a marker for table of contents
        self.mark_toc()
        
        # Middle section
        self.write_section_rec(self.r.find('middle'), None)
        
        # Finished buffering, write to file
        self.write_to_file(filename)
        
    # ---------------------------------------------------------
    # The following are the write interface methods to override
    
    def write_t(self, t):
        raise NotImplementedError('Must override!')
    
    def write_figure(self, figure):
        raise NotImplementedError('Must override!')
        
    def write_table(self, table):
        raise NotImplementedError('Must override!')

    def write_top(self, left_header, right_header):
        raise NotImplementedError('Must override!')
    
    def write_title(self, title, docName=None):
        raise NotImplementedError('Must override!')
    
    def write_heading(self, text):
        raise NotImplementedError('Must override!')
    
    def write_paragraph(self, text):
        raise NotImplementedError('Must override!')
    
    def write_to_file(self, filename):
        raise NotImplementedError('Must override!')
    
    def add_to_toc(self, title, anchor):
        raise NotImplementedError('Must override!')