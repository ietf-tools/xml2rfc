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
        self.write_middle(self.r.find('middle'))
        
        # Finished buffering, write to file
        self.write_to_file(filename)
        
    # ---------------------------------------------------------
    # The following are the write interface methods to override
    
    def write_t(self, t):
        raise NotImplementedError('Must override!')

    def write_top(self, left_header, right_header):
        raise NotImplementedError('Must override!')
    
    def write_title(self, title, docName=None):
        raise NotImplementedError('Must override!')
    
    def write_heading(self, text):
        raise NotImplementedError('Must override!')
    
    def write_paragraph(self, text):
        raise NotImplementedError('Must override!')
    
    def write_middle(self, middle):
        raise NotImplementedError('Must override!')
    
    def write_to_file(self, filename):
        raise NotImplementedError('Must override!')