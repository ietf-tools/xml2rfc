# bibxml8
Index.cgi in this directory will auto-generate IANA references in bibxml format.

http://xml2rfc.ietf.org/public/rfc/bibxml-iana/reference.IANA.service-names-port-numbers

The suffix determines whether xml or kramdown is generated.

# curl http://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xml

# <?xml version='1.0' encoding='UTF-8'?>
# <?xml-stylesheet type="text/xsl" href="service-names-port-numbers.xsl"?>
# <?oxygen RNGSchema="service-names-port-numbers.rng" type="xml"?>
# <registry xmlns="http://www.iana.org/assignments" id="service-names-port-numbers">
#   <title>Service Name and Transport Protocol Port Number Registry</title>
#   <category>Service Names and Transport Protocol Port Numbers</category>
#   <updated>2016-12-14</updated>
#   <xref type="rfc" data="rfc6335"/>
#   <expert>TCP/UDP: Joe Touch; Eliot Lear, Allison Mankin, Markku Kojo, Kumiko Ono, Martin Stiemerling, 
# Lars Eggert, Alexey Melnikov, Wes Eddy, Alexander Zimmermann, Brian Trammell, and Jana Iyengar
# SCTP: Allison Mankin and Michael Tuexen
# DCCP: Eddie Kohler and Yoshifumi Nishida</expert>
#   <note>
# Service names and port numbers are used to distinguish between different
# services that run over transport protocols such as TCP, UDP, DCCP, and
# SCTP.
# 

