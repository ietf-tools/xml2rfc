# Python libs
import string

class XmlRfcWriter:
    """ Base class for all writers """
    
    def __init__(self, xmlrfc):
        # We will refer to the XmlRfc document root as 'r'
        self.r = xmlrfc.getroot()
        
        # Document counters
        self.ref_index = 1
        self.figure_count = 0
        self.table_count = 0

    def _prepare_top_left(self):
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
            
    def _prepare_top_right(self):
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
    
    def _write_figure(self, figure):
        """ Writes <figure> elements """
        align = figure.attrib['align']

        # Write preamble
        preamble = figure.find('preamble')
        if preamble is not None:
            self.write_paragraph(self.expand_refs(preamble), align=align)

        # Write figure
        self.figure_count += 1
        artwork = figure.find('artwork')
        artwork_align = align
        if 'align' in artwork.attrib:
            artwork_align = artwork.attrib['align']
        self.write_raw(figure.find('artwork').text, align=artwork_align)
        
        # Write postamble
        postamble = figure.find('postamble')
        if postamble is not None:
            self.write_paragraph(self.expand_refs(postamble), align=align)
        
        # Write label
        title = ''
        if figure.attrib['title'] != '':
            title = ': ' + figure.attrib['title']
        self.write_label('Figure ' + str(self.figure_count) + title, \
                         align='center') 
    
    def _write_table(self, table):
        """ Writes <texttable> elements """
        align = table.attrib['align']
        
        # Write preamble
        preamble = table.find('preamble')
        if preamble is not None:
            self.write_paragraph(self.expand_refs(preamble), align=align)
        
        # Write table
        self.table_count += 1
        self.draw_table(table)
        
        # Write postamble
        postamble = table.find('postamble')
        if postamble is not None:
            self.write_paragraph(self.expand_refs(postamble), align=align)
        
        # Write label
        title = ''
        if table.attrib['title'] != '':
            title = ': ' + table.attrib['title']
        self.write_label('Table ' + str(self.table_count) + title, \
                         align='center') 
    
    def _write_t_rec(self, t, indent=3, sub_indent=0, bullet='', idstring=None):
        """ Writes a <t> element """
        
        # Write the actual text
        self.write_paragraph(self.expand_refs(t), idstring=idstring)
        
        # Check for child elements
        for element in t:
            if element.tag == 'list':
                self.write_list(element)
                if element.tail:
                    self.write_paragraph(element.tail)
            elif element.tag == 'figure':
                self._write_figure(element)
            elif element.tag == 'texttable':
                self._write_table(element)
            
    def _write_section_rec(self, section, indexstring, appendix=False):
        """ Recursively writes <section> elements """
        anchor = None
        if 'anchor' in section.attrib:
            anchor = section.attrib['anchor']
        if indexstring:
            # Prepend a neat index string to the title
            self.write_heading(section.attrib['title'], \
                               bullet=indexstring + '.', \
                               idstring='rfc.section.' + indexstring, \
                               anchor=anchor)
            # Write to TOC as well
            if section.attrib['toc'] != 'exclude':
                self.add_to_toc(indexstring, section.attrib['title'], \
                                anchor=anchor)
        else:
            # Must be <middle> or <back> element -- no title or index.
            indexstring = ''
        
        paragraph_id = 1
        for element in section:
            # Write elements in XML document order
            if element.tag == 't':
                idstring = indexstring + 'p.' + str(paragraph_id)
                self._write_t_rec(element, idstring=idstring)
                paragraph_id += 1
            elif element.tag == 'figure':
                self._write_figure(element)
            elif element.tag == 'texttable':
                self._write_table(element)
    
        index = 1
        for child_sec in section.findall('section'):
            if appendix == True:
                self._write_section_rec(child_sec, 'Appendix ' + \
                                       string.uppercase[index-1] + '.')
            else:
                if indexstring:
                    self._write_section_rec(child_sec, indexstring + '.' \
                                            + str(index))
                else:
                    self._write_section_rec(child_sec, str(index))
            index += 1

        # Set the ending index number so we know where to begin references
        if indexstring == '' and appendix == False:
            self.ref_index = index

    def write(self, filename):
        """ Public method to write an RFC document to a file.
        
            Step through the rfc tree and call writer specific methods.
        """
        # Header
        self.write_top(self._prepare_top_left(), self._prepare_top_right())

        # Title & Optional docname
        title = self.r.find('front/title').text
        if 'docName' in self.r.attrib:
            docName = self.r.attrib['docName']
        self.write_title(title, docName)
        
        # Abstract
        abstract = self.r.find('front/abstract')
        if abstract is not None:
            self.write_heading('Abstract', idstring='rfc.abstract')
            for t in abstract.findall('t'):
                self._write_t_rec(t)

        # Status
        self.write_heading('Status of this Memo', idstring='rfc.status')
        self.write_paragraph(self.r.attrib['status'])

        # Copyright
        self.write_heading('Copyright Notice', idstring='rfc.copyrightnotice')
        self.write_paragraph(self.r.attrib['copyright'])
        
        # Store a marker for table of contents
        self.mark_toc()
        
        # Middle sections
        self._write_section_rec(self.r.find('middle'), None)
        
        # References sections
        # Treat references as nested only if there is more than one <references>
        ref_indexstring = str(self.ref_index) + '.'
        references = self.r.findall('back/references')
        if len(references) > 1:
            ref_title = 'References'
            self.write_heading(ref_indexstring + ' ' + ref_title)
            self.add_to_toc(ref_indexstring, ref_title)
            for index, reference_list in enumerate(references):
                ref_newindexstring = ref_indexstring + str(index + 1) + '.'
                ref_title = reference_list.attrib['title']
                self.write_heading(ref_newindexstring + ' ' + ref_title)
                self.add_to_toc(ref_newindexstring, ref_title)
                self.write_reference_list(reference_list)
        else:
            ref_title = references[0].attrib['title']
            self.write_heading(ref_indexstring + ' ' + ref_title)
            self.add_to_toc(ref_indexstring, ref_title)
            self.write_reference_list(references[0])
        
        # Appendix sections
        self._write_section_rec(self.r.find('back'), None, appendix=True)
        
        # Authors addresses section
        authors = self.r.findall('front/author')
        if len(authors) > 1:
            self.write_heading("Authors' Addresses")
            self.add_to_toc('', "Authors' Addresses")
        else:
            self.write_heading("Author's Address")
            self.add_to_toc('', "Author's Address")
        for author in authors:
            self.write_address_card(author)
            
        # Primary buffer is finished -- apply any post processing
        self.post_processing()
        
        # Finished buffering, write to file
        self.write_to_file(filename)
        
    # -----------------------------------------
    # Base writer interface methods to override
    # -----------------------------------------
    
    def mark_toc(self):
        raise NotImplementedError('Must override!')
    
    def write_raw(self, text, align='left'):
        raise NotImplementedError('Must override!')
        
    def write_label(self, text, align='center'):
        raise NotImplementedError('Must override!')
    
    def write_title(self, title, docName=None):
        raise NotImplementedError('Must override!')
        
    def write_heading(self, text, bullet=None, idstring=None, anchor=None):
        raise NotImplementedError('Must override!')

    def write_paragraph(self, text, align='left', idstring=None):
        raise NotImplementedError('Must override!')

    def write_list(self, list):
        raise NotImplementedError('Must override!')

    def write_top(self, left_header, right_header):
        raise NotImplementedError('Must override!')
    
    def write_address_card(self, author):
        raise NotImplementedError('Must override!')
    
    def write_reference_list(self, list):
        raise NotImplementedError('Must override!')
    
    def draw_table(self, table):
        raise NotImplementedError('Must override!')
    
    def expand_refs(self, element):
        raise NotImplementedError('Must override!')
    
    def add_to_toc(self, bullet, title, anchor=None):
        raise NotImplementedError('Must override!')
    
    def post_processing(self):
        raise NotImplementedError('Must override!')
    
    def write_to_file(self, filename):
        raise NotImplementedError('Must override!')