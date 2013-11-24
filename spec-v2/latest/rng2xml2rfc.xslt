<xsl:transform xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
               xmlns:rng="http://relaxng.org/ns/structure/1.0"
               xmlns:x="http://purl.org/net/xml2rfc/ext"
               xmlns:a="http://relaxng.org/ns/compatibility/annotations/1.0"
               version="1.0"
               exclude-result-prefixes="rng a"
>

<xsl:output encoding="UTF-8" indent="yes" omit-xml-declaration="yes" />

<xsl:strip-space elements="figure"/>

<xsl:template match="/">
  <xsl:apply-templates select="rng:grammar"/>
</xsl:template>

<xsl:variable name="spec" select="document('draft-reschke-xml2rfc-latest.xml')"/>

<xsl:template match="rng:grammar">
  <xsl:apply-templates select="rng:define/rng:element">
    <xsl:sort select="@name"/>
  </xsl:apply-templates>
</xsl:template>

<xsl:template match="rng:element">
<xsl:variable name="anchor" select="concat('element.',@name)"/>
<section title="&lt;{@name}&gt;" anchor="{$anchor}">
  <x:anchor-alias value="{@name}"/>
  <iref item="Elements" subitem="{@name}" primary="true"/>
  <iref item="{@name} element" primary="true"/>

  <xsl:variable name="attributecontents" select="descendant-or-self::rng:attribute"/>
  <xsl:variable name="elementcontents" select="*[not(descendant-or-self::rng:attribute) and not(self::rng:empty)]"/>

  <xsl:variable name="appearsin" select="//rng:element[.//rng:ref/@name=current()/@name]"/>

  <xsl:variable name="elemdoc" select="$spec/rfc/middle/section/section[@anchor=$anchor]/t[not(comment()='AG')] | $spec/rfc/middle/section/section[@anchor=$anchor]/figure | $spec/rfc/middle/section/section[@anchor=$anchor]/texttable"/>
  <xsl:if test="not($elemdoc)">
    <xsl:message>No prose for element: <xsl:value-of select="@name"/></xsl:message>
  </xsl:if>
  <xsl:apply-templates select="$elemdoc" mode="copy"/>
  
  <xsl:if test="$appearsin">
    <t>
      <xsl:comment>AG</xsl:comment>
      <xsl:text>This element appears as child element of: </xsl:text>
      <xsl:for-each select="$appearsin">
        <xsl:sort select="@name"/>
          <xsl:text>&lt;</xsl:text>
          <x:ref><xsl:value-of select="@name"/></x:ref>
          <xsl:text>&gt;</xsl:text> (<xref target="element.{@name}"/>)<xsl:if test="position() != last()">, </xsl:if>
          <xsl:if test="position() = last() -1">and </xsl:if>
      </xsl:for-each>
      <xsl:text>.</xsl:text>
    </t>
  </xsl:if>
  
  <xsl:if test="$elementcontents">
    <section title="Contents" toc="exclude" anchor="{$anchor}.contents">
      <xsl:choose>
        <xsl:when test="count($elementcontents)=1">
          <xsl:apply-templates select="$elementcontents"/>
        </xsl:when>
        <xsl:otherwise>
          <t>
            <list style="numbers">
              <xsl:apply-templates select="$elementcontents"/>
            </list>
          </t>
        </xsl:otherwise>
      </xsl:choose>
    </section>
  </xsl:if>  

  <xsl:if test="$attributecontents">
    <section title="Attributes" toc="exclude">
      <xsl:apply-templates select="$attributecontents">
        <xsl:sort select="concat(@name,*/@name)"/>
      </xsl:apply-templates>
    </section>
  </xsl:if>  

  <section title="Grammar" toc="exclude" anchor="{$anchor}.grammar">
    <t/>
    <figure><artwork type="application/relax-ng-compact-syntax">&#10;<xsl:apply-templates select="." mode="rnc"/></artwork></figure>
  </section>
  
</section>
</xsl:template>

<xsl:template match="rng:*">
  <t>
    <cref>
      Missing template for <xsl:value-of select="local-name(.)"/>.
    </cref>
  </t>
</xsl:template>

<xsl:template match="rng:oneOrMore[rng:ref]">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="rng:optional[rng:attribute]">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="rng:optional[rng:ref]">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="rng:attribute">
  <xsl:variable name="elem" select="ancestor::rng:element"/>
  <xsl:variable name="anchor" select="concat('element.',$elem/@name,'.attribute.',translate(@name,':','-'))"/>
  
  <section title="{@name}" anchor="{$anchor}" toc="exclude">
    <iref item="Attributes" subitem="{@name}"/>
    <iref item="{$elem/@name} element" subitem="{@name} attribute"/>
    <iref item="{@name} attribute" subitem="in {$elem/@name} element"/>
    <t>
      <xsl:comment>AG</xsl:comment>
      <xsl:choose>
        <xsl:when test="parent::rng:optional">(optional)</xsl:when>
        <xsl:otherwise>(mandatory)</xsl:otherwise>
      </xsl:choose>
    </t>
    <xsl:apply-templates select="$spec/rfc/middle/section/section/section/section[@anchor=$anchor]/t[not(comment()='AG')]" mode="copy"/>
    <xsl:if test="rng:choice">
      <t>
        <xsl:comment>AG</xsl:comment>
        <xsl:text>Allowed values: </xsl:text>
        <list style="symbols">
          <xsl:for-each select="rng:choice/rng:value">
            <t>
              <xsl:text>"</xsl:text>
              <xsl:value-of select="."/>
              <xsl:text>"</xsl:text>
              <xsl:if test=". = ../../@a:defaultValue"> (default)</xsl:if>
            </t>
          </xsl:for-each>
        </list>
      </t>
    </xsl:if>    
  </section>
</xsl:template>

<xsl:template match="rng:ref">
  <t>
    <xsl:comment>AG</xsl:comment>
    <xsl:variable name="elem" select="//rng:define[@name=current()/@name]/rng:element/@name"/>
    <iref item="Elements" subitem="{$elem}"/>
    <xsl:variable name="container" select="ancestor::rng:element[1]"/>
    <iref item="{$elem} element" subitem="inside {$container/@name}"/>
    <xsl:choose>
      <xsl:when test="parent::rng:oneOrMore">One or more </xsl:when>
      <xsl:when test="parent::rng:zeroOrMore">Optional </xsl:when>
      <xsl:when test="parent::rng:optional">One optional </xsl:when>
      <xsl:when test="parent::rng:choice"></xsl:when>
      <xsl:otherwise>One </xsl:otherwise>
    </xsl:choose>
    <xsl:text>&lt;</xsl:text>
    <x:ref><xsl:value-of select="$elem"/></x:ref>
    <xsl:text>&gt; element</xsl:text>
    <xsl:if test="parent::rng:zeroOrMore or parent::rng:oneOrMore or parent::rng:choice">s</xsl:if><xsl:text> (</xsl:text><xref target="element.{$elem}"/><xsl:text>)</xsl:text>
  </t>
</xsl:template>

<xsl:template match="rng:ref[@name='TEXT' or @name='CTEXT']">
  <t>
    <xsl:comment>AG</xsl:comment>
    <xsl:text>Text</xsl:text>
  </t>
</xsl:template>

<xsl:template match="rng:zeroOrMore[rng:ref]">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="rng:zeroOrMore[rng:choice]">
<t>
  <xsl:comment>AG</xsl:comment>
  <xsl:text>In any order: </xsl:text>
  <list style="symbols">
    <xsl:apply-templates select="rng:choice/*"/>
  </list>
</t>
</xsl:template>

<xsl:template match="*" mode="copy">
  <xsl:element name="{local-name()}">
    <xsl:copy-of select="@*"/>
    <xsl:apply-templates select="node()" mode="copy"/>
  </xsl:element>
</xsl:template>

<xsl:template match="text()" mode="copy">
  <xsl:choose>
    <xsl:when test="normalize-space()=''">
      <!-- eat the node -->
    </xsl:when>
    <xsl:otherwise>
      <xsl:copy />
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<!-- experimental RNC conversion -->
<xsl:template match="*" mode="rnc">
  <xsl:message>Missing mode=rfc template for <xsl:value-of select="local-name()"/></xsl:message>
</xsl:template>

<xsl:template match="rng:element" mode="rnc">
  <xsl:call-template name="escape-name"/>
  <xsl:text> =&#10;</xsl:text>
  <xsl:text>  element </xsl:text>
  <xsl:call-template name="escape-name"/>
  <xsl:text> {&#10;</xsl:text>
  <xsl:for-each select="*">
    <xsl:text>    </xsl:text>
    <xsl:apply-templates select="." mode="rnc">
      <xsl:with-param name="indent" select="'    '"/>
    </xsl:apply-templates>
    <xsl:if test="position()!=last()">
      <xsl:text>,</xsl:text>
    </xsl:if>
    <xsl:text>&#10;</xsl:text>
  </xsl:for-each>
  <xsl:text>  }&#10;</xsl:text>
</xsl:template>

<xsl:template match="rng:oneOrMore" mode="rnc">
  <xsl:param name="indent"/>
  <xsl:apply-templates select="*" mode="rnc">
    <xsl:with-param name="indent" select="$indent"/>
  </xsl:apply-templates>
  <xsl:text>+</xsl:text>
</xsl:template>

<xsl:template match="rng:zeroOrMore" mode="rnc">
  <xsl:param name="indent"/>
  <xsl:apply-templates select="*" mode="rnc">
    <xsl:with-param name="indent" select="$indent"/>
  </xsl:apply-templates>
  <xsl:text>*</xsl:text>
