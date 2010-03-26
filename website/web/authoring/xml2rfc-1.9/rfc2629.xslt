<!--
	XSLT transformation from RFC2629 XML format to HTML
    
    Copyright (c) 2001 Julian F. Reschke (julian.reschke@greenbytes.de)
    
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
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0"
                xmlns:xalan="http://xml.apache.org/xalan"
                xmlns:msxsl="urn:schemas-microsoft-com:xslt"
                xmlns:saxon="http://icl.com/saxon"
                xmlns:myns="mailto:julian.reschke@greenbytes.de?subject=rcf2629.xslt"
                exclude-result-prefixes="msxsl xalan saxon myns"
                xmlns="http://www.w3.org/1999/xhtml"
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

<!-- use symbolic reference names instead of numeric ones if a processing instruction <?rfc?>
     exists with contents symrefs="yes". Can be overriden by an XSLT parameter -->

<xsl:param name="useSymrefs"
	select="substring-after(
    	translate(/processing-instruction('rfc')[contains(.,'symrefs=')], '&quot; ', ''),
        'symrefs=')"
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
    	translate(/processing-instruction('rfc')[contains(.,'private=')], '&quot; ', ''),
        'private=')"
/>

<!-- URL prefix for RFCs. -->

<xsl:param name="rfcUrlPrefix" select="'http://www.ietf.org/rfc/rfc'" />


<!-- build help keys for indices -->

<xsl:key name="index-first-letter"
	match="iref"
    use="translate(substring(@item,1,1),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ')" />

<xsl:key name="index-item"
	match="iref"
    use="@item" />

<xsl:key name="index-item-subitem"
	match="iref"
    use="concat(@item,'..',@subitem)" />


<!-- Templates for the various elements of rfc2629.dtd -->
              
<xsl:template match="abstract">
    <h1>Abstract</h1>
	<xsl:apply-templates />
</xsl:template>

<xsl:template match="artwork">
	<pre><xsl:apply-templates /></pre>
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
	<xsl:if test="address/postal/street">
    <tr>
      <td>&#0160;</td>
      <td><xsl:for-each select="address/postal/street"><xsl:value-of select="." /><br /></xsl:for-each></td>
    </tr>
  </xsl:if>
	<xsl:if test="address/postal/city">
    <tr>
      <td>&#0160;</td>
	    <td><xsl:value-of select="concat(address/postal/city,', ',address/postal/region,' ',address/postal/code)" /></td>
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
			<td><a href="mailto:{address/email}"><xsl:value-of select="address/email" /></a></td>
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
	<xsl:apply-templates select="*[name()!='references']" />

	<!-- insert the index if index entries exist -->
    <xsl:if test="//iref">
    	<xsl:call-template name="insertIndex" />
    </xsl:if>

	<!-- copyright statements -->
    <xsl:call-template name="insertCopyright" />
        
</xsl:template>

<xsl:template match="eref">
	<a href="{@target}"><xsl:apply-templates /></a>
</xsl:template>
               
<xsl:template match="figure">
	<xsl:apply-templates />
</xsl:template>

