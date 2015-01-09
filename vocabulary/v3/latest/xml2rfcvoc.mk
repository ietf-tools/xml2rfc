xml2rfc.all: \
	draft-hoffman-xml2rfc-latest.xml xml2rfcv3-annotated.rng

xml2rfcv3.rnc: xml2rfcv3.rng
	java -jar ../../tools/trang.jar -o lineLength=69 $< $@

#xml2rfcv3.dtd: xml2rfcv3.rng
#	java -jar ../../tools/trang.jar $< $@

xml2rfcv3-annotated.rng: xml2rfcv3.rng annotate-rng.xslt draft-hoffman-xml2rfc-latest.xml
	saxon $< annotate-rng.xslt doc=draft-hoffman-xml2rfc-latest.xml > $@

xml2rfcv3-spec.xml: xml2rfcv3.rng rng2xml2rfc.xslt
	saxon $< rng2xml2rfc.xslt voc=v3 specsrc=draft-hoffman-xml2rfc-latest.xml > $@

xml2rfcv3-spec-deprecated.xml: xml2rfcv3.rng rng2xml2rfc.xslt
	saxon $< rng2xml2rfc.xslt specsrc=draft-hoffman-xml2rfc-latest.xml deprecated=yes > $@

xml2rfcv3.rnc.folded: xml2rfcv3.rnc
	./fold-rnc.sh $< > $@

draft-hoffman-xml2rfc-latest.xml: xml2rfcv3-spec.xml xml2rfcv3-spec-deprecated.xml xml2rfcv3.rnc.folded differences-from-v2.txt
	cp -v $@ $@.bak
	./refresh-inclusions.sh $@

xml2rfcv2 = xml2rfcv2.rnc

differences-from-v2.txt:	xml2rfcv3.rnc $(xml2rfcv2)
	fold -w66 -s $(xml2rfcv2) > $@.v2
	fold -w66 -s $<  > $@.v3
	diff -w --old-line-format='- %L' --new-line-format='+ %L' \
	--unchanged-line-format='  %L' -d $@.v2 $@.v3 \
	| sed "s/\&/\&amp;/g" > $@
	rm -f $@.v2 $@.v3


	
