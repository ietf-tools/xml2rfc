#!/usr/bin/env python3

'''
Program to make full, real RNG from xml2rfcv3.rng
This entails:
	Add xml:lang and xml:base to every element except SVG
	Remove PIs that were only there for other tools
'''

try:
	InLines = open("xml2rfcv3.rng", mode="r").readlines()
except:
	exit("Was unable to read the lines out of xml2rfcv3.rng. Exiting.")

MoreAtts = """      <optional>
        <attribute name="xml:base"/>
      </optional>
      <optional>
        <attribute name="xml:lang"/>
      </optional>
"""

# Add the attributes to every element.
OutLines = []
for ThisLine in InLines:
	OutLines.append(ThisLine)
	if ThisLine.startswith("    <element name"):
		if not(ThisLine.startswith('<element name="svg"')):  # Don't add this to <svg>
			OutLines.append(MoreAtts)

# Remove the PIs
OutText = "".join(OutLines)
OutText = OutText.replace("<?hidden-in-prose?>", "").replace("<?deprecated?>", "")

try:
	OutF = open("xml2rfcv3-full.rng", mode="w")
except:
	exit("Could not open xml2rfcv3-full.rng for writing. Exiting.")
OutF.write(OutText)
OutF.close()



