BIBXML Processing

This directory contains a complete rewrite of the bibxml processing.

The primary entry point it gen-bibxml-all.

It invokes in turn the various bibxml generators via their gen-bibxml-xyz-all
   Each generator creates
   	the reference...xml files in the appropriate bibxml-xyz directory
	the rdf/item...rdf files in the appropriate bibxml-xyz directory
	the tarball and zipfiles

The script bibxml_common/generate-tarball-zipfile is used by several of the
generators for creating the tarball and zipfiles.