<xsl:template match="front">

	<xsl:call-template name="insertTocLink">
		<xsl:with-param name="includeTitle" select="true()" />
	</xsl:call-template>
            
	<!-- collect information for left column -->
    
	<xsl:variable name="leftColumn">
    
    <!-- default case -->
    <xsl:if test="not($private)">
    	<myns:item>Network Working Group</myns:item>
      <myns:item>
      	<xsl:choose>
          <xsl:when test="/rfc/@ipr">INTERNET DRAFT</xsl:when>
          <xsl:otherwise>Request for Comments: <xsl:value-of select="/rfc/@number"/></xsl:otherwise>
        </xsl:choose>
      </myns:item>
      <xsl:if test="/rfc/@docName">
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
      <myns:item>
       	Category:
        <xsl:call-template name="insertCategoryLong" />
      </myns:item>
      <xsl:if test="/rfc/@ipr">
       	<myns:item>Expires: <xsl:call-template name="expirydate" /></myns:item>
      </xsl:if>
    </xsl:if>
    
    <!-- private case -->
    <xsl:if test="$private">
      <myns:item><xsl:value-of select="$private" /></myns:item>
    </xsl:if>
    
  </xsl:variable>

    <!-- collect information for right column -->
    
    <xsl:variable name="rightColumn">
    	<xsl:for-each select="author">
        	<xsl:if test="@surname">
            	<myns:item><xsl:value-of select="concat(@initials,' ',@surname)" /></myns:item>
            </xsl:if>
			<xsl:variable name="orgOfFollowing" select="string(following-sibling::node()/organization/@abbrev)" />
            <xsl:if test="string(organization/@abbrev) != $orgOfFollowing">
				<myns:item><xsl:value-of select="organization/@abbrev" /></myns:item>
    		</xsl:if>
        </xsl:for-each>
        <myns:item>
        	<xsl:value-of select="concat(date/@month,' ',date/@year)" />
       	</myns:item>
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
  
  <xsl:call-template name="insertStatus" />
        

	<h1>Copyright Notice</h1>
	<p>
		Copyright (C) The Internet Society (<xsl:value-of select="/rfc/front/date/@year" />). All Rights Reserved.
    </p>

	<xsl:apply-templates select="abstract" />
	<xsl:apply-templates select="note" />

	<xsl:if test="$includeToc='yes'">
		<xsl:call-template name="insertToc" />
	</xsl:if>

</xsl:template>

<xsl:template match="iref">
	<a><xsl:attribute name="name">#rfc.iref.<xsl:number level="any"/></xsl:attribute></a>
</xsl:template>

<!-- list templates depend on the list style -->

<xsl:template match="list[@style='empty' or not(@style)]">
	<blockquote>
    	<xsl:apply-templates />
    </blockquote>
</xsl:template>

<xsl:template match="list[@style='hanging']">
	<blockquote>
    	<dl>
    		<xsl:apply-templates />
    	</dl>
   	</blockquote>
</xsl:template>

<xsl:template match="list[@style='numbers']">
	<blockquote><ol class="text">
    	<xsl:apply-templates />
	</ol></blockquote>
</xsl:template>

<xsl:template match="list[@style='symbols']">
	<ul class="text">
    	<xsl:apply-templates />
  </ul>
</xsl:template>

<!-- same for t(ext) elements -->

<xsl:template match="list[@style='empty' or not(@style)]/t">
	<p>
    	<xsl:apply-templates />
    </p>
</xsl:template>

<xsl:template match="list[@style='numbers' or @style='symbols']/t">
	<li>
    	<xsl:apply-templates />
    </li>
</xsl:template>

<xsl:template match="list[@style='hanging']/t">
	<dt><xsl:value-of select="@hangText" /></dt>
    <dd>
    	<xsl:apply-templates />
    </dd>
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
    	<xsl:apply-templates />
    </p>
</xsl:template>

<xsl:template match="preamble">
	<p>
    <xsl:if test="$insertEditingMarks='yes'"><sup><xsl:number level="any" count="preamble|t"/></sup></xsl:if>
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
	            <xsl:value-of select="
    	           	concat(
                   		$rfcUrlPrefix,
        				substring-after (normalize-space($rfcRef), ' '),
                      	'.txt')
               	" />
          	</xsl:when>
            <xsl:otherwise />
    	</xsl:choose>
	</xsl:variable>
	
    <tr>
       	<td valign="top">
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
                   	<xsl:when test="@surname">
        				<xsl:choose>
 		                   	<xsl:when test="address/email">
                               	<a href="mailto:{address/email}">
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
			       	"<a href="{$target}"><xsl:value-of select="front/title" /></a>",
    			</xsl:when>
        		<xsl:otherwise>
           			"<xsl:value-of select="front/title" />",
                </xsl:otherwise>
         	</xsl:choose>
            
            <xsl:for-each select="seriesInfo">
               	<xsl:choose>
                   	<xsl:when test="not(@name) and not(@value) and ./text()"><xsl:value-of select="." /></xsl:when>
					<xsl:otherwise><xsl:value-of select="@name" />&#0160;<xsl:value-of select="@value" /></xsl:otherwise>
                </xsl:choose>,
          	</xsl:for-each>
            
            <xsl:value-of select="front/date/@month" />&#0160;<xsl:value-of select="front/date/@year" />.
       	</td>
    </tr>

</xsl:template>


<xsl:template match="references">
	
    <xsl:call-template name="insertTocLink">
    	<xsl:with-param name="rule" select="true()" />
   	</xsl:call-template>
	
    <a name="rfc.references">
    	<h1>References</h1>
   	</a>
	
    <table border="0">
    	<xsl:apply-templates />
   	</table>

</xsl:template>

<xsl:template match="references[@title]">
	
    <xsl:call-template name="insertTocLink">
    	<xsl:with-param name="rule" select="true()" />
   	</xsl:call-template>
	
    <a name="rfc.references.{@title}">
    	<h1><xsl:value-of select="@title" /></h1>
   	</a>
	
    <table border="0">
    	<xsl:apply-templates />
   	</table>

</xsl:template>

<xsl:template match="rfc">
	<html>
    <head>
      <title><xsl:value-of select="front/title" /></title>
 			<style type="text/css">
        <xsl:call-template name="insertCss" />
      </style>
    </head>
		<body>
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
    <xsl:if test="$insertEditingMarks='yes'"><sup><xsl:number level="any" count="preamble|t"/></sup></xsl:if>
    <xsl:if test="string-length($paraNumber) &gt; 0"><a name="rfc.section.{$paraNumber}" /></xsl:if>
    <xsl:apply-templates />
  </p>
</xsl:template>
               
               
<xsl:template match="section">

    <xsl:variable name="sectionNumber">
		<xsl:call-template name="sectionnumber" />
    </xsl:variable>
    
    <xsl:if test="not(ancestor::section)">
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
    	<a name="rfc.section.{$sectionNumber}"><xsl:value-of select="$sectionNumber" /></a>.&#0160;
        <xsl:choose>
	        <xsl:when test="@anchor">
    	    	<a name="{@anchor}"><xsl:value-of select="@title" /></a>
       		</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="@title" />
           	</xsl:otherwise>
     	</xsl:choose>
    </xsl:element>
    <xsl:apply-templates />
</xsl:template>

<xsl:template match="vspace[not(@blankLines)]">
  <br />
</xsl:template>

<xsl:template match="vspace[@blankLines]">
  <br/><xsl:for-each select="//*[position() &lt; @blankLines]"><br /></xsl:for-each>
</xsl:template>

<xsl:template match="xref[node()]">
	<xsl:variable name="target" select="@target" />
    <xsl:variable name="node" select="//*[@anchor=$target]" />
	<a href="#{$target}"><xsl:apply-templates /></a>
    <xsl:if test="/rfc/back/references/reference[@anchor=$target]">
    	<sup><small><xsl:call-template name="referencename">
		   	<xsl:with-param name="node" select="." />
        </xsl:call-template></small></sup>
  	</xsl:if>
</xsl:template>
               
<xsl:template match="xref[not(node())]">
	<xsl:variable name="target" select="@target" />
  <xsl:variable name="node" select="//*[@anchor=$target]" />
	<a href="#{$target}">
    <xsl:choose>
      <xsl:when test="local-name($node)='section'">
        section
        <xsl:for-each select="$node">
          <xsl:number level="multiple" />
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
    
    <a name="rfc.authors">
    	<h1>Author's Address<xsl:if test="count(/rfc/front/author) &gt; 1">es</xsl:if></h1>
 	</a>

	<table width="99%" border="0" cellpadding="0" cellspacing="0">
    	<xsl:for-each select="/rfc/front/author">
        	<xsl:apply-templates select="." />
    	</xsl:for-each>
	</table>
</xsl:template>


<!-- insert copyright statement -->

<xsl:template name="insertCopyright">

	<!-- insert link to TOC including horizontal rule -->
	<xsl:call-template name="insertTocLink">
		<xsl:with-param name="rule" select="true()" />
	</xsl:call-template> 

	<a name="rfc.copyright">
    	<h1>Full Copyright Statement</h1>
   	</a>

	<p class="copyright">    
		Copyright (C) The Internet Society (<xsl:value-of select="/rfc/front/date/@year" />). All Rights Reserved.
	</p>

	<p class="copyright">
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
	</p>

	<p class="copyright">
		The limited permissions granted above are perpetual and will not be
        revoked by the Internet Society or its successors or assigns.
	</p>

	<p class="copyright">
		This document and the information contained herein is provided on an
        "AS IS" basis and THE INTERNET SOCIETY AND THE INTERNET ENGINEERING
        TASK FORCE DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT
        NOT LIMITED TO ANY WARRANTY THAT THE USE OF THE INFORMATION HEREIN WILL
        NOT INFRINGE ANY RIGHTS OR ANY IMPLIED WARRANTIES OF MERCHANTABILITY OR
        FITNESS FOR A PARTICULAR PURPOSE.
	</p>

	<h1>Acknowledgement</h1>

	<p class="copyright">
    	Funding for the RFC editor function is currently provided by the
        Internet Society.
   	</p>

</xsl:template>


<!-- insert CSS style info -->

<xsl:template name="insertCss">
A
{
	text-decoration: none
}
A:hover
{
	text-decoration: underline
}
A:active
{
	text-decoration: underline
}
BODY
{
	color: #000000;
  font-family: helvetica, arial, sans-serif;
  font-size: 13px;
}
H1
{
	color: #333333;
  font-size: 16px;
  line-height: 16px;
  font-family: helvetica, arial, sans-serif;
	page-break-after: avoid;
}
H2
{
	color: #000000;
  font-size: 14px;
  font-family: helvetica, arial, sans-serif;
	page-break-after: avoid;
}
H3
{
	color: #000000;
  font-size: 13px;
  font-family: helvetica, arial, sans-serif;
	page-break-after: avoid;
}
P
{
	margin-left: 2em;
  margin-right: 2em;
}
PRE
{
	margin-left: 3em;
  color: #333333
}
TABLE
{
	font-size: 13px
}
TD.header
{
	color: #ffffff;
  font-size: 10px;
  font-family: arial, helvetica, sans-serif;
  valign: top
}
.copyright
{
	font-size: 10px
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

<xsl:template name="insertIndex">

	<!-- insert link to TOC including horizontal rule -->
	<xsl:call-template name="insertTocLink">
		<xsl:with-param name="rule" select="true()" />
	</xsl:call-template> 

	<a name="rfc.index">
    	<h1>Index</h1>
   	</a>

	<table>
    	<xsl:variable name="lcase" select="'abcdefghijklmnopqrstuvwxyz'" />
    	<xsl:variable name="ucase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'" />       
        
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
                    	&#0160;&#0160;
                       	<xsl:value-of select="@item" />&#0160;
                        <xsl:for-each select="key('index-item',@item)[not(@subitem) or @subitem='']">
							<xsl:sort select="translate(@item,$lcase,$ucase)" />
                			
                            <xsl:variable name="backlink">#rfc.iref.<xsl:number level="any" /></xsl:variable>
                			&#0160;<a href="{$backlink}"><xsl:call-template name="sectionnumber" /></a>
                            <xsl:if test="position()!=last()">,</xsl:if>
                        </xsl:for-each>
                    </td>
            	</tr>
                
                <xsl:for-each select="key('index-item',@item)[@subitem and @subitem!='']">
		        	<tr>
						<td>
        	            	&#0160;&#0160;&#0160;&#0160;
            	           	<xsl:value-of select="@subitem" />&#0160;
                	        <xsl:for-each select="key('index-item-subitem',concat(@item,'..',@subitem))">
								<xsl:sort select="translate(@item,$lcase,$ucase)" />
                			
                           	 <xsl:variable name="backlink">#rfc.iref.<xsl:number level="any" /></xsl:variable>
                				&#0160;<a href="{$backlink}"><xsl:call-template name="sectionnumber" /></a>
                            	<xsl:if test="position()!=last()">,</xsl:if>
                        	</xsl:for-each>
                		</td>
        			</tr>
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
        <xsl:otherwise>(category missing or unknown)</xsl:otherwise>
	</xsl:choose>
</xsl:template>



<xsl:template name="insertStatus">

    <h1>Status of this Memo</h1>

	<xsl:choose>
    	<xsl:when test="/rfc/@ipr">
			<p>
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
					<xsl:otherwise>CONFORMANCE UNDEFINED</xsl:otherwise>
				</xsl:choose>

				Internet-Drafts are working documents of the Internet Engineering
				Task Force (IETF), its areas, and its working groups.
				Note that other groups may also distribute working documents as
				Internet-Drafts.
				Internet-Drafts are draft documents valid for a maximum of six months
				and may be updated, replaced, or obsoleted by other documents at any time.
				It is inappropriate to use Internet-Drafts as reference material or to cite
				them other than as "work in progress".
			</p>
			<p>
				The list of current Internet-Drafts can be accessed at
				<a href='http://www.ietf.org/ietf/1id-abstracts.txt'>http://www.ietf.org/ietf/1id-abstracts.txt</a>.
			</p>
			<p>
				The list of Internet-Draft Shadow Directories can be accessed at
				<a href='http://www.ietf.org/shadow.html'>http://www.ietf.org/shadow.html</a>.
			</p>
			<p>
				This Internet-Draft will expire on <xsl:call-template name="expirydate" />.
			</p>
      	</xsl:when>

		<xsl:when test="/rfc/@category='bcp'">
			<p>
            	This document specifies an Internet Best Current Practice for the Internet
				Community, and requests discussion and suggestions for improvements.
				Distribution of this memo is unlimited.
           	</p>
      	</xsl:when>
		<xsl:when test="/rfc/@category='exp'">
			<p>
            	This memo defines an Experimental Protocol for the Internet community.
				It does not specify an Internet standard of any kind.
				Discussion and suggestions for improvement are requested.
				Distribution of this memo is unlimited.
           	</p>
    	</xsl:when>
		<xsl:when test="/rfc/@category='historic'">
			<p>
            	This memo describes a historic protocol for the Internet community.
				It does not specify an Internet standard of any kind.
				Distribution of this memo is unlimited.
         	</p>
      	</xsl:when>
		<xsl:when test="/rfc/@category='info'">
			<p>
            	This memo provides information for the Internet community.
				It does not specify an Internet standard of any kind.	
				Distribution of this memo is unlimited.
            </p>
      	</xsl:when>
		<xsl:when test="/rfc/@category='std'">
			<p>
            	This document specifies an Internet standards track protocol for the Internet
				community, and requests discussion and suggestions for improvements.
				Please refer to the current edition of the &quot;Internet Official Protocol
				Standards&quot; (STD 1) for the standardization state and status of this	
				protocol. Distribution of this memo is unlimited.
          	</p>
      	</xsl:when>
		<xsl:otherwise>
			<p>UNSUPPORTED CATEGORY.</p>
		</xsl:otherwise>
    </xsl:choose>

</xsl:template>

<xsl:template name="insertToc">

	<xsl:call-template name="insertTocLink">
		<xsl:with-param name="includeTitle" select="true()" />
   	 <xsl:with-param name="rule" select="true()" />
	</xsl:call-template>

	<a name="rfc.toc">
    	<h1>Table of Contents</h1>
   	</a>

	<ul compact="compact" class="toc">
		<xsl:for-each select="//section|//references">
			
            <xsl:variable name="sectionNumber">
        		<xsl:call-template name="sectionnumber" />
      		</xsl:variable>
			
          <xsl:variable name="target">
        		<xsl:choose>
              <xsl:when test="self::references and not(@title)">rfc.references</xsl:when>
              <xsl:when test="self::references and @title">rfc.references.<xsl:value-of select="@title"/></xsl:when>
  	        	<xsl:when test="@anchor"><xsl:value-of select="@anchor" /></xsl:when>
    	        <xsl:otherwise>rfc.section.<xsl:value-of select="$sectionNumber" /></xsl:otherwise>
        		</xsl:choose>
        	</xsl:variable>
			
            <xsl:variable name="number">
        		<xsl:choose>
            		<xsl:when test="name()='references'">&#167;</xsl:when>
					<xsl:otherwise>
                		<xsl:call-template name="sectionnumber" />
                	</xsl:otherwise>
        		</xsl:choose>
        	</xsl:variable>
		
        	<xsl:variable name="title">
        		<xsl:choose>
            		<xsl:when test="self::references and not(@title)">References</xsl:when>
    	        	<xsl:otherwise><xsl:value-of select="@title" /></xsl:otherwise>
        		</xsl:choose>
        	</xsl:variable>
		
        	<b>
        		<a href="#{$target}"><xsl:value-of select="$number" /></a>&#0160;
        		<xsl:value-of select="$title"/>
       		</b>
        	<br />
		</xsl:for-each>
	
    	<b>
       		<a href="#rfc.authors">&#167;</a>&#0160;Author's Address
  		</b>
		<br />
		<xsl:if test="//iref">
	    	<b>
    	   		<a href="#rfc.index">&#167;</a>&#0160;Index
  			</b>
			<br />
       	</xsl:if>
		<b>
       		<a href="#rfc.copyright">&#167;</a>&#0160;Full Copyright Statement
  		</b>
		<br />
	</ul>
  
  <!-- experimental -->
  <xsl:if test="//processing-instruction('rfc-issue')">
    <xsl:call-template name="insertIssuesList" />
  </xsl:if>

</xsl:template>

<xsl:template name="insertTocLink">
	<xsl:param name="includeTitle" select="false()" />
	<xsl:param name="rule" />
	<xsl:if test="$rule"><hr class="noprint" size="1" shade="0" /></xsl:if>
	<table class="noprint" border="0" cellpadding="0" cellspacing="2" width="30" height="15" align="right">
    	<xsl:if test="$includeTitle"><tr>
        	<td bgcolor="#000000" align="center" valign="center" width="30" height="30">
       			<b><span class="RFC">&#0160;RFC&#0160;</span></b><br />
           		<span class="hotText"><xsl:value-of select="/rfc/@number"/></span>
        	</td>
    	</tr></xsl:if>
		<xsl:if test="$includeToc='yes'">
    	<tr>
        	<td bgcolor="#990000" align="center" width="30" height="15">
           		<a href="#rfc.toc" CLASS="link2"><b class="link2">&#0160;TOC&#0160;</b></a>
			</td>
        </tr>
        </xsl:if>
	</table>	
</xsl:template>


<xsl:template name="referencename">
	<xsl:param name="node" />
	<xsl:choose>
    	<xsl:when test="$useSymrefs='yes'">[<xsl:value-of select="$node/@anchor" />]</xsl:when>
    	<xsl:otherwise><xsl:for-each select="$node">[<xsl:number />]</xsl:for-each></xsl:otherwise>
  	</xsl:choose>
</xsl:template>



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


<xsl:template name="sectionnumber">
	<xsl:choose>
       	<xsl:when test="ancestor::back"><xsl:number count="section" level="multiple" format="A.1.1.1.1.1.1.1" /></xsl:when>
       	<xsl:otherwise><xsl:number count="section" level="multiple"/></xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template name="sectionnumberPara">
	<!-- get section number of ancestor section element, then add t or figure number -->
	<xsl:if test="ancestor::section">
    	<xsl:for-each select="ancestor::section[1]"><xsl:call-template name="sectionnumber" />.p.</xsl:for-each><xsl:number count="t|figure" />
  	</xsl:if>
</xsl:template>

<!-- experimental annotation support -->

<xsl:template name="getToken">
  <xsl:param name="text" />
  <xsl:param name="index" />
  <xsl:choose>
    <xsl:when test="$index = 0">
      <xsl:value-of select="substring-before(normalize-space($text),' ')" />
    </xsl:when>
    <xsl:otherwise>
      <xsl:call-template name="getToken">
        <xsl:with-param name="text" select="substring-after(normalize-space($text),' ')" />
        <xsl:with-param name="index" select="$index - 1" />
      </xsl:call-template>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template name="getTokenFrom">
  <xsl:param name="text" />
  <xsl:param name="index" />
  <xsl:choose>
    <xsl:when test="$index = 0">
      <xsl:value-of select="$text" />
    </xsl:when>
    <xsl:otherwise>
      <xsl:call-template name="getTokenFrom">
        <xsl:with-param name="text" select="substring-after(normalize-space($text),' ')" />
        <xsl:with-param name="index" select="$index - 1" />
      </xsl:call-template>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="processing-instruction('rfc-issue')">
  <xsl:variable name="name"><xsl:call-template name="getToken">
    <xsl:with-param name="index" select="0" />
    <xsl:with-param name="text" select="." />
  </xsl:call-template></xsl:variable>
  <xsl:variable name="type"><xsl:call-template name="getToken">
    <xsl:with-param name="index" select="1" />
    <xsl:with-param name="text" select="." />
  </xsl:call-template></xsl:variable>
  <xsl:variable name="date"><xsl:call-template name="getToken">
    <xsl:with-param name="index" select="2" />
    <xsl:with-param name="text" select="." />
  </xsl:call-template></xsl:variable>
  <xsl:variable name="who"><xsl:call-template name="getToken">
    <xsl:with-param name="index" select="3" />
    <xsl:with-param name="text" select="." />
  </xsl:call-template></xsl:variable>
  <xsl:variable name="text"><xsl:call-template name="getTokenFrom">
    <xsl:with-param name="index" select="4" />
    <xsl:with-param name="text" select="." />
  </xsl:call-template></xsl:variable>

  <a name="rfc.issue.{$name}">
  <table style="background-color: khaki; border-width: thin; border-style: solid; border-color: black;" align="right" width="50%">
    <tr>
      <td>[<xsl:value-of select="$name" />], <a href="mailto:{$who}?subject={/rfc/@docName}, {$name}"><i><xsl:value-of select="$who" /></i></a>, <xsl:value-of select="$date" /></td>
    </tr>
    <tr>
      <td><xsl:value-of select="$text" /></td>
    </tr>
  </table>
  </a>
    
</xsl:template>

<xsl:template name="insertIssuesList">

  <h2>Issues list</h2>
  <p>
  <table>
    <xsl:for-each select="//processing-instruction('rfc-issue')">
  <xsl:variable name="name"><xsl:call-template name="getToken">
    <xsl:with-param name="index" select="0" />
    <xsl:with-param name="text" select="." />
  </xsl:call-template></xsl:variable>
  <xsl:variable name="type"><xsl:call-template name="getToken">
    <xsl:with-param name="index" select="1" />
    <xsl:with-param name="text" select="." />
  </xsl:call-template></xsl:variable>
  <xsl:variable name="date"><xsl:call-template name="getToken">
    <xsl:with-param name="index" select="2" />
    <xsl:with-param name="text" select="." />
  </xsl:call-template></xsl:variable>
  <xsl:variable name="who"><xsl:call-template name="getToken">
    <xsl:with-param name="index" select="3" />
    <xsl:with-param name="text" select="." />
  </xsl:call-template></xsl:variable>
  <xsl:variable name="text"><xsl:call-template name="getTokenFrom">
    <xsl:with-param name="index" select="4" />
    <xsl:with-param name="text" select="." />
  </xsl:call-template></xsl:variable>
      <tr>
        <td><a href="#rfc.issue.{$name}"><xsl:value-of select="$name" /></a></td>
        <td><xsl:value-of select="$type" /></td>
        <td><xsl:value-of select="$date" /></td>
        <td><a href="mailto:{$who}?subject={/rfc/@docName}, {$name}"><xsl:value-of select="$who" /></a></td>
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


</xsl:stylesheet>
