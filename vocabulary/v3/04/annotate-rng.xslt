<xsl:transform xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
               xmlns:a="http://relaxng.org/ns/compatibility/annotations/1.0"
               xmlns:rng="http://relaxng.org/ns/structure/1.0"
               xmlns="http://relaxng.org/ns/structure/1.0"
               version="1.0"
>

<xsl:strip-space elements="*"/>

<xsl:output encoding="UTF-8" indent="yes" />

<xsl:param name="doc"/>

<xsl:variable name="d" select="document($doc)"/>

<xsl:template match="rng:grammar">
  <grammar xmlns:a="http://relaxng.org/ns/compatibility/annotations/1.0">
    <xsl:apply-templates select="node()|@*" />
  </grammar>
</xsl:template>

<xsl:template match="rng:define/rng:element">
	<xsl:copy>
    <xsl:apply-templates select="@*" />
    <xsl:variable name="a" select="concat('element.',@name)"/>
    <xsl:variable name="section" select="$d//section[@anchor=$a]"/>
    <xsl:if test="$section">
      <xsl:variable name="t" select="$section/t[not(comment()='AG')]"/>
      <xsl:if test="$t">
        <a:annotation>
          <xsl:value-of select="normalize-space($t[1])"/>
        </a:annotation>
      </xsl:if>
    </xsl:if>
    <xsl:apply-templates select="node()" />
  </xsl:copy>
</xsl:template>


<!-- rules for identity transformation -->

<xsl:template match="node()|@*"><xsl:copy><xsl:apply-templates select="node()|@*" /></xsl:copy></xsl:template>

<xsl:template match="/">
	<xsl:copy><xsl:apply-templates select="node()" /></xsl:copy>
</xsl:template>

</xsl:transform>