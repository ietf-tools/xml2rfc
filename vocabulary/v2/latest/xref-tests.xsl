<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0">
  <xsl:output method="xml" doctype-system="rfc2629.dtd" exclude-result-prefixes="xsl" indent="yes"/>
  <xsl:variable name="format" select="('', 'counter', 'title', 'none', 'default')"/>
  <xsl:variable name="pageno" select="('', 'true', 'false')"/>
  <xsl:variable name="target" select="('section-anchor', 'reference-anchor')"/>  
  <xsl:template match="/">
    <rfc ipr="trust200902" docName="xref-tests" category="std" xml:lang="en">
      <front>
        <title abbrev="xref">xref Test Cases</title>
        <author initials="E." surname="Wilde" fullname="Erik Wilde">
          <organization>UC Berkeley</organization>
          <address>
            <email>dret@berkeley.edu</email>
            <uri>http://dret.net/netdret/</uri>
         </address>
        </author>
        <date year="2014"/>
        <abstract>
          <t>Some xref test cases.</t>
        </abstract>
      </front>
      <middle>
        <section title="Tests">
          <xsl:for-each select="$format">
            <xsl:variable name="formatval" select="."/>
            <xsl:for-each select="$pageno">
              <xsl:variable name="pagenoval" select="."/>
              <xsl:for-each select="$target">
                <xsl:variable name="targetval" select="."/>
                <t>
                  <xsl:text>&lt;xref</xsl:text>
                    <xsl:if test="$formatval ne ''">
                      <xsl:text> format="</xsl:text>
                      <xsl:value-of select="$formatval"/>
                      <xsl:text>"</xsl:text>
                    </xsl:if>
                    <xsl:if test="$pagenoval ne ''">
                      <xsl:text> pageno="</xsl:text>
                      <xsl:value-of select="$pagenoval"/>
                      <xsl:text>"</xsl:text>
                    </xsl:if>
                    <xsl:if test="$targetval ne ''">
                      <xsl:text> target="</xsl:text>
                      <xsl:value-of select="$targetval"/>
                      <xsl:text>"</xsl:text>
                    </xsl:if>
                  <xsl:text>/>: </xsl:text>
                  <xref>
                    <xsl:if test="$formatval ne ''">
                      <xsl:attribute name="format" select="$formatval"/>
                    </xsl:if>
                    <xsl:if test="$pagenoval ne ''">
                      <xsl:attribute name="pageno" select="$pagenoval"/>
                    </xsl:if>
                    <xsl:if test="$targetval ne ''">
                      <xsl:attribute name="target" select="$targetval"/>
                    </xsl:if>
                  </xref>
                </t>
              </xsl:for-each>
            </xsl:for-each>
          </xsl:for-each>
        </section>
        <section title="Test Target" anchor="section-anchor">
          <t>Some text...</t>
        </section>
      </middle>
      <back>
        <references title="Normative References">
          <reference anchor="reference-anchor" target="http://www.w3.org/TR/2008/REC-xml-20081126/">
            <front>
              <title>Extensible Markup Language (XML) 1.0 (Fifth Edition)</title>
              <author fullname="Eve Maler" surname="Maler" initials="E."/>
              <author fullname="Francois Yergeau" surname="Yergeau" initials="F."/>
              <author fullname="Jean Paoli" surname="Paoli" initials="J."/>
              <author fullname="Michael Sperberg-McQueen" surname="Sperberg-McQueen" initials="M."/>
              <author fullname="Tim Bray" surname="Bray" initials="T."/>
              <date year="2008" month="November" day="26"/>
            </front>
            <seriesInfo name="W3C Recommendation" value="REC-xml-20081126"/>
            <annotation> Latest version available at <eref target="http://www.w3.org/TR/xml"/>. </annotation>
          </reference>
        </references>
      </back>
    </rfc>
  </xsl:template>
</xsl:stylesheet>
