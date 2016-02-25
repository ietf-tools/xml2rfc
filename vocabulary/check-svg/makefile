
SAMPLES=svg-samples
CHECKS=svg-samples-check
OUT=svg-samples-out

tests:
	rm -rf $(OUT); mkdir $(OUT)
	./check-svg.py -O $(OUT) $(SAMPLES)/*.svg
	diff -r $(CHECKS) $(OUT)

clean:
	rm -rf __pycache__ $(OUT) *.pyc
