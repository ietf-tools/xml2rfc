# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

import string
import datetime
import xml2rfc.log

class BaseRfcWriter:
    """ Base class for all writers 
    
        All public methods need to be overridden for a writer implementation.
    """

    def __init__(self, xmlrfc, quiet=False, verbose=False):
        self.quiet = quiet
        self.verbose = verbose

        # We will refer to the XmlRfc document root as 'r'
        self.xmlrfc = xmlrfc
        self.r = xmlrfc.getroot()
        self.pis = xmlrfc.getpis()

        # Document counters
        self.ref_index = 1
        self.figure_count = 0
        self.table_count = 0

    def _prepare_top_left(self):
        """ Returns a lines of lines for the top left header """
        lines = [self.r.attrib['trad_header']]
        rfcnumber = self.r.attrib.get('number')
        expire_string = None
        if rfcnumber:
            lines.append('Request for Comments: ' + rfcnumber)
        else:
            # No RFC number -- assume internet draft
            lines.append('Internet-Draft')
            # Create the expiration date as published date + six months
            date = self.r.find('front/date')
            month = date.attrib.get('month', '')
            year = date.attrib.get('year', '')
            if month and year:
                try:
                    start_date = datetime.datetime.strptime(month + year, \
                                                            '%B%Y')
                    expire_date = start_date + datetime.timedelta(6 * 30 + 15)
                    expire_string = 'Expires: ' + expire_date.strftime('%B %Y')
                except ValueError:
                    pass
            elif not year:
                # Warn about no date
                xml2rfc.log.warn('No date specified for document.')

        updates = self.r.attrib.get('updates')
        if updates:
            lines.append(updates)
        obsoletes = self.r.attrib.get('obsoletes')
        if obsoletes:
            lines.append(obsoletes)
        category = self.r.attrib.get('category')
        if category:
            lines.append('Category: ' + category)
        if expire_string:
            lines.append(expire_string)
        return lines

    def _prepare_top_right(self):
        """ Returns a list of lines for the top right header """
        lines = []
        for author in self.r.findall('front/author'):
            lines.append(author.attrib['initials'] + ' ' + \
                            author.attrib['surname'])
            organization = author.find('organization')
            if organization is not None:
                abbrev = organization.attrib.get('abbrev')
                if abbrev:
                    lines.append(abbrev)
                elif organization.text:
                    lines.append(organization.text)
        date = self.r.find('front/date')
        month = date.attrib.get('month', '')
        year = date.attrib.get('year', '')
        lines.append(month + ' ' + year)
        return lines

    def _write_figure(self, figure):
        """ Writes <figure> elements """
        align = figure.attrib.get('align', 'left')
        self.figure_count += 1

        # Insert anchor(s) into document
        self.insert_anchor('rfc.figure.' + str(self.figure_count))
        anchor = figure.attrib.get('anchor')
        if anchor:
            self.insert_anchor(anchor)

        # Write preamble
        preamble = figure.find('preamble')
        if preamble is not None:
            self.write_t_rec(preamble, align=align)

        # Write figure
        artwork = figure.find('artwork')
        artwork_align = artwork.attrib.get('align', align)  # Default to figure
        blanklines = int(self.pis.get('artworklines', 0))
        self.write_raw(figure.find('artwork').text, align=artwork_align, \
                       blanklines=blanklines)

        # Write postamble
        postamble = figure.find('postamble')
        if postamble is not None:
            self.write_t_rec(postamble, align=align)

        # Write label
        title = figure.attrib.get('title', '')
        if title:
            title = ': ' + title
        self.write_label('Figure ' + str(self.figure_count) + title, \
                         type='figure')

    def _write_table(self, table):
        """ Writes <texttable> elements """
        align = table.attrib['align']
        self.table_count += 1

        # Insert anchor(s) into document
        self.insert_anchor('rfc.table.' + str(self.table_count))
        anchor = table.attrib.get('anchor')
        if anchor:
            self.insert_anchor(anchor)

        # Write preamble
        preamble = table.find('preamble')
        if preamble is not None:
            self.write_t_rec(preamble, align=align)

        # Write table
        self.draw_table(table, table_num=self.table_count)

        # Write postamble
        postamble = table.find('postamble')
        if postamble is not None:
            self.write_t_rec(postamble, align=align)

        # Write label
        title = table.attrib.get('title', '')
        if title:
            title = ': ' + title
        self.write_label('Table ' + str(self.table_count) + title, \
                         type='table')

    def _write_section_rec(self, section, indexstring, appendix=False, \
                           level=0):
        """ Recursively writes <section> elements """
        anchor = section.attrib.get('anchor', None)
        if indexstring:
            idstring = 'rfc.section.' + indexstring
            # Prepend a neat index string to the title
            self.write_heading(section.attrib['title'], \
                               bullet=indexstring + '.', idstring=idstring, \
                               anchor=anchor, level=level)
            # Write to TOC as well
            include_toc = section.attrib.get('toc', 'include')
            if include_toc != 'exclude' and \
            (appendix == False or self.pis.get('tocappendix', 'yes') == 'yes'):
                self.add_to_toc(indexstring, section.attrib['title'], \
                                link=idstring)
        else:
            # Must be <middle> or <back> element -- no title or index.
            indexstring = ''

        paragraph_id = 1
        for element in section:
            # Write elements in XML document order
            if element.tag == 't':
                idstring = 'rfc.section.' + indexstring + '.p.' + \
                            str(paragraph_id)
                self.write_t_rec(element, idstring=idstring)
                paragraph_id += 1
            elif element.tag == 'figure':
                self._write_figure(element)
            elif element.tag == 'texttable':
                self._write_table(element)

        index = 1
        for child_sec in section.findall('section'):
            if appendix == True:
                self._write_section_rec(child_sec, 'Appendix ' + \
                                        string.uppercase[index - 1] + '',
                                        level=level + 1, appendix=True)
            else:
                if indexstring:
                    self._write_section_rec(child_sec, indexstring + '.' \
                                            + str(index), level=level + 1)
                else:
                    self._write_section_rec(child_sec, str(index), \
                                            level=level + 1)
            index += 1

        # Set the ending index number so we know where to begin references
        if indexstring == '' and appendix == False:
            self.ref_index = index

    def write(self, filename):
        """ Public method to write the RFC document to a file. """

        # Do any pre processing necessary, such as inserting metadata
        self.pre_processing()

        # Block header
        self.write_top(self._prepare_top_left(), self._prepare_top_right())

        # Title & Optional docname
        title = self.r.find('front/title').text
        docName = self.r.attrib.get('docName', None)
        self.write_title(title, docName)

        # Abstract
        abstract = self.r.find('front/abstract')
        if abstract is not None:
            self.write_heading('Abstract', idstring='rfc.abstract')
            for t in abstract.findall('t'):
                self.write_t_rec(t)

        # Any notes
        for note in self.r.findall('front/note'):
            self.write_heading(note.attrib.get('title', 'Note'))
            for t in note.findall('t'):
                self.write_t_rec(t)

        # Status
        self.write_heading('Status of this Memo', idstring='rfc.status')
        self.write_paragraph(self.r.attrib.get('status', ''))

        # Copyright
        self.write_heading('Copyright Notice', idstring='rfc.copyrightnotice')
        self.write_paragraph(self.r.attrib.get('copyright', ''))

        # Insert the table of contents marker at this position
        toc_enabled = self.pis.get('toc', 'no')
        if toc_enabled == 'yes':
            self.insert_toc()

        # Middle sections
        self._write_section_rec(self.r.find('middle'), None)

        # References sections
        # Treat references as nested only if there is more than one
        ref_indexstring = str(self.ref_index)
        ref_idstring = 'rfc.section.' + ref_indexstring
        references = self.r.findall('back/references')
        if len(references) > 1:
            ref_title = 'References'
            self.write_heading(ref_title, bullet=ref_indexstring + '.', \
                               idstring=ref_idstring)
            self.add_to_toc(ref_indexstring, ref_title, link=ref_idstring)
            for index, reference_list in enumerate(references):
                ref_newindexstring = ref_indexstring + '.' + str(index + 1)
                ref_newidstring = ref_idstring + '.' + str(index + 1)
                ref_title = reference_list.attrib['title']
                self.write_heading(ref_title, bullet=ref_newindexstring + '.',\
                                   idstring=ref_newidstring, level=2)
                self.add_to_toc(ref_newindexstring, ref_title, \
                                link=ref_newidstring)
                self.write_reference_list(reference_list)
        elif len(references) == 1:
            ref_title = references[0].attrib['title']
            self.write_heading(ref_title, bullet=ref_indexstring + '.', \
                               idstring=ref_idstring)
            self.add_to_toc(ref_indexstring, ref_title, \
                            link=ref_idstring)
            self.write_reference_list(references[0])
            
        # Additional index -- The writer is responsible for tracking irefs, 
        # so we have nothing to pass here
        self.write_iref_index()

        # Appendix sections
        self._write_section_rec(self.r.find('back'), None, appendix=True)

        # Authors addresses section
        authors = self.r.findall('front/author')
        idstring = 'rfc.authors'
        if len(authors) > 1:
            title = "Authors' Addresses"
        else:
            title = "Author's Address"
        self.write_heading(title, idstring=idstring)
        self.add_to_toc('', title)
        for author in authors:
            self.write_address_card(author)

        # Primary buffer is finished -- apply any post processing
        self.post_processing()

        # Finished buffering, write to file
        self.write_to_file(filename)

        if not self.quiet:
            xml2rfc.log.write('Created file', filename)

    # -----------------------------------------
    # Base writer interface methods to override
    # -----------------------------------------

    def insert_toc(self):
        """ Marks the current buffer position to insert ToC at """
        raise NotImplementedError('insert_toc() needs to be overridden')

    def write_raw(self, text, indent=3, align='left', blanklines=0):
        """ Writes a block of text that preserves all whitespace """
        raise NotImplementedError('write_raw() needs to be overridden')

    def write_label(self, text, type='figure'):
        """ Writes a table or figure label """
        raise NotImplementedError('write_label() needs to be overridden')

    def write_title(self, title, docName=None):
        """ Writes the document title """
        raise NotImplementedError('write_title() needs to be overridden')

    def write_heading(self, text, bullet='', idstring=None, anchor=None, \
                      level=1):
        """ Writes a section heading """
        raise NotImplementedError('write_heading() needs to be overridden')

    def write_paragraph(self, text, align='left', idstring=None):
        """ Writes a paragraph of text """
        raise NotImplementedError('write_paragraph() needs to be'\
                                  ' overridden')

    def write_t_rec(self, t, align='left', idstring=None):
        """ Recursively writes <t> elements """
        raise NotImplementedError('write_t_rec() needs to be overridden')

    def write_top(self, left_header, right_header):
        """ Writes the main document header

            Takes two list arguments, one for each margin, and combines them
            so that they exist on the same lines of text
        """
        raise NotImplementedError('write_top() needs to be overridden')

    def write_address_card(self, author):
        """ Writes the address information for an <author> element """
        raise NotImplementedError('write_address_card() needs to be ' \
                                  'overridden')

    def write_reference_list(self, list):
        """ Writes a <references> element """
        raise NotImplementedError('write_reference_list() needs to be ' \
                                  'overridden')
        
    def write_iref_index(self):
        """ Writes an additional index if there were iref elements """
        raise NotImplementedError('write_iref_index() needs to be ' \
                                  'overridden')

    def insert_anchor(self, text):
        """ Inserts a document anchor for internal links """
        raise NotImplementedError('insert_anchor() needs to be overridden')

    def draw_table(self, table, table_num=None):
        """ Draws a formatted table from a <texttable> element

            For HTML nothing is really 'drawn' since we can use <table>
        """
        raise NotImplementedError('draw_table() needs to be overridden')

    def add_to_toc(self, bullet, title, link=None):
        """ Adds a section to the table of contents """
        raise NotImplementedError('add_to_toc() needs to be overridden')

    def pre_processing(self):
        """ First method that is called before traversing the XML RFC tree """
        raise NotImplementedError('pre_processing() needs to be overridden')

    def post_processing(self):
        """ Last method that is called after traversing the XML RFC tree """
        raise NotImplementedError('post_processing() needs to be overridden')

    def write_to_file(self, filename):
        """ Writes the finished buffer to a file """
        raise NotImplementedError('write_to_file() needs to be overridden')
