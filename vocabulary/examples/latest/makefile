INPUTS= PrepareDraft.py convertv2v3.pl draft-hoffman-rfcexamples-input.xml example-full-v2.xml

draft-hoffman-rfcexamples-latest.txt: $(INPUTS)
	./PrepareDraft.py


testConvert: example-full-v2.xml
	./convertv2v3.pl -C < example-full-v2.xml > /tmp/example-full-v3.xml