</xsl:template>

<xsl:template match="rng:optional" mode="rnc">
  <xsl:param name="indent"/>
  <xsl:apply-templates select="*" mode="rnc">
    <xsl:with-param name="indent" select="$indent"/>
  </xsl:apply-templates>
  <xsl:text>?</xsl:text>
</xsl:template>

<xsl:template match="rng:choice" mode="rnc">
  <xsl:param name="indent"/>
  <xsl:text>(</xsl:text>
  <xsl:for-each select="*">
    <xsl:apply-templates select="." mode="rnc">
      <xsl:with-param name="indent" select="$indent"/>
    </xsl:apply-templates>
    <xsl:if test="position()!=last()">
      <xsl:text>&#10;</xsl:text>
      <xsl:value-of select="$indent"/>
      <xsl:text> | </xsl:text>
    </xsl:if>
  </xsl:for-each>
  <xsl:text>)</xsl:text>
</xsl:template>

<xsl:template match="rng:attribute/rng:choice" mode="rnc">
  <xsl:param name="indent"/>
  <xsl:variable name="content" select="normalize-space(.)"/>
  <xsl:comment>
    <xsl:value-of select="string-length($content)"/>
  </xsl:comment>
  <xsl:choose>
    <xsl:when test="count(*)=1">
      <xsl:text> { </xsl:text>
      <xsl:apply-templates select="*" mode="rnc">
        <xsl:with-param name="indent" select="$indent"/>
      </xsl:apply-templates>
      <xsl:text> }</xsl:text>
    </xsl:when>
    <xsl:when test="string-length($content) > 40">
      <xsl:text> (</xsl:text>
      <xsl:for-each select="*">
        <xsl:text>&#10;</xsl:text>
        <xsl:text>  </xsl:text>
        <xsl:value-of select="$indent"/>
        <xsl:if test="position()!=1">
          <xsl:text>| </xsl:text>
        </xsl:if>
        <xsl:apply-templates select="." mode="rnc">
          <xsl:with-param name="indent" select="$indent"/>
        </xsl:apply-templates>
      </xsl:for-each>
      <xsl:text>&#10;</xsl:text>
      <xsl:value-of select="$indent"/>
      <xsl:text>)</xsl:text>
    </xsl:when>
    <xsl:otherwise>
      <xsl:text> ( </xsl:text>
      <xsl:for-each select="*">
        <xsl:apply-templates select="." mode="rnc">
          <xsl:with-param name="indent" select="$indent"/>
        </xsl:apply-templates>
        <xsl:if test="position()!=last()">
          <xsl:text> | </xsl:text>
        </xsl:if>
      </xsl:for-each>
      <xsl:text> )</xsl:text>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="rng:value" mode="rnc">
  <xsl:text>"</xsl:text>
  <!-- escaping? -->
  <xsl:value-of select="."/>
  <xsl:text>"</xsl:text>
</xsl:template>

<xsl:template match="rng:data[@type='IDREF']" mode="rnc">
  <xsl:text> { xsd:IDREF }</xsl:text>
</xsl:template>

<xsl:template match="rng:data[@type='ID']" mode="rnc">
  <xsl:text> { xsd:ID }</xsl:text>
</xsl:template>

<xsl:template match="rng:attribute" mode="rnc">
  <xsl:param name="indent"/>
  <xsl:text>attribute </xsl:text>
  <xsl:call-template name="escape-name"/>
  <xsl:apply-templates select="*" mode="rnc">
    <xsl:with-param name="indent" select="$indent"/>
  </xsl:apply-templates>
</xsl:template>

<xsl:template match="rng:attribute/rng:ref" mode="rnc">
  <xsl:text> { </xsl:text>
  <xsl:call-template name="escape-name"/>
  <xsl:text> }</xsl:text>
</xsl:template>

<xsl:template match="rng:ref" mode="rnc">
  <xsl:call-template name="escape-name-xref"/>
</xsl:template>

<xsl:template match="rng:empty" mode="rnc">
  <xsl:text>empty</xsl:text>
</xsl:template>

<xsl:template name="escape-name-xref">
  <xsl:if test="@name='list'">
    <xsl:text>\</xsl:text>
  </xsl:if>
  <xsl:choose>
    <xsl:when test="@name='TEXT' or @name='CTEXT'">
      <xsl:value-of select="@name"/>
    </xsl:when>
    <xsl:otherwise>
      <xref target="element.{@name}.grammar" format="none"><xsl:value-of select="@name"/></xref>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template name="escape-name">
  <xsl:if test="@name='list'">
    <xsl:text>\</xsl:text>
  </xsl:if>
  <xsl:value-of select="@name"/>
</xsl:template>

</xsl:transform>