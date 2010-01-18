<!--
    XSLT transformation from RFC2629 XML format to HTML

    Copyright (c) 2001-2003 Julian F. Reschke (julian.reschke@greenbytes.de)

    placed into the public domain

    change history:

    2001-03-28  julian.reschke@greenbytes.de

    Code rearranged, generate numbered section anchors for paragraphs (t)
    as well. Fixes in index handling.

    2001-04-12  julian.reschke@greenbytes.de

    Moved HTML output into XHTML namespace.

    2001-10-02  julian.reschke@greenbytes.de

    Fixed default location for RFCs and numbering of section references.
    Support ?rfc editing processing instruction.

    2001-10-07  julian.reschke@greenbytes.de

    Made telephone number links active.

    2001-10-08  julian.reschke@greenbytes.de

    Support for vspace element.

    2001-10-09  julian.reschke@greenbytes.de

    Experimental support for rfc-issue PI.

    2001-11-11  julian.reschke@greenbytes.de

    Support rfc private PI. Removed bogus code reporting the WG in the header.

    2001-12-17  julian.reschke@greenbytes.de

    Support title attribute on references element

    2002-01-05  julian.reschke@greenbytes.de

    Support for list/@style="@format"

    2002-01-09  julian.reschke@greenbytes.de

    Display "closed" RFC issues as deleted

    2002-01-14  julian.reschke@greenbytes.de

    Experimentally and optionally parse XML encountered in artwork elements
    (requires MSXSL).

    2002-01-27  julian.reschke@greenbytes.de

    Some cleanup. Moved RFC issues from PIs into namespaced elements.

    2002-01-29  julian.reschke@greenbytes.de

    Added support for sortrefs PI. Added support for figure names.

    2002-02-07  julian.reschke@greenbytes.de

    Highlight parts of artwork which are too wide (72 characters).

    2002-02-12  julian.reschke@greenbytes.de

    Code rearrangement for static texts. Fixes for section numbering.
    TOC generation rewritten.

    2002-02-15  julian.reschke@greenbytes.de

    Support for irefs in sections; support iref @primary=true

    2002-03-03  julian.reschke@greenbytes.de

    Moved anchor prefix into a constant. Added sanity checks on user anchor
    names.

    2002-03-23  julian.reschke@greenbytes.de

    Bugfix in detection of matching org names when creating the header. Fixed
    sorting in subitems.

    2002-04-02  julian.reschke@greenbytes.de

    Fix TOC link HTML generation when no TOC is generated (created broken
    HTML table code).

    2002-04-03  julian.reschke@greenbytes.de

    Made rendering of references more tolerant re: missing parts.

    2002-04-08  julian.reschke@greenbytes.de

    Fixed reference numbering when references are split into separate sections.

    2002-04-16  julian.reschke@greenbytes.de

    Fix default namespace (shouldn't be set for HTML output method).

    2002-04-19  julian.reschke@greenbytes.de

    Lowercase internal CSS selectors for Mozilla compliance. Do not put TOC
    into ul element.

    2002-04-21  julian.reschke@greenbytes.de

    Make numbered list inside numbered lists use alphanumeric numbering.

    2002-05-05  julian.reschke@greenbytes.de

    Updated issue/editing support.

    2002-05-15  julian.reschke@greenbytes.de

    Bugfix for section numbering after introduction of ed:replace

    2002-06-21  julian.reschke@greenbytes.de

    When producing private documents, do not include document status, copyright etc.

    2002-07-08  julian.reschke@greenbytes.de

    Fix xrefs to Appendices.

    2002-07-19  fielding

    Make artwork lightyellow for easier reading.

    2002-10-09  fielding

    Translate references title to anchor name to avoid non-uri characters.
    
    2002-10-13  julian.reschke@greenbytes.de
    
    Support for tocdepth PI.

    2002-11-03  julian.reschke@greenbytes.de
    
    Added temporariry workaround for Mozilla/Transformiix result tree fragment problem.
    (search for 'http://bugzilla.mozilla.org/show_bug.cgi?id=143668')
    
    2002-12-25  julian.reschke@greenbytes.de
    
    xref code: attempt to uppercase "section" and "appendix" when at the start
    of a sentence.
    
    2003-02-02  julian.reschke@greenbytes.de
    
    fixed code for vspace blankLines="0", enhanced display for list with "format" style,
    got rid of HTML blockquote elements, added support for "hangIndent"
    
    2003-04-10  julian.reschke@greenbytes.de
    
    experimental support for appendix and spanx elements
    
    2003-04-19  julian.reschke@greenbytes.de
    
    fixed counting of list numbers in "format %" styles (one counter
    per unique format string). Added more spanx styles.

    2003-05-02  julian.reschke@greenbytes.de
    
    experimental texttable support
    
    2003-05-02  fielding 
    
    Make mailto links optional (default = none) (jre: default and PI name changed)

    2003-05-04  julian.rechke@greenbytes.de
    
    experimental support for HTML link elements; fix default for table header
    alignment default

    2003-05-06  julian.rechke@greenbytes.de
    
    support for "background" PI.
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0"
                xmlns:xalan="http://xml.apache.org/xalan"
                xmlns:msxsl="urn:schemas-microsoft-com:xslt"
                xmlns:saxon="http://icl.com/saxon"
                xmlns:myns="mailto:julian.reschke@greenbytes.de?subject=rcf2629.xslt"
                exclude-result-prefixes="msxsl xalan saxon myns ed"
                xmlns:ed="http://greenbytes.de/2002/rfcedit"
                >

<xsl:output method="html" encoding="iso-8859-1" />


<!-- process some of the processing instructions supported by Marshall T. Rose's
     xml2rfc sofware, see <http://xml.resource.org/> -->

<!-- include a table of contents if a processing instruction <?rfc?>
     exists with contents toc="yes". Can be overriden by an XSLT parameter -->

<xsl:param name="includeToc"
  select="substring-after(
      translate(/processing-instruction('rfc')[contains(.,'toc=')], '&quot; ', ''),
        'toc=')"
/>

<!-- optional tocdepth-->

<xsl:param name="unparsedTocDepth"
  select="substring-after(
      translate(/processing-instruction('rfc')[contains(.,'tocdepth=')], '&quot; ', ''),
        'tocdepth=')"
/>

<xsl:variable name="tocDepth">
  <xsl:choose>
    <xsl:when test="$unparsedTocDepth='1'">1</xsl:when>
    <xsl:when test="$unparsedTocDepth='2'">2</xsl:when>
    <xsl:when test="$unparsedTocDepth='3'">3</xsl:when>
    <xsl:when test="$unparsedTocDepth='4'">4</xsl:when>
    <xsl:when test="$unparsedTocDepth='5'">5</xsl:when>
    <xsl:otherwise>99</xsl:otherwise>
  </xsl:choose>
</xsl:variable>


<!-- use symbolic reference names instead of numeric ones if a processing instruction <?rfc?>
     exists with contents symrefs="yes". Can be overriden by an XSLT parameter -->

<xsl:param name="useSymrefs"
  select="substring-after(
      translate(/processing-instruction('rfc')[contains(.,'symrefs=')], '&quot; ', ''),
        'symrefs=')"
/>

<!-- sort references if a processing instruction <?rfc?>
     exists with contents sortrefs="yes". Can be overriden by an XSLT parameter -->

<xsl:param name="sortRefs"
  select="substring-after(
      translate(/processing-instruction('rfc')[contains(.,'sortrefs=')], '&quot; ', ''),
        'sortrefs=')"
/>

<!-- insert editing marks if a processing instruction <?rfc?>
     exists with contents editing="yes". Can be overriden by an XSLT parameter -->

<xsl:param name="insertEditingMarks"
  select="substring-after(
      translate(/processing-instruction('rfc')[contains(.,'editing=')], '&quot; ', ''),
        'editing=')"
/>

<!-- make it a private paper -->

<xsl:param name="private"
  select="substring-after(
      translate(/processing-instruction('rfc')[contains(.,'private=')], '&quot;', ''),
        'private=')"
/>

<!-- background image? -->

<xsl:param name="background"
  select="substring-after(
      translate(/processing-instruction('rfc')[contains(.,'background=')], '&quot;', ''),
        'background=')"
/>

<!-- extension for XML parsing in artwork -->

<xsl:param name="parse-xml-in-artwork"
  select="substring-after(
      translate(/processing-instruction('rfc-ext')[contains(.,'parse-xml-in-artwork=')], '&quot; ', ''),
        'parse-xml-in-artwork=')"
/>

<!-- choose whether or not to do mailto links --> 
  
 <xsl:param name="link-mailto" 
   select="substring-after( 
       translate(/processing-instruction('rfc')[contains(.,'linkmailto=')], '&quot;', ''), 
         'linkmailto=')" 
 /> 


<!-- URL prefix for RFCs. -->

<xsl:param name="rfcUrlPrefix" select="'http://www.ietf.org/rfc/rfc'" />


<!-- build help keys for indices -->
<xsl:key name="index-first-letter"
  match="iref"
    use="translate(substring(@item,1,1),'abcdefghijklmnoprrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ')" />

<xsl:key name="index-item"
  match="iref"
    use="@item" />

<xsl:key name="index-item-subitem"
  match="iref"
    use="concat(@item,'..',@subitem)" />

<!-- character translation tables -->
<xsl:variable name="lcase" select="'abcdefghijklmnopqrstuvwxyz'" />
<xsl:variable name="ucase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'" />       

<xsl:variable name="plain" select="' #/ABCDEFGHIJKLMNOPQRSTUVWXYZ'" />
<xsl:variable name="touri" select="'___abcdefghijklmnopqrstuvwxyz'" />

<!-- prefix for automatically generated anchors -->
<xsl:variable name="anchor-prefix" select="'rfc'" />

<!-- Templates for the various elements of rfc2629.dtd -->
              
<xsl:template match="abstract">
    <h1>Abstract</h1>
  <xsl:apply-templates />
</xsl:template>

<msxsl:script language="JScript" implements-prefix="myns">
  function parseXml(str) {
    var doc = new ActiveXObject ("MSXML2.DOMDocument");
    doc.async = false;
    if (doc.loadXML (str)) return "";
    return doc.parseError.reason + "\n" + doc.parseError.srcText + " (" + doc.parseError.line + "/" + doc.parseError.linepos + ")";
  }
</msxsl:script>

<xsl:template match="artwork">
  <xsl:if test="not(ancestor::ed:del) and $parse-xml-in-artwork='yes' and function-available('myns:parseXml')">
    <xsl:if test="contains(.,'&lt;?xml')">
      <xsl:variable name="body" select="substring-after(substring-after(.,'&lt;?xml'),'?>')" /> 
      <xsl:if test="$body!='' and myns:parseXml($body)!=''">
        <table style="background-color: red; border-width: thin; border-style: solid; border-color: black;">
        <tr><td>
        XML PARSE ERROR:
        <pre><xsl:value-of select="myns:parseXml($body)" /></pre>
        </td></tr></table>
      </xsl:if>
    </xsl:if>
    <xsl:if test="@ed:parse-xml-after">
      <xsl:if test="myns:parseXml(string(.))!=''">
        <table style="background-color: red; border-width: thin; border-style: solid; border-color: black;">
        <tr><td>
        XML PARSE ERROR:
        <pre><xsl:value-of select="myns:parseXml(string(.))" /></pre>
        </td></tr></table>
      </xsl:if>
    </xsl:if>
  </xsl:if>
  <pre><!--<xsl:value-of select="." />--><xsl:call-template name="showArtwork">
    <xsl:with-param name="mode" select="'html'" />
    <xsl:with-param name="text" select="." />
    <xsl:with-param name="initial" select="'yes'" />
  </xsl:call-template></pre>
</xsl:template>

<xsl:template match="author">
  <tr>
    <td>&#0160;</td>
    <td><xsl:value-of select="@fullname" /></td>
  </tr>
  <tr>
    <td>&#0160;</td>
    <td><xsl:value-of select="organization" /></td>
  </tr>
  <xsl:if test="address/postal/street!=''">
    <tr>
      <td>&#0160;</td>
      <td><xsl:for-each select="address/postal/street"><xsl:value-of select="." /><br /></xsl:for-each></td>
    </tr>
  </xsl:if>
  <xsl:if test="address/postal/city|address/postal/region|address/postal/code">
    <tr>
      <td>&#0160;</td>
      <td>
        <xsl:if test="address/postal/city"><xsl:value-of select="address/postal/city" />, </xsl:if>
        <xsl:if test="address/postal/region"><xsl:value-of select="address/postal/region" />&#160;</xsl:if>
        <xsl:if test="address/postal/code"><xsl:value-of select="address/postal/code" /></xsl:if>
      </td>
    </tr>
  </xsl:if>
  <xsl:if test="address/postal/country">
    <tr>
      <td>&#0160;</td>
      <td><xsl:value-of select="address/postal/country" /></td>
    </tr>
  </xsl:if>
  <xsl:if test="address/phone">
    <tr>
      <td align="right"><b>Phone:&#0160;</b></td>
      <td><a href="tel:{address/phone}"><xsl:value-of select="address/phone" /></a></td>
    </tr>
  </xsl:if>
  <xsl:if test="address/facsimile">
    <tr>
      <td align="right"><b>Fax:&#0160;</b></td>
      <td><a href="fax:{address/facsimile}"><xsl:value-of select="address/facsimile" /></a></td>
    </tr>
  </xsl:if>
  <xsl:if test="address/email">
    <tr>
      <td align="right"><b>EMail:&#0160;</b></td>
      <td>
        <a>
          <xsl:if test="$link-mailto!='no'">
            <xsl:attribute name="href">mailto:<xsl:value-of select="address/email" /></xsl:attribute>
          </xsl:if>
          <xsl:value-of select="address/email" />
        </a>
      </td>
    </tr>
  </xsl:if>
  <xsl:if test="address/uri">
    <tr>
      <td align="right"><b>URI:&#0160;</b></td>
      <td><a href="{address/uri}"><xsl:value-of select="address/uri" /></a></td>
    </tr>
  </xsl:if>
  <tr>
    <td>&#0160;</td>
    <td />
  </tr>
</xsl:template>

<xsl:template match="back">

  <!-- add references section first, no matter where it appears in the
    source document -->
  <xsl:apply-templates select="references" />
   
  <!-- next, add information about the document's authors -->
  <xsl:call-template name="insertAuthors" />
    
  <!-- add all other top-level sections under <back> -->
  <xsl:apply-templates select="*[not(self::references)]" />

  <xsl:if test="not($private)">
    <!-- copyright statements -->
    <xsl:variable name="copyright"><xsl:call-template name="insertCopyright" /></xsl:variable>
  
    <!-- emit it -->
    <xsl:choose>
      <xsl:when test="function-available('msxsl:node-set')">
        <xsl:apply-templates select="msxsl:node-set($copyright)" />
      </xsl:when>
      <xsl:when test="function-available('saxon:node-set')">
        <xsl:apply-templates select="saxon:node-set($copyright)" />
      </xsl:when>
      <xsl:when test="function-available('xalan:nodeset')">
        <xsl:apply-templates select="xalan:nodeset($copyright)" />
      </xsl:when>
      <xsl:otherwise> <!--proceed with fingers crossed-->
        <xsl:apply-templates select="$copyright" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:if>
  
  <!-- insert the index if index entries exist -->
  <xsl:if test="//iref">
    <xsl:call-template name="insertIndex" />
  </xsl:if>

</xsl:template>

<xsl:template match="eref[node()]">
  <a href="{@target}"><xsl:apply-templates /></a>
</xsl:template>
               
<xsl:template match="figure">
  <xsl:if test="@anchor!=''">
    <a name="{@anchor}" />
  </xsl:if>
  <xsl:choose>
    <xsl:when test="@title!='' or @anchor!=''">
      <xsl:variable name="n"><xsl:number level="any" count="figure[@title!='' or @anchor!='']" /></xsl:variable>
      <a name="{$anchor-prefix}.figure.{$n}" />
    </xsl:when>
    <xsl:otherwise>
      <xsl:variable name="n"><xsl:number level="any" count="figure[not(@title!='' or @anchor!='')]" /></xsl:variable>
      <a name="{$anchor-prefix}.figure.u.{$n}" />
    </xsl:otherwise>
  </xsl:choose>
  <xsl:apply-templates />
  <xsl:if test="@title!='' or @anchor!=''">
    <xsl:variable name="n"><xsl:number level="any" count="figure[@title!='' or @anchor!='']" /></xsl:variable>
    <p class="figure">Figure <xsl:value-of select="$n"/><xsl:if test="@title!=''">: <xsl:value-of select="@title" /></xsl:if></p>
  </xsl:if>
</xsl:template>

<xsl:template match="front">

  <xsl:call-template name="insertTocLink">
    <xsl:with-param name="includeTitle" select="true()" />
  </xsl:call-template>
            
  <!-- collect information for left column -->
    
  <xsl:variable name="leftColumn">
    <xsl:call-template name="collectLeftHeaderColumn" />    
  </xsl:variable>

  <!-- collect information for right column -->
    
  <xsl:variable name="rightColumn">
    <xsl:call-template name="collectRightHeaderColumn" />    
  </xsl:variable>
    
    <!-- insert the collected information -->
    
  <table width="66%" border="0" cellpadding="1" cellspacing="1">
    <xsl:choose>
      <xsl:when test="function-available('msxsl:node-set')">
        <xsl:call-template name="emitheader">
          <xsl:with-param name="lc" select="msxsl:node-set($leftColumn)" />    
          <xsl:with-param name="rc" select="msxsl:node-set($rightColumn)" />    
        </xsl:call-template>
      </xsl:when>    
      <xsl:when test="function-available('saxon:node-set')">
        <xsl:call-template name="emitheader">
          <xsl:with-param name="lc" select="saxon:node-set($leftColumn)" />    
          <xsl:with-param name="rc" select="saxon:node-set($rightColumn)" />    
        </xsl:call-template>
      </xsl:when>    
      <xsl:when test="function-available('xalan:nodeset')">
        <xsl:call-template name="emitheader">
          <xsl:with-param name="lc" select="xalan:nodeset($leftColumn)" />    
          <xsl:with-param name="rc" select="xalan:nodeset($rightColumn)" />    
        </xsl:call-template>
      </xsl:when>    
      <xsl:otherwise>    
        <xsl:call-template name="emitheader">
          <xsl:with-param name="lc" select="$leftColumn" />    
          <xsl:with-param name="rc" select="$rightColumn" />    
        </xsl:call-template>
      </xsl:otherwise>    
    </xsl:choose>
  </table>
  <br />

  <!-- main title -->
  <div align="right"><span class="title"><xsl:value-of select="title"/></span></div>
  <xsl:if test="/rfc/@docName">
    <div align="right"><span class="filename"><xsl:value-of select="/rfc/@docName"/></span></div>
  </xsl:if>  
  
  <xsl:if test="not($private)">
    <!-- Get status info formatted as per RFC2629-->
    <xsl:variable name="preamble"><xsl:call-template name="insertPreamble" /></xsl:variable>
    
    <!-- emit it -->
    <xsl:choose>
      <xsl:when test="function-available('msxsl:node-set')">
        <xsl:apply-templates select="msxsl:node-set($preamble)" />
      </xsl:when>
      <xsl:when test="function-available('saxon:node-set')">
        <xsl:apply-templates select="saxon:node-set($preamble)" />
      </xsl:when>
      <xsl:when test="function-available('xalan:nodeset')">
        <xsl:apply-templates select="xalan:nodeset($preamble)" />
      </xsl:when>
      <xsl:when test="system-property('xsl:vendor')='Transformiix' and system-property('xsl:vendor-url')='http://www.mozilla.org/projects/xslt/'">
        <!--special case for Transformiix as of Mozilla release 1.2b -->
        <!--see http://bugzilla.mozilla.org/show_bug.cgi?id=143668 -->
        <xsl:apply-templates select="$preamble/node()" />
      </xsl:when>
      <xsl:otherwise>
        <!--proceed with fingers crossed-->
        <xsl:apply-templates select="$preamble/node()" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:if>
            
  <xsl:apply-templates select="abstract" />
  <xsl:apply-templates select="note" />
    
  <xsl:if test="$includeToc='yes'">
    <xsl:apply-templates select="/" mode="toc" />
    <xsl:call-template name="insertTocAppendix" />
  </xsl:if>

