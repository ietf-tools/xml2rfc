#!/usr/bin/python3

# Make sure the parts are there
try:
	FullDraftText = open("draft-hoffman-rfcexamples-latest", mode="r")
except:
	exit("Weird: could not find 'draft-hoffman-rfcexamples-latest'. Exiting.")

try:
	FullV2ExampleText = open("example-full-v2.xml", mode="r")
except:
	exit("Weird: could not find 'example-full-v2.xml'. Exiting.")

FigWrapper = '''<figure>
<artwork>
<![CDATA[
]]>
</artwork>
</figure>
'''

