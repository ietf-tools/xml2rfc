xml2rfc.all: \
	draft-iab-xml2rfcv2-latest.xml xml2rfcv2-annotated.rng

xml2rfcv1.rnc: xml2rfcv1.dtd trang.jar
	java -jar trang.jar -i inline-attlist $< $@

xml2rfcv2.rnc: xml2rfcv2.dtd trang.jar
	java -jar trang.jar -i inline-attlist $< $@

xml2rfcv2.rng: xml2rfcv2.dtd trang.jar
	java -jar trang.jar -i inline-attlist $< $@

xml2rfcv2-annotated.rng: xml2rfcv2.rng annotate-rng.xslt draft-iab-xml2rfcv2-latest.xml
	saxon $< annotate-rng.xslt doc=draft-iab-xml2rfcv2-latest.xml > $@

xml2rfcv2-spec.xml: xml2rfcv2.rng rng2xml2rfc.xslt
	saxon $< rng2xml2rfc.xslt voc=v3 > $@

xml2rfcv2.rnc.folded: xml2rfcv2.rnc
	./fold-rnc.sh $< > $@

draft-iab-xml2rfcv2-latest.xml: xml2rfcv2-spec.xml xml2rfcv2.rnc.folded
	cp -v $@ $@.bak
	./refresh-inclusions.sh $@

trang.jar:	trang-20091111.zip
	unzip -j trang-20091111.zip trang-20091111/trang.jar

trang-20091111.zip:
	wget http://jing-trang.googlecode.com/files/trang-20091111.zip || \
	curl -o trang-20091111.zip http://jing-trang.googlecode.com/files/trang-20091111.zip