</xsl:template>


<xsl:template match="iref">
  <a><xsl:attribute name="name"><xsl:value-of select="$anchor-prefix"/>.iref.<xsl:number level="any"/></xsl:attribute></a>
</xsl:template>

<!-- list templates depend on the list style -->

<xsl:template match="list[@style='empty' or not(@style)]">
  <dl>
    <xsl:apply-templates />
  </dl>
</xsl:template>

<xsl:template match="list[starts-with(@style,'format ')]">
  <table>
    <xsl:apply-templates />
  </table>
</xsl:template>

<xsl:template match="list[@style='hanging']">
  <dl>
    <xsl:apply-templates />
  </dl>
</xsl:template>

<xsl:template match="list[@style='numbers']">
  <blockquote>
    <ol>
      <xsl:apply-templates />
    </ol>
  </blockquote>
</xsl:template>

<!-- numbered list inside numbered list -->
<xsl:template match="list[@style='numbers']/t/list[@style='numbers']" priority="9">
  <ol style="list-style-type: lower-alpha">
    <xsl:apply-templates />
  </ol>
</xsl:template>

<xsl:template match="list[@style='symbols']">
  <ul>
    <xsl:apply-templates />
  </ul>
</xsl:template>

<!-- same for t(ext) elements -->

<xsl:template match="list[@style='empty' or not(@style)]/t">
  <dd style="margin-top: .5em">
    <xsl:apply-templates />
  </dd>
</xsl:template>

<xsl:template match="list[@style='numbers' or @style='symbols']/t">
  <li>
    <xsl:apply-templates />
  </li>
</xsl:template>

<xsl:template match="list[@style='hanging']/t">
  <dt style="margin-top: .5em">
    <xsl:value-of select="@hangText" />
  </dt>
  <dd>
    <!-- if hangIndent present, use 0.7 of the specified value (1em is the width of the "m" character -->
    <xsl:if test="../@hangIndent">
      <xsl:attribute name="style">margin-left: <xsl:value-of select="../@hangIndent * 0.7"/>em</xsl:attribute>
    </xsl:if>
    <xsl:apply-templates />
  </dd>
</xsl:template>

<xsl:template match="list[starts-with(@style,'format ') and (contains(@style,'%c') or contains(@style,'%d'))]/t">
  <xsl:variable name="list" select=".." />
  <xsl:variable name="format" select="substring-after(../@style,'format ')" />
  <xsl:variable name="pos">
    <xsl:choose>
      <xsl:when test="$list/@counter">
        <xsl:number level="any" count="list[@counter=$list/@counter or (not(@counter) and @style=$list/@counter)]/t" />
      </xsl:when>
      <xsl:otherwise>
        <xsl:number level="any" count="list[@counter=$list/@style or (not(@counter) and @style=$list/@style)]/t" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <tr>
    <td class="top">
      <xsl:choose>
        <xsl:when test="contains($format,'%c')">
          <xsl:value-of select="substring-before($format,'%c')"/><xsl:number value="$pos" format="A" /><xsl:value-of select="substring-after($format,'%c')"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="substring-before($format,'%d')"/><xsl:number value="$pos" format="1" /><xsl:value-of select="substring-after($format,'%d')"/>
        </xsl:otherwise>
      </xsl:choose>
      &#160;
    </td>
    <td class="top">
      <xsl:apply-templates />
    </td>
  </tr>
</xsl:template>

<xsl:template match="middle">
  <xsl:apply-templates />
</xsl:template>

<xsl:template match="note">
  <h1><xsl:value-of select="@title" /></h1>
    <xsl:apply-templates />
</xsl:template>

<xsl:template match="postamble">
  <p>
    <xsl:call-template name="editingMark" />
    <xsl:apply-templates />
  </p>
</xsl:template>

<xsl:template match="preamble">
  <p>
    <xsl:call-template name="editingMark" />
    <xsl:apply-templates />
  </p>
</xsl:template>


<xsl:template match="reference">

  <xsl:variable name="target">
    <xsl:choose>
      <xsl:when test="@target"><xsl:value-of select="@target" /></xsl:when>
      <xsl:when test="seriesInfo/@name='RFC'"><xsl:value-of select="concat($rfcUrlPrefix,seriesInfo[@name='RFC']/@value,'.txt')" /></xsl:when>
      <xsl:when test="seriesInfo[starts-with(.,'RFC')]">
        <xsl:variable name="rfcRef" select="seriesInfo[starts-with(.,'RFC')]" />
        <xsl:value-of select="concat($rfcUrlPrefix,substring-after (normalize-space($rfcRef), ' '),'.txt')" />
      </xsl:when>
      <xsl:otherwise />
    </xsl:choose>
  </xsl:variable>
  
  <tr>
    <td valign="top" nowrap="nowrap">
      <b>
        <a name="{@anchor}">
          <xsl:call-template name="referencename">
            <xsl:with-param name="node" select="." />
          </xsl:call-template>
        </a>
      </b>
    </td>
    
    <td valign="top">
      <xsl:for-each select="front/author">
        <xsl:choose>
          <xsl:when test="@surname and @surname!=''">
            <xsl:choose>
               <xsl:when test="address/email">
                <a>
                  <xsl:if test="$link-mailto!='no'">
                    <xsl:attribute name="href">mailto:<xsl:value-of select="address/email" /></xsl:attribute>
                  </xsl:if>
                  <xsl:if test="organization/text()">
                    <xsl:attribute name="title"><xsl:value-of select="organization/text()"/></xsl:attribute>
                  </xsl:if>
                  <xsl:value-of select="concat(@surname,', ',@initials)" />
                </a>
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="concat(@surname,', ',@initials)" />
              </xsl:otherwise>
            </xsl:choose>
            
            <xsl:if test="position()!=last() - 1">,&#0160;</xsl:if>
            <xsl:if test="position()=last() - 1"> and </xsl:if>
          </xsl:when>
          <xsl:when test="organization/text()">
            <xsl:choose>
              <xsl:when test="address/uri">
                <a href="{address/uri}"><xsl:value-of select="organization" /></a>
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="organization" />
              </xsl:otherwise>
            </xsl:choose>
            <xsl:if test="position()!=last() - 1">,&#0160;</xsl:if>
            <xsl:if test="position()=last() - 1"> and </xsl:if>
          </xsl:when>
          <xsl:otherwise />
        </xsl:choose>
      </xsl:for-each>
         
      <xsl:choose>
        <xsl:when test="string-length($target) &gt; 0">
          <xsl:text>"</xsl:text><a href="{$target}"><xsl:value-of select="front/title" /></a><xsl:text>"</xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>"</xsl:text><xsl:value-of select="front/title" /><xsl:text>"</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
            
      <xsl:for-each select="seriesInfo">
        <xsl:text>, </xsl:text>
        <xsl:choose>
          <xsl:when test="not(@name) and not(@value) and ./text()"><xsl:value-of select="." /></xsl:when>
          <xsl:otherwise><xsl:value-of select="@name" /><xsl:if test="@value!=''">&#0160;<xsl:value-of select="@value" /></xsl:if></xsl:otherwise>
        </xsl:choose>
      </xsl:for-each>
      
      <xsl:if test="front/date/@year != '' and front/date/@year != '???'">
        <xsl:text>, </xsl:text>
        <xsl:if test="front/date/@month and front/date/@month!='???'"><xsl:value-of select="front/date/@month" />&#0160;</xsl:if>
        <xsl:value-of select="front/date/@year" />
      </xsl:if>
      
      <xsl:text>.</xsl:text>
    </td>
  </tr>
</xsl:template>


<xsl:template match="references[not(@title)]">

  <xsl:call-template name="insertTocLink">
    <xsl:with-param name="rule" select="true()" />
  </xsl:call-template>

  <h1><a name="{$anchor-prefix}.references">References</a></h1>

  <table border="0">
    <xsl:choose>
      <xsl:when test="$sortRefs='yes'">
        <xsl:apply-templates>
          <xsl:sort select="@anchor" />
        </xsl:apply-templates>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates />
      </xsl:otherwise>
    </xsl:choose>
  </table>
  
</xsl:template>

<xsl:template match="references[@title]">

  <xsl:call-template name="insertTocLink">
    <xsl:with-param name="rule" select="true()" />
  </xsl:call-template>

  <xsl:variable name="safeanchor" select="translate(@title,$plain,$touri)" />
  <h1><a name="{$anchor-prefix}.{$safeanchor}">
    <xsl:value-of select="@title" />
  </a></h1>

  <table border="0">
    <xsl:choose>
      <xsl:when test="$sortRefs='yes'">
        <xsl:apply-templates>
          <xsl:sort select="@anchor" />
        </xsl:apply-templates>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates />
      </xsl:otherwise>
    </xsl:choose>
  </table>

</xsl:template>

<xsl:template match="rfc">
  <html>
    <head>
      <title><xsl:value-of select="front/title" /></title>
       <style type="text/css">
        <xsl:call-template name="insertCss" />
      </style>
      <xsl:if test="$includeToc='yes'">
        <link rel="Contents" href="#rfc.toc" />
      </xsl:if>
      <link rel="Author" href="#rfc.authors" />
      <link rel="Copyright" href="#rfc.copyright" />
      <xsl:if test="//iref">
        <link rel="Index" href="#rfc.index" />
      </xsl:if>
      <xsl:apply-templates select="/" mode="links" />
      <xsl:for-each select="/rfc/ed:link">
        <link><xsl:copy-of select="@*" /></link>
      </xsl:for-each>
      <xsl:if test="/rfc/@number">
        <link rel="Alternate" title="Authorative ASCII version" href="http://www.ietf.org/rfc/rfc{/rfc/@number}" />
      </xsl:if>
    </head>
    <body>
      <!-- insert diagnostics -->
      <xsl:call-template name="insertDiagnostics"/>
    
      <xsl:apply-templates select="front" />
      <xsl:apply-templates select="middle" />
      <xsl:apply-templates select="back" />
    </body>
  </html>
</xsl:template>               


<xsl:template match="t">
  <xsl:variable name="paraNumber">
    <xsl:call-template name="sectionnumberPara" />
  </xsl:variable>
    
  <p>
    <xsl:if test="string-length($paraNumber) &gt; 0">
      <!--<xsl:attribute name="title"><xsl:value-of select="concat($anchor-prefix,'.section.',$paraNumber)" /></xsl:attribute> -->
      <a name="{$anchor-prefix}.section.{$paraNumber}" />
    </xsl:if>
    <xsl:call-template name="editingMark" />
    <xsl:apply-templates />
  </p>
</xsl:template>
               
               
<xsl:template match="section|appendix">

  <xsl:variable name="sectionNumber">
    <xsl:choose>
      <xsl:when test="@myns:unnumbered"></xsl:when>
      <xsl:otherwise><xsl:call-template name="sectionnumber" /></xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
    
  <xsl:if test="not(ancestor::section) and not(@myns:notoclink)">
    <xsl:call-template name="insertTocLink">
      <xsl:with-param name="rule" select="true()" />
    </xsl:call-template>
  </xsl:if>
  
  <xsl:variable name="elemtype">
    <xsl:choose>
      <xsl:when test="count(ancestor::section) = 0">h1</xsl:when>
      <xsl:when test="count(ancestor::section) = 1">h2</xsl:when>
      <xsl:otherwise>h3</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  
  <xsl:element name="{$elemtype}">
    <!-- generate anchors for irefs that are immediate childs of this section -->
    <xsl:apply-templates select="iref"/>
    <xsl:if test="$sectionNumber!=''">
      <a name="{$anchor-prefix}.section.{$sectionNumber}"><xsl:value-of select="$sectionNumber" /></a>&#0160;
    </xsl:if>
    <xsl:choose>
      <xsl:when test="@anchor">
        <a name="{@anchor}"><xsl:value-of select="@title" /></a>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="@title" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:element>
  <xsl:apply-templates select="*[not(self::iref)]" />
</xsl:template>

<xsl:template match="spanx[@style='emph' or not(@style)]">
  <em><xsl:apply-templates /></em>
</xsl:template>

<xsl:template match="spanx[@style='verb']">
  <tt><xsl:apply-templates /></tt>
</xsl:template>

<xsl:template match="spanx[@style='strong']">
  <strong><xsl:apply-templates /></strong>
</xsl:template>


<xsl:template match="vspace[not(@blankLines) or @blankLines=0]">
  <br />
</xsl:template>

<xsl:template match="vspace[@blankLines &gt; 0]">
  <br/><xsl:for-each select="//*[position() &lt;= @blankLines]"> <br /></xsl:for-each>
</xsl:template>

<xsl:template match="xref[node()]">
  <xsl:variable name="target" select="@target" />
  <xsl:variable name="node" select="//*[@anchor=$target]" />
  <a href="#{$target}"><xsl:apply-templates /></a>
  <xsl:for-each select="/rfc/back/references/reference[@anchor=$target]">
    <xsl:text> </xsl:text><xsl:call-template name="referencename">
       <xsl:with-param name="node" select="." />
    </xsl:call-template>
  </xsl:for-each>
</xsl:template>
               
<xsl:template match="xref[not(node())]">
  <xsl:variable name="context" select="." />
  <xsl:variable name="target" select="@target" />
  <xsl:variable name="node" select="//*[@anchor=$target]" />
  <!-- should check for undefined targets -->
  <a href="#{$target}">
    <xsl:choose>
      <xsl:when test="local-name($node)='section'">
        <xsl:for-each select="$node">
          <xsl:call-template name="sectiontype">
            <xsl:with-param name="prec" select="$context/preceding-sibling::node()[1]" />
          </xsl:call-template>
          <xsl:call-template name="sectionnumber" />
        </xsl:for-each>
      </xsl:when>
      <xsl:when test="local-name($node)='figure'">
        <xsl:text>Figure </xsl:text>
        <xsl:for-each select="$node">
          <xsl:number level="any" count="figure[@title!='' or @anchor!='']" />
        </xsl:for-each>
      </xsl:when>
      <xsl:otherwise>
        <xsl:attribute name="title"><xsl:value-of select="normalize-space($node/front/title)" /></xsl:attribute>
        <xsl:call-template name="referencename"><xsl:with-param name="node" select="/rfc/back/references/reference[@anchor=$target]" /></xsl:call-template></xsl:otherwise>
    </xsl:choose>
  </a>
</xsl:template>

<!-- mark unmatched elements red -->

<xsl:template match="*">
     <font color="red"><tt>&lt;<xsl:value-of select="name()" />&gt;</tt></font>
    <xsl:copy><xsl:apply-templates select="node()|@*" /></xsl:copy>
     <font color="red"><tt>&lt;/<xsl:value-of select="name()" />&gt;</tt></font>
</xsl:template>

<xsl:template match="/">
  <xsl:copy><xsl:apply-templates select="node()" /></xsl:copy>
</xsl:template>








<!-- utility templates -->

<xsl:template name="collectLeftHeaderColumn">
  <xsl:param name="mode" />
  <!-- default case -->
  <xsl:if test="not($private)">
    <myns:item>Network Working Group</myns:item>
    <myns:item>
       <xsl:choose>
        <xsl:when test="/rfc/@ipr and $mode='nroff'">Internet Draft</xsl:when>
        <xsl:when test="/rfc/@ipr">INTERNET DRAFT</xsl:when>
        <xsl:otherwise>Request for Comments: <xsl:value-of select="/rfc/@number"/></xsl:otherwise>
      </xsl:choose>
    </myns:item>
    <xsl:if test="/rfc/@docName and $mode!='nroff'">
      <myns:item>
        &lt;<xsl:value-of select="/rfc/@docName" />&gt;
      </myns:item>
    </xsl:if>
    <xsl:if test="/rfc/@obsoletes and /rfc/@obsoletes!=''">
      <myns:item>
        Obsoletes: <xsl:call-template name="rfclist">
          <xsl:with-param name="list" select="normalize-space(/rfc/@obsoletes)" />
        </xsl:call-template>
      </myns:item>
    </xsl:if>
    <xsl:if test="/rfc/@seriesNo">
       <myns:item>
        <xsl:choose>
          <xsl:when test="/rfc/@category='bcp'">BCP: <xsl:value-of select="/rfc/@seriesNo" /></xsl:when>
          <xsl:when test="/rfc/@category='info'">FYI: <xsl:value-of select="/rfc/@seriesNo" /></xsl:when>
          <xsl:when test="/rfc/@category='std'">STD: <xsl:value-of select="/rfc/@seriesNo" /></xsl:when>
          <xsl:otherwise><xsl:value-of select="concat(/rfc/@category,': ',/rfc/@seriesNo)" /></xsl:otherwise>
        </xsl:choose>
      </myns:item>
    </xsl:if>
    <xsl:if test="/rfc/@updates and /rfc/@updates!=''">
      <myns:item>
          Updates: <xsl:call-template name="rfclist">
             <xsl:with-param name="list" select="normalize-space(/rfc/@updates)" />
          </xsl:call-template>
      </myns:item>
    </xsl:if>
    <xsl:if test="$mode!='nroff'">
      <myns:item>
         Category:
        <xsl:call-template name="insertCategoryLong" />
      </myns:item>
    </xsl:if>
    <xsl:if test="/rfc/@ipr">
       <myns:item>Expires: <xsl:call-template name="expirydate" /></myns:item>
    </xsl:if>
  </xsl:if>
    
  <!-- private case -->
  <xsl:if test="$private">
    <myns:item><xsl:value-of select="$private" /></myns:item>
  </xsl:if>
</xsl:template>

<xsl:template name="collectRightHeaderColumn">
  <xsl:for-each select="author">
     <xsl:if test="@surname">
       <myns:item><xsl:value-of select="concat(@initials,' ',@surname)" /></myns:item>
    </xsl:if>
    <xsl:variable name="org"><xsl:choose>
      <xsl:when test="organization/@abbrev"><xsl:value-of select="organization/@abbrev" /></xsl:when>
      <xsl:otherwise><xsl:value-of select="organization" /></xsl:otherwise>
    </xsl:choose></xsl:variable>
    <xsl:variable name="orgOfFollowing"><xsl:choose>
      <xsl:when test="following-sibling::node()[1]/organization/@abbrev"><xsl:value-of select="following-sibling::node()[1]/organization/@abbrev" /></xsl:when>
      <xsl:otherwise><xsl:value-of select="following-sibling::node()/organization" /></xsl:otherwise>
    </xsl:choose></xsl:variable>
    <xsl:if test="$org != $orgOfFollowing">
       <myns:item><xsl:value-of select="$org" /></myns:item>
    </xsl:if>
  </xsl:for-each>
  <myns:item>
     <xsl:value-of select="concat(date/@month,' ',date/@year)" />
   </myns:item>
</xsl:template>


<xsl:template name="emitheader">
  <xsl:param name="lc" />
  <xsl:param name="rc" />

  <xsl:for-each select="$lc/myns:item | $rc/myns:item">
    <xsl:variable name="pos" select="position()" />
    <xsl:if test="$pos &lt; count($lc/myns:item) + 1 or $pos &lt; count($rc/myns:item) + 1"> 
      <tr>
        <td width="33%" bgcolor="#666666" class="header"><xsl:copy-of select="$lc/myns:item[$pos]/node()" />&#0160;</td>
        <td width="33%" bgcolor="#666666" class="header"><xsl:copy-of select="$rc/myns:item[$pos]/node()" />&#0160;</td>
      </tr>
    </xsl:if>
  </xsl:for-each>
</xsl:template>


<xsl:template name="expirydate">
  <xsl:variable name="date" select="/rfc/front/date" />
  <xsl:choose>
      <xsl:when test="$date/@month='January'">July <xsl:value-of select="$date/@year" /></xsl:when>
      <xsl:when test="$date/@month='February'">August <xsl:value-of select="$date/@year" /></xsl:when>
      <xsl:when test="$date/@month='March'">September <xsl:value-of select="$date/@year" /></xsl:when>
      <xsl:when test="$date/@month='April'">October <xsl:value-of select="$date/@year" /></xsl:when>
      <xsl:when test="$date/@month='May'">November <xsl:value-of select="$date/@year" /></xsl:when>
      <xsl:when test="$date/@month='June'">December <xsl:value-of select="$date/@year" /></xsl:when>
      <xsl:when test="$date/@month='July'">January <xsl:value-of select="$date/@year + 1" /></xsl:when>
      <xsl:when test="$date/@month='August'">February <xsl:value-of select="$date/@year + 1" /></xsl:when>
      <xsl:when test="$date/@month='September'">March <xsl:value-of select="$date/@year + 1" /></xsl:when>
      <xsl:when test="$date/@month='October'">April <xsl:value-of select="$date/@year + 1" /></xsl:when>
      <xsl:when test="$date/@month='November'">May <xsl:value-of select="$date/@year + 1" /></xsl:when>
      <xsl:when test="$date/@month='December'">June <xsl:value-of select="$date/@year + 1" /></xsl:when>
        <xsl:otherwise>WRONG SYNTAX FOR MONTH</xsl:otherwise>
     </xsl:choose>
</xsl:template>

<!-- produce back section with author information -->
<xsl:template name="insertAuthors">

  <!-- insert link to TOC including horizontal rule -->
  <xsl:call-template name="insertTocLink">
    <xsl:with-param name="rule" select="true()" />
  </xsl:call-template>
    
  <a name="{$anchor-prefix}.authors">
    <h1>Author's Address<xsl:if test="count(/rfc/front/author) &gt; 1">es</xsl:if></h1>
   </a>

  <table width="99%" border="0" cellpadding="0" cellspacing="0">
    <xsl:apply-templates select="/rfc/front/author" />
  </table>
</xsl:template>


<xsl:template name="insertAuthorSummary">
  <xsl:choose>
    <xsl:when test="count(/rfc/front/author)=1">
      <xsl:value-of select="/rfc/front/author[1]/@surname" />
    </xsl:when>
    <xsl:when test="count(/rfc/front/author)=2">
      <xsl:value-of select="concat(/rfc/front/author[1]/@surname,' &amp; ',/rfc/front/author[2]/@surname)" />
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="concat(/rfc/front/author[1]/@surname,' et al.')" />
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<!-- insert copyright statement -->

<xsl:template name="insertCopyright">

  <section title="Full Copyright Statement" anchor="{$anchor-prefix}.copyright" myns:unnumbered="unnumbered">

  <t>    
    Copyright (C) The Internet Society (<xsl:value-of select="/rfc/front/date/@year" />). All Rights Reserved.
  </t>

  <t>
    This document and translations of it may be copied and furnished to
    others, and derivative works that comment on or otherwise explain it or
    assist in its implementation may be prepared, copied, published and
    distributed, in whole or in part, without restriction of any kind,
    provided that the above copyright notice and this paragraph are included
    on all such copies and derivative works. However, this document itself
    may not be modified in any way, such as by removing the copyright notice
    or references to the Internet Society or other Internet organizations,
    except as needed for the purpose of developing Internet standards in
    which case the procedures for copyrights defined in the Internet
    Standards process must be followed, or as required to translate it into
    languages other than English.
  </t>

  <t>
    The limited permissions granted above are perpetual and will not be
    revoked by the Internet Society or its successors or assigns.
  </t>

  <t>
    This document and the information contained herein is provided on an
    "AS IS" basis and THE INTERNET SOCIETY AND THE INTERNET ENGINEERING
    TASK FORCE DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT
    NOT LIMITED TO ANY WARRANTY THAT THE USE OF THE INFORMATION HEREIN WILL
    NOT INFRINGE ANY RIGHTS OR ANY IMPLIED WARRANTIES OF MERCHANTABILITY OR
    FITNESS FOR A PARTICULAR PURPOSE.
  </t>
  </section>
  
  <section title="Acknowledgement" myns:unnumbered="unnumbered" myns:notoclink="notoclink">
  <t>
      Funding for the RFC editor function is currently provided by the
      Internet Society.
  </t>
  </section>

</xsl:template>


<!-- insert CSS style info -->

<xsl:template name="insertCss">
a
{
  text-decoration: none
}
a:hover
{
  text-decoration: underline
}
a:active
{
  text-decoration: underline
}
body
{
  <xsl:if test="$background!=''">
  background: url(<xsl:value-of select="$background" />) #ffffff left top;
  </xsl:if>
  color: #000000;
  font-family: helvetica, arial, sans-serif;
  font-size: 13px;
}
dl
{
  margin-left: 2em;
}
h1
{
  color: #333333;
  font-size: 16px;
  line-height: 16px;
  font-family: helvetica, arial, sans-serif;
  page-break-after: avoid;
}
h2
{
  color: #000000;
  font-size: 14px;
  font-family: helvetica, arial, sans-serif;
  page-break-after: avoid;
}
h3
{
  color: #000000;
  font-size: 13px;
  font-family: helvetica, arial, sans-serif;
  page-break-after: avoid;
}
p
{
  margin-left: 2em;
  margin-right: 2em;
}
pre
{
  margin-left: 3em;
  background-color: lightyellow;
}
table
{
  margin-left: 2em;
  font-size: 13px;  
}
td.top
{
  vertical-align: top;
}
td.header
{
  color: #ffffff;
  font-size: 10px;
  font-family: arial, helvetica, sans-serif;
  vertical-align: top
}
.editingmark
{
  background-color: khaki;
}
.hotText
{
  color:#ffffff;
  font-weight: normal;
  text-decoration: none;
  font-family: chelvetica, arial, sans-serif;
  font-size: 9px
}
.link2
{
  color:#ffffff;
  font-weight: bold;
  text-decoration: none;
  font-family: helvetica, arial, sans-serif;
  font-size: 9px
}
.toowide
{
  color: red;
  font-weight: bold;
}
.RFC
{
  color:#666666;
  font-weight: bold;
  text-decoration: none;
  font-family: helvetica, arial, sans-serif;
  font-size: 9px
}
.title
{
  color: #990000;
  font-size: 22px;
  line-height: 22px;
  font-weight: bold;
  text-align: right;
  font-family: helvetica, arial, sans-serif
}
.figure
{
  font-weight: bold;
  text-align: center;
  font-size: 9x;
}
.filename
{
  color: #333333;
  font-weight: bold;
  font-size: 16px;
  line-height: 24px;
  font-family: helvetica, arial, sans-serif;
}

del
{
  color: red;
}

ins
{
  color: blue;
}

@media print {
         .noprint {display:none}
}
</xsl:template>


<!-- generate the index section -->

<xsl:template name="insertSingleIref">
  <xsl:variable name="backlink">#<xsl:value-of select="$anchor-prefix"/>.iref.<xsl:number level="any" /></xsl:variable>
  &#0160;<a href="{$backlink}"><xsl:choose>
      <xsl:when test="@primary='true'"><b><xsl:call-template name="sectionnumber" /></b></xsl:when>
      <xsl:otherwise><xsl:call-template name="sectionnumber" /></xsl:otherwise>
    </xsl:choose>
  </a><xsl:if test="position()!=last()">, </xsl:if>
</xsl:template>


<xsl:template name="insertIndex">

  <!-- insert link to TOC including horizontal rule -->
  <xsl:call-template name="insertTocLink">
    <xsl:with-param name="rule" select="true()" />
  </xsl:call-template> 

  <a name="{$anchor-prefix}.index">
    <h1>Index</h1>
  </a>

  <table>
        
    <xsl:for-each select="//iref[generate-id(.) = generate-id(key('index-first-letter',translate(substring(@item,1,1),$lcase,$ucase)))]">
      <xsl:sort select="translate(@item,$lcase,$ucase)" />
            
      <tr>
        <td>
          <b><xsl:value-of select="translate(substring(@item,1,1),$lcase,$ucase)" /></b>
        </td>
      </tr>
            
      <xsl:for-each select="key('index-first-letter',translate(substring(@item,1,1),$lcase,$ucase))">
    
        <xsl:sort select="translate(@item,$lcase,$ucase)" />
         
        <xsl:if test="generate-id(.) = generate-id(key('index-item',@item))">
    
          <tr>
            <td>
              &#0160;&#0160;<xsl:value-of select="@item" />&#0160;
                
              <xsl:for-each select="key('index-item',@item)[not(@subitem) or @subitem='']">
                <xsl:sort select="translate(@item,$lcase,$ucase)" />
                <xsl:call-template name="insertSingleIref" />
              </xsl:for-each>
            </td>
          </tr>
                
          <xsl:for-each select="key('index-item',@item)[@subitem and @subitem!='']">
            <xsl:sort select="translate(@subitem,$lcase,$ucase)" />
            
             <xsl:if test="generate-id(.) = generate-id(key('index-item-subitem',concat(@item,'..',@subitem)))">
            <tr>
              <td>
                &#0160;&#0160;&#0160;&#0160;<xsl:value-of select="@subitem" />&#0160;
                  
                <xsl:for-each select="key('index-item-subitem',concat(@item,'..',@subitem))">
                  <xsl:sort select="translate(@item,$lcase,$ucase)" />                    
                  <xsl:call-template name="insertSingleIref" />
                </xsl:for-each>
              </td>
            </tr>
            </xsl:if>
          </xsl:for-each>
                
        </xsl:if>
                
      </xsl:for-each>            

    </xsl:for-each>
  </table>
</xsl:template>

<xsl:template name="insertCategoryLong">
  <xsl:choose>
    <xsl:when test="/rfc/@category='bcp'">Best Current Practice</xsl:when>
    <xsl:when test="/rfc/@category='info'">Informational</xsl:when>
    <xsl:when test="/rfc/@category='std'">Standards Track</xsl:when>
    <xsl:when test="/rfc/@category='exp'">Experimental</xsl:when>
    <xsl:otherwise>(category missing or unknown)</xsl:otherwise>
  </xsl:choose>
</xsl:template>



<xsl:template name="insertPreamble">

  <section title="Status of this Memo" myns:unnumbered="unnumbered" myns:notoclink="notoclink">

  <xsl:choose>
    <xsl:when test="/rfc/@ipr">
      <t>
        This document is an Internet-Draft and is 
        <xsl:choose>
          <xsl:when test="/rfc/@ipr = 'full2026'">
            in full conformance with all provisions of Section 10 of RFC2026.    
            </xsl:when>
          <xsl:when test="/rfc/@ipr = 'noDerivativeWorks2026'">
            in full conformance with all provisions of Section 10 of RFC2026
            except that the right to produce derivative works is not granted.   
            </xsl:when>
          <xsl:when test="/rfc/@ipr = 'noDerivativeWorksNow'">
            in full conformance with all provisions of Section 10 of RFC2026
            except that the right to produce derivative works is not granted.
            (If this document becomes part of an IETF working group activity,
            then it will be brought into full compliance with Section 10 of RFC2026.)  
            </xsl:when>
          <xsl:when test="/rfc/@ipr = 'none'">
            NOT offered in accordance with Section 10 of RFC2026,
            and the author does not provide the IETF with any rights other
            than to publish as an Internet-Draft.
            </xsl:when>
          <xsl:otherwise>CONFORMANCE UNDEFINED.</xsl:otherwise>
        </xsl:choose>

        Internet-Drafts are working documents of the Internet Engineering
        Task Force (IETF), its areas, and its working groups.
        Note that other groups may also distribute working documents as
        Internet-Drafts.
      </t>
      <t>
        Internet-Drafts are draft documents valid for a maximum of six months
        and may be updated, replaced, or obsoleted by other documents at any time.
        It is inappropriate to use Internet-Drafts as reference material or to cite
        them other than as "work in progress".
      </t>
      <t>
        The list of current Internet-Drafts can be accessed at
        <eref target='http://www.ietf.org/ietf/1id-abstracts.txt'>http://www.ietf.org/ietf/1id-abstracts.txt</eref>.
      </t>
      <t>
        The list of Internet-Draft Shadow Directories can be accessed at
        <eref target='http://www.ietf.org/shadow.html'>http://www.ietf.org/shadow.html</eref>.
      </t>
      <t>
        This Internet-Draft will expire in <xsl:call-template name="expirydate" />.
      </t>
    </xsl:when>

    <xsl:when test="/rfc/@category='bcp'">
      <t>
        This document specifies an Internet Best Current Practice for the Internet
        Community, and requests discussion and suggestions for improvements.
        Distribution of this memo is unlimited.
      </t>
    </xsl:when>
    <xsl:when test="/rfc/@category='exp'">
      <t>
        This memo defines an Experimental Protocol for the Internet community.
        It does not specify an Internet standard of any kind.
        Discussion and suggestions for improvement are requested.
        Distribution of this memo is unlimited.
      </t>
    </xsl:when>
    <xsl:when test="/rfc/@category='historic'">
      <t>
        This memo describes a historic protocol for the Internet community.
        It does not specify an Internet standard of any kind.
        Distribution of this memo is unlimited.
      </t>
    </xsl:when>
    <xsl:when test="/rfc/@category='info'">
      <t>
        This memo provides information for the Internet community.
        It does not specify an Internet standard of any kind.  
        Distribution of this memo is unlimited.
      </t>
    </xsl:when>
    <xsl:when test="/rfc/@category='std'">
      <t>
        This document specifies an Internet standards track protocol for the Internet
        community, and requests discussion and suggestions for improvements.
        Please refer to the current edition of the &quot;Internet Official Protocol
        Standards&quot; (STD 1) for the standardization state and status of this  
        protocol. Distribution of this memo is unlimited.
      </t>
    </xsl:when>
    <xsl:otherwise>
      <t>UNSUPPORTED CATEGORY.</t>
    </xsl:otherwise>
  </xsl:choose>
  
  </section>

  <section title="Copyright Notice" myns:unnumbered="yes" myns:notoclink="notoclink">
  <t>
    Copyright (C) The Internet Society (<xsl:value-of select="/rfc/front/date/@year" />). All Rights Reserved.
  </t>
  </section>
  
</xsl:template>

<!-- TOC generation -->

<xsl:template match="/" mode="toc">
  <xsl:call-template name="insertTocLink">
    <xsl:with-param name="includeTitle" select="true()" />
      <xsl:with-param name="rule" select="true()" />
  </xsl:call-template>

  <h1>
    <a name="{$anchor-prefix}.toc">Table of Contents</a>
  </h1>

  <p>
    <xsl:apply-templates mode="toc" />
  </p>
</xsl:template>

<xsl:template name="insertTocLine">
  <xsl:param name="number" />
  <xsl:param name="target" />
  <xsl:param name="title" />

  <!-- handle tocdepth parameter -->
  <xsl:choose>  
    <xsl:when test="string-length(translate($number,'.ABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890&#167;','.')) &gt;= $tocDepth">
      <!-- dropped entry -->
    </xsl:when>
    <xsl:otherwise>
      <xsl:choose>
        <xsl:when test="starts-with($number,'del-')">
          <xsl:value-of select="'&#160;&#160;&#160;&#160;&#160;&#160;'"/>
          <del>
            <xsl:value-of select="$number" />&#0160;
            <a href="#{$target}"><xsl:value-of select="$title"/></a>
          </del>
        </xsl:when>
        <xsl:when test="$number=''">
          <b>
            &#0160;&#0160;
            <a href="#{$target}"><xsl:value-of select="$title"/></a>
          </b>
        </xsl:when>
        <xsl:otherwise>
          <b>
            <xsl:value-of select="translate($number,'.ABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890&#167;','&#160;')"/>
            <xsl:value-of select="$number" />&#0160;
            <a href="#{$target}"><xsl:value-of select="$title"/></a>
          </b>
        </xsl:otherwise>
      </xsl:choose>
      <br />
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>


<xsl:template match="back" mode="toc">

  <xsl:apply-templates select="references" mode="toc" />
  <xsl:apply-templates select="/rfc/front" mode="toc" />
  <xsl:apply-templates select="*[not(self::references)]" mode="toc" />

  <!-- copyright statements -->
  <xsl:call-template name="insertTocLine">
    <xsl:with-param name="number" select="'&#167;'"/>
    <xsl:with-param name="target" select="concat($anchor-prefix,'.copyright')"/>
    <xsl:with-param name="title" select="'Full Copyright Statement'"/>
  </xsl:call-template>

  <!-- insert the index if index entries exist -->
  <xsl:if test="//iref">
    <xsl:call-template name="insertTocLine">
      <xsl:with-param name="number" select="'&#167;'"/>
      <xsl:with-param name="target" select="concat($anchor-prefix,'.index')"/>
      <xsl:with-param name="title" select="'Index'"/>
    </xsl:call-template>
  </xsl:if>

</xsl:template>

<xsl:template match="front" mode="toc">

  <xsl:variable name="title">
    <xsl:if test="count(author)=1">Author's Address</xsl:if>
    <xsl:if test="count(author)!=1">Author's Addresses</xsl:if>
  </xsl:variable>

  <xsl:call-template name="insertTocLine">
    <xsl:with-param name="number" select="'&#167;'"/>
    <xsl:with-param name="target" select="concat($anchor-prefix,'.authors')"/>
    <xsl:with-param name="title" select="$title"/>
  </xsl:call-template>

</xsl:template>

<xsl:template match="references" mode="toc">

  <xsl:variable name="target">
    <xsl:choose>
      <xsl:when test="@title"><xsl:value-of select="$anchor-prefix"/>.<xsl:value-of select="translate(@title,$plain,$touri)"/></xsl:when>
      <xsl:otherwise><xsl:value-of select="$anchor-prefix"/>.references</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="title">
    <xsl:choose>
      <xsl:when test="@title"><xsl:value-of select="@title" /></xsl:when>
      <xsl:otherwise>References</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:call-template name="insertTocLine">
    <xsl:with-param name="number" select="'&#167;'"/>
    <xsl:with-param name="target" select="$target"/>
    <xsl:with-param name="title" select="$title"/>
  </xsl:call-template>

</xsl:template>

<xsl:template match="section" mode="toc">
  <xsl:variable name="sectionNumber">
    <xsl:call-template name="sectionnumber" />
  </xsl:variable>

  <xsl:variable name="target">
    <xsl:choose>
      <xsl:when test="@anchor"><xsl:value-of select="@anchor" /></xsl:when>
       <xsl:otherwise><xsl:value-of select="$anchor-prefix"/>.section.<xsl:value-of select="$sectionNumber" /></xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:call-template name="insertTocLine">
    <xsl:with-param name="number" select="$sectionNumber"/>
    <xsl:with-param name="target" select="$target"/>
    <xsl:with-param name="title" select="@title"/>
  </xsl:call-template>

  <xsl:apply-templates mode="toc" />
</xsl:template>

<xsl:template match="middle" mode="toc">
  <xsl:apply-templates mode="toc" />
</xsl:template>

<xsl:template match="rfc" mode="toc">
  <xsl:apply-templates select="middle|back" mode="toc" />
</xsl:template>

<xsl:template match="ed:del|ed:ins|ed:replace" mode="toc">
  <xsl:apply-templates mode="toc" />
</xsl:template>

<xsl:template match="*" mode="toc" />


<xsl:template name="insertTocAppendix">
  
  <xsl:if test="//figure[@title!='' or @anchor!='']">
    <p>
      <xsl:for-each select="//figure[@title!='' or @anchor!='']">
        <xsl:variable name="title">Figure <xsl:value-of select="position()"/><xsl:if test="@title">: <xsl:value-of select="@title"/></xsl:if>
        </xsl:variable>
        <xsl:call-template name="insertTocLine">
          <xsl:with-param name="target" select="concat($anchor-prefix,'.figure.',position())" />
          <xsl:with-param name="title" select="$title" />
        </xsl:call-template>
      </xsl:for-each>
    </p>
  </xsl:if>
  
  <!-- experimental -->
  <xsl:if test="//ed:issue">
    <xsl:call-template name="insertIssuesList" />
  </xsl:if>

</xsl:template>

<xsl:template name="insertTocLink">
  <xsl:param name="includeTitle" select="false()" />
  <xsl:param name="rule" />
  <xsl:if test="$rule"><hr class="noprint"/></xsl:if>
  <xsl:if test="$includeTitle or $includeToc='yes'">
    <table class="noprint" border="0" cellpadding="0" cellspacing="2" width="30" height="15" align="right">
      <xsl:if test="$includeTitle">
        <tr>
          <td bgcolor="#000000" align="center" valign="center" width="30" height="30">
            <b><span class="RFC">&#0160;RFC&#0160;</span></b><br />
            <span class="hotText"><xsl:value-of select="/rfc/@number"/></span>
          </td>
        </tr>
      </xsl:if>
      <xsl:if test="$includeToc='yes'">
        <tr>
          <td bgcolor="#990000" align="center" width="30" height="15">
                 <a href="#{$anchor-prefix}.toc" CLASS="link2"><b class="link2">&#0160;TOC&#0160;</b></a>
          </td>
        </tr>
      </xsl:if>
    </table>
  </xsl:if>
</xsl:template>


<xsl:template name="referencename">
  <xsl:param name="node" />
  <xsl:choose>
    <xsl:when test="$useSymrefs='yes'">[<xsl:value-of select="$node/@anchor" />]</xsl:when>
    <xsl:otherwise><xsl:for-each select="$node">[<xsl:number level="any" />]</xsl:for-each></xsl:otherwise>
  </xsl:choose>
</xsl:template>



<xsl:template name="replace-substring">

  <xsl:param name="string" />
  <xsl:param name="replace" />
  <xsl:param name="by" />

  <xsl:choose>
    <xsl:when test="contains($string,$replace)">
      <xsl:value-of select="concat(substring-before($string, $replace),$by)" />
      <xsl:call-template name="replace-substring">
        <xsl:with-param name="string" select="substring-after($string,$replace)" />
        <xsl:with-param name="replace" select="$replace" />
        <xsl:with-param name="by" select="$by" />
      </xsl:call-template>
    </xsl:when>
    <xsl:otherwise><xsl:value-of select="$string" /></xsl:otherwise>
  </xsl:choose>

</xsl:template>

<xsl:template name="showArtworkLine">
  <xsl:param name="line" />
  <xsl:param name="mode" />
  
  <xsl:variable name="maxw" select="69" />
  
  <xsl:if test="string-length($line) &gt; $maxw">
    <xsl:message>Artwork exceeds maximum width: <xsl:value-of select="$line" /></xsl:message>
  </xsl:if>
  
  <xsl:choose>
    <xsl:when test="$mode='html'">
      <xsl:value-of select="substring($line,0,$maxw)" />
      <xsl:if test="string-length($line) &gt;= $maxw">
        <span class="toowide"><xsl:value-of select="substring($line,$maxw)" /></span>
      </xsl:if>
      <xsl:text>&#10;</xsl:text>
    </xsl:when>
    <xsl:when test="$mode='nroff'">
      <xsl:variable name="cline">
        <xsl:call-template name="replace-substring">
          <xsl:with-param name="string" select="$line" />
          <xsl:with-param name="replace" select="'\'" />
          <xsl:with-param name="by" select="'\\'" />
        </xsl:call-template>
      </xsl:variable>
      <xsl:value-of select="concat($cline,'&#10;')" />
    </xsl:when>
    <xsl:otherwise><xsl:value-of select="concat($line,'&#10;')" /></xsl:otherwise>
  </xsl:choose>
  
</xsl:template>

<xsl:template name="showArtwork">
  <xsl:param name="mode" />
  <xsl:param name="text" />
  <xsl:param name="initial" />
  <xsl:variable name="delim" select="'&#10;'" />
  <xsl:variable name="first" select="substring-before($text,$delim)" />
  <xsl:variable name="remainder" select="substring-after($text,$delim)" />
  
  <xsl:choose>
    <xsl:when test="not(contains($text,$delim))">
      <xsl:call-template name="showArtworkLine">
        <xsl:with-param name="line" select="$text" />
        <xsl:with-param name="mode" select="$mode" />
      </xsl:call-template>
    </xsl:when>
    <xsl:otherwise>
      <!-- suppress empty initial lines -->
      <xsl:if test="$initial!='yes' or normalize-space($first)!=''">
        <xsl:call-template name="showArtworkLine">
          <xsl:with-param name="line" select="$first" />
          <xsl:with-param name="mode" select="$mode" />
        </xsl:call-template>
      </xsl:if>
      <xsl:if test="$remainder!=''">
        <xsl:call-template name="showArtwork">
          <xsl:with-param name="text" select="$remainder" />
          <xsl:with-param name="mode" select="$mode" />
          <xsl:with-param name="initial" select="'no'" />
        </xsl:call-template>
      </xsl:if>
    </xsl:otherwise>
  </xsl:choose>
  
</xsl:template>


<!--<xsl:template name="dump">
  <xsl:param name="text" />
  <xsl:variable name="c" select="substring($text,1,1)"/>
  <xsl:choose>
    <xsl:when test="$c='&#9;'">&amp;#9;</xsl:when>
    <xsl:when test="$c='&#10;'">&amp;#10;</xsl:when>
    <xsl:when test="$c='&#13;'">&amp;#13;</xsl:when>
    <xsl:when test="$c='&amp;'">&amp;amp;</xsl:when>
    <xsl:otherwise><xsl:value-of select="$c" /></xsl:otherwise>
  </xsl:choose>
  <xsl:if test="string-length($text) &gt; 1">
    <xsl:call-template name="dump">
      <xsl:with-param name="text" select="substring($text,2)" />
    </xsl:call-template>
  </xsl:if>
</xsl:template>-->


<xsl:template name="rfclist">
  <xsl:param name="list" />
  <xsl:choose>
      <xsl:when test="contains($list,',')">
          <xsl:variable name="rfcNo" select="substring-before($list,',')" />
          <a href="{concat($rfcUrlPrefix,$rfcNo,'.txt')}"><xsl:value-of select="$rfcNo" /></a>,
          <xsl:call-template name="rfclist">
              <xsl:with-param name="list" select="normalize-space(substring-after($list,','))" />
            </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
          <xsl:variable name="rfcNo" select="$list" />
          <a href="{concat($rfcUrlPrefix,$rfcNo,'.txt')}"><xsl:value-of select="$rfcNo" /></a>
         </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:variable name="hasEdits" select="count(//ed:del|//ed:ins)!=0" />

<xsl:template name="sectionnumber">
  <xsl:choose>
    <xsl:when test="$hasEdits">
      <xsl:call-template name="sectionnumberAndEdits" />
    </xsl:when>
    <xsl:otherwise>
      <xsl:choose>
        <xsl:when test="ancestor::back"><xsl:number count="ed:del|ed:ins|section|appendix" level="multiple" format="A.1.1.1.1.1.1.1" /></xsl:when>
        <xsl:when test="self::appendix"><xsl:number count="ed:del|ed:ins|appendix" level="multiple" format="A.1.1.1.1.1.1.1" /></xsl:when>
        <xsl:otherwise><xsl:number count="ed:del|ed:ins|section" level="multiple"/></xsl:otherwise>
      </xsl:choose>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template name="endsWithDot">
  <xsl:param name="str"/>
  <xsl:choose>
    <xsl:when test="contains($str,'.') and substring-after($str,'.')=''" ><xsl:value-of select="true()"/></xsl:when>
    <xsl:when test="not(contains($str,'.'))" ><xsl:value-of select="false()"/></xsl:when>
    <xsl:otherwise>
      <xsl:call-template name="endsWithDot">
        <xsl:with-param name="str" select="substring-after($str,'.')" /> 
      </xsl:call-template>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>


<xsl:template name="sectiontype">
  <xsl:param name="prec" />
  <xsl:variable name="startOfSentence">
    <xsl:call-template name="endsWithDot">
      <xsl:with-param name="str" select="normalize-space($prec)"/>
    </xsl:call-template>
  </xsl:variable>
  <xsl:choose>
    <xsl:when test="ancestor::back and $startOfSentence='true'">Appendix </xsl:when>
    <xsl:when test="ancestor::back">appendix </xsl:when>
    <xsl:when test="$startOfSentence='true'">Section </xsl:when>
    <xsl:otherwise>section </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template name="sectionnumberPara">
  <!-- get section number of ancestor section element, then add t or figure number -->
  <xsl:if test="ancestor::section">
    <xsl:for-each select="ancestor::section[1]"><xsl:call-template name="sectionnumber" />.p.</xsl:for-each><xsl:number count="t|figure" />
  </xsl:if>
</xsl:template>

<xsl:template name="editingMark">
  <xsl:if test="$insertEditingMarks='yes' and ancestor::rfc">
    <sup><span class="editingmark"><xsl:number level="any" count="postamble|preamble|t"/></span></sup>&#0160;
  </xsl:if>
</xsl:template>

<!-- experimental annotation support -->

<xsl:template match="ed:issue">
  <xsl:variable name="style">
    <xsl:choose>
      <xsl:when test="@status='closed'">background-color: grey; border-width: thin; border-style: solid; border-color: black; text-decoration: line-through </xsl:when>
      <xsl:otherwise>background-color: khaki; border-width: thin; border-style: solid; border-color: black;</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  
  <a name="{$anchor-prefix}.issue.{@name}">
   <table style="{$style}"> <!-- align="right" width="50%"> -->
      <tr>
        <td colspan="3">
          <xsl:choose>
            <xsl:when test="@href">
              <em><a href="{@href}"><xsl:value-of select="@name" /></a></em>
            </xsl:when>
            <xsl:otherwise>
              <em><xsl:value-of select="@name" /></em>
            </xsl:otherwise>
          </xsl:choose>
          &#0160;
          (type: <xsl:value-of select="@type"/>, status: <xsl:value-of select="@status"/>)
        </td>
      </tr>
      <xsl:for-each select="ed:item">
        <tr>
          <td valign="top">
            <a href="mailto:{@entered-by}?subject={/rfc/@docName}, {../@name}"><i><xsl:value-of select="@entered-by"/></i></a>
          </td>
          <td nowrap="nowrap" valign="top">
            <xsl:value-of select="@date"/>
          </td>
          <td valign="top">
            <xsl:copy-of select="node()" />
          </td>
        </tr>
      </xsl:for-each>
      <xsl:for-each select="ed:resolution">
        <tr>
          <td valign="top">
            <xsl:if test="@entered-by">
              <a href="mailto:{@entered-by}?subject={/rfc/@docName}, {../@name}"><i><xsl:value-of select="@entered-by"/></i></a>
            </xsl:if>
          </td>
          <td nowrap="nowrap" valign="top">
            <xsl:value-of select="@date"/>
          </td>
          <td valign="top">
            <em>Resolution:</em>&#0160;<xsl:copy-of select="node()" />
          </td>
        </tr>
      </xsl:for-each>      
    </table>
  </a>
    
</xsl:template>

<xsl:template name="insertIssuesList">

  <h2>Issues list</h2>
  <p>
  <table>
    <xsl:for-each select="//ed:issue">
      <xsl:sort select="@status" />
      <xsl:sort select="@name" />
      <tr>
        <td><a href="#{$anchor-prefix}.issue.{@name}"><xsl:value-of select="@name" /></a></td>
        <td><xsl:value-of select="@type" /></td>
        <td><xsl:value-of select="@status" /></td>
        <td><xsl:value-of select="ed:item[1]/@date" /></td>
        <td><a href="mailto:{ed:item[1]/@entered-by}?subject={/rfc/@docName}, {@name}"><xsl:value-of select="ed:item[1]/@entered-by" /></a></td>
      </tr>
    </xsl:for-each>
  </table>
  </p>
  
</xsl:template>

<xsl:template name="formatTitle">
  <xsl:if test="@who">
    <xsl:value-of select="@who" />
  </xsl:if>
  <xsl:if test="@datetime">
    <xsl:value-of select="concat(' (',@datetime,')')" />
  </xsl:if>
  <xsl:if test="@reason">
    <xsl:value-of select="concat(': ',@reason)" />
  </xsl:if>
  <xsl:if test="@cite">
    <xsl:value-of select="concat(' &lt;',@cite,'&gt;')" />
  </xsl:if>
</xsl:template>

<xsl:template name="insertDiagnostics">
  
  <!-- check anchor names -->
  <xsl:variable name="badAnchors" select="//*[starts-with(@anchor,$anchor-prefix)]" />
  <xsl:if test="$badAnchors">
    <p>
      The following anchor names may collide with internally generated anchors because of their prefix "<xsl:value-of select="$anchor-prefix" />":
      <xsl:for-each select="$badAnchors">
        <xsl:value-of select="@anchor"/><xsl:if test="position()!=last()">, </xsl:if>
      </xsl:for-each>
    </p>
    <xsl:message>
      The following anchor names may collide with internally generated anchors because of their prefix "<xsl:value-of select="$anchor-prefix" />":
      <xsl:for-each select="$badAnchors">
        <xsl:value-of select="@anchor"/><xsl:if test="position()!=last()">, </xsl:if>
      </xsl:for-each>
    </xsl:message>
  </xsl:if>
  
</xsl:template>

<!-- special change mark support, not supported by RFC2629 yet -->

<xsl:template match="ed:del">
  <del>
    <xsl:copy-of select="@*"/>
    <xsl:if test="not(@title) and @ed:entered-by and @datetime">
      <xsl:attribute name="title"><xsl:value-of select="concat(@datetime,', ',@ed:entered-by)"/></xsl:attribute>
    </xsl:if>
    <xsl:apply-templates />
  </del>
</xsl:template>

<xsl:template match="ed:ins">
  <ins>
    <xsl:copy-of select="@*"/>
    <xsl:if test="not(@title) and @ed:entered-by and @datetime">
      <xsl:attribute name="title"><xsl:value-of select="concat(@datetime,', ',@ed:entered-by)"/></xsl:attribute>
    </xsl:if>
    <xsl:if test="@ed:resolves">
      <table style="background-color: khaki; border-width: thin; border-style: solid; border-color: black;" align="right">
        <tr><td>resolves: <a href="#{$anchor-prefix}.issue.{@ed:resolves}"><xsl:value-of select="@ed:resolves"/></a></td></tr>
      </table>
    </xsl:if>
    <xsl:apply-templates />
  </ins>
</xsl:template>

<xsl:template match="ed:replace">
  <del>
    <xsl:copy-of select="@*"/>
    <xsl:if test="not(@title) and @ed:entered-by and @datetime">
      <xsl:attribute name="title"><xsl:value-of select="concat(@datetime,', ',@ed:entered-by)"/></xsl:attribute>
    </xsl:if>
    <xsl:apply-templates select="ed:del/node()" />
  </del>
  <ins>
    <xsl:copy-of select="@*"/>
    <xsl:if test="not(@title) and @ed:entered-by and @datetime">
      <xsl:attribute name="title"><xsl:value-of select="concat(@datetime,', ',@ed:entered-by)"/></xsl:attribute>
    </xsl:if>
    <xsl:if test="@ed:resolves">
      <table style="background-color: khaki; border-width: thin; border-style: solid; border-color: black;" align="right">
        <tr><td>resolves: <a href="#{$anchor-prefix}.issue.{@ed:resolves}"><xsl:value-of select="@ed:resolves"/></a></td></tr>
      </table>
    </xsl:if>
    <xsl:apply-templates select="ed:ins/node()" />
  </ins>
</xsl:template>

<xsl:template name="sectionnumberAndEdits">
  <xsl:choose>
    <xsl:when test="ancestor::ed:del">del-<xsl:number count="ed:del//section" level="any"/></xsl:when>
    <xsl:when test="self::section and parent::ed:ins and local-name(../..)='replace'">
      <xsl:for-each select="../.."><xsl:call-template name="sectionnumberAndEdits" /></xsl:for-each>
      <xsl:for-each select="..">
        <xsl:if test="parent::ed:replace">
          <xsl:for-each select="..">
            <xsl:if test="parent::section">.</xsl:if><xsl:value-of select="1+count(preceding-sibling::section|preceding-sibling::ed:ins/section|preceding-sibling::ed:replace/ed:ins/section)" />
          </xsl:for-each>
        </xsl:if>
      </xsl:for-each>
    </xsl:when>
    <xsl:when test="self::section[parent::ed:ins]">
      <xsl:for-each select="../.."><xsl:call-template name="sectionnumberAndEdits" /></xsl:for-each>
      <xsl:for-each select="..">
        <xsl:if test="parent::section">.</xsl:if><xsl:value-of select="1+count(preceding-sibling::section|preceding-sibling::ed:ins/section|preceding-sibling::ed:replace/ed:ins/section)" />
      </xsl:for-each>
    </xsl:when>
    <xsl:when test="self::section">
      <xsl:for-each select=".."><xsl:call-template name="sectionnumberAndEdits" /></xsl:for-each>
      <xsl:if test="parent::section">.</xsl:if>
      <xsl:choose>
        <xsl:when test="parent::back">
          <xsl:number format="A" value="1+count(preceding-sibling::section|preceding-sibling::ed:ins/section|preceding-sibling::ed:replace/ed:ins/section)" />
        </xsl:when>
        <xsl:otherwise>
          <xsl:number value="1+count(preceding-sibling::section|preceding-sibling::ed:ins/section|preceding-sibling::ed:replace/ed:ins/section)" />
        </xsl:otherwise>
      </xsl:choose>
    </xsl:when>
    <xsl:when test="self::middle or self::back"><!-- done --></xsl:when>
    <xsl:otherwise>
      <!-- go up one level -->
      <xsl:for-each select=".."><xsl:call-template name="sectionnumberAndEdits" /></xsl:for-each>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<!-- experimental table formatting -->

<xsl:template match="texttable">
  <xsl:apply-templates select="preamble" />
  <table>
    <thead>
      <tr>
        <xsl:apply-templates select="ttcol" />
      </tr>
    </thead>
    <tbody>
      <xsl:variable name="columns" select="count(ttcol)" />
      <xsl:for-each select="c[(position() mod $columns) = 1]">
        <tr>
          <xsl:for-each select=". | following-sibling::c[position() &lt; $columns]">
            <td>
              <xsl:variable name="pos" select="position()" />
              <xsl:variable name="col" select="../ttcol[position() = $pos]" />
              <xsl:if test="$col/@align">
                <xsl:attribute name="align"><xsl:value-of select="$col/@align" /></xsl:attribute>
              </xsl:if>
              <xsl:apply-templates select="node()" />
            </td>
          </xsl:for-each>
        </tr>
      </xsl:for-each>
    </tbody>
  </table>
  <xsl:apply-templates select="postamble" />
</xsl:template>

<xsl:template match="ttcol">
  <th>
    <xsl:if test="@width">
      <xsl:attribute name="width"><xsl:value-of select="@width" /></xsl:attribute>
    </xsl:if>
    <xsl:choose>
      <xsl:when test="@align">
        <xsl:attribute name="align"><xsl:value-of select="@align" /></xsl:attribute>
      </xsl:when>
      <xsl:otherwise>
        <xsl:attribute name="align">left</xsl:attribute>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates />
  </th>
</xsl:template>

<!-- Chapter Link Generation -->

<xsl:template match="node()" mode="links"><xsl:apply-templates mode="links"/></xsl:template>

<xsl:template match="/*/middle//section[not(myns:unnumbered) and not(ancestor::section)]" mode="links">
  <xsl:variable name="sectionNumber"><xsl:call-template name="sectionnumber" /></xsl:variable>
  <link rel="Chapter" title="{$sectionNumber} {@title}" href="#rfc.section.{$sectionNumber}" />
  <xsl:apply-templates mode="links" />
</xsl:template>

<xsl:template match="/*/back//section[not(myns:unnumbered) and not(ancestor::section)]" mode="links">
  <xsl:variable name="sectionNumber"><xsl:call-template name="sectionnumber" /></xsl:variable>
  <link rel="Appendix" title="{$sectionNumber} {@title}" href="#rfc.section.{$sectionNumber}" />
  <xsl:apply-templates mode="links" />
</xsl:template>

</xsl:stylesheet>
