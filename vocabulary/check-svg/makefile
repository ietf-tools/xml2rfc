
tests:
	rm -rf svg-samples-out; mkdir svg-samples-out
	./check-svg.py -O svg-samples-out svg-samples/*.svg
	diff -r svg-samples-check svg-samples-out
