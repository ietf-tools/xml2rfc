
SAMPLES=svg-samples
CHECKS=svg-samples-check
OUT=svg-samples-out

all: tests

tests: test1 test2
test1:
	@ echo Test 1
	rm -rf $(OUT); mkdir $(OUT)
	./check-svg.py -O $(OUT) $(SAMPLES)/*.svg
	diff -r $(CHECKS) $(OUT)
test2:
	@ echo Test 2
	rm -rf $(OUT); mkdir $(OUT)
	for i in $(SAMPLES)/*.svg;do \
		./check-svg.py -o $(OUT)/`basename $$i` $$i; \
	done
	diff -r $(CHECKS) $(OUT)

clean:
	rm -rf __pycache__ $(OUT) *.pyc *~

DIR=etc
PUB= $$HOME/public_html/$(DIR)
INS= check-svg.py word_properties.py
WEB=/home/www/tools.ietf.org/tools/xml2rfc/$(DIR)

install: all install_only

install_only:
	@for i in $(INS); do \
	    if [ $$i -nt $(WEB)/$$i ];then \
	        echo cp $$i $(WEB)/$$i; \
	        cp $$i $(WEB)/$$i; \
	    fi; \
	done

diff-install: all
	@for i in $(INS); do \
	        echo diff $$i $(WEB)/$$i; \
	        diff $$i $(WEB)/$$i; \
	done

test-install: all
	@for i in $(INS); do \
	    if [ $$i -nt $(PUB)/$$i ];then \
	        echo cp $$i $(PUB)/$$i; \
	        cp $$i $(PUB)/$$i; \
	    fi; \
	done

