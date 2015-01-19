#!/usr/bin/env python3
import os.path, subprocess

DraftInputFile = "draft-hoffman-rfcexamples-input.xml"
DraftOutputFile = "draft-hoffman-rfcexamples-latest.xml"
ExampleFullV2File = "example-full-v2.xml"
ExampleFullV3File = "example-full-v3.xml"
V2FullMarker = "<!-- INSERTV2FULL-->"
V3FullMarker = "<!-- INSERTV3FULL-->"
# The following might only work on Paul's machine
Xml2rfcBin = "/usr/local/bin/xml2rfc"

# Make sure the parts are there
try:
	FullDraftText = open(DraftInputFile, mode="r").read()
except:
	exit("Could not find '{0}'. Exiting.".format(DraftInputFile))
try:
	FullV2ExampleText = open(ExampleFullV2File, mode="r").read()
except:
	exit("Could not find '{0}'. Exiting.".format(ExampleFullV2File))

# Escaping is hard, let's go shopping
def EscapedFigure(InText):
	OutText = InText.replace("&", "&amp;")
	OutText = OutText.replace("<", "&lt;")
	FigStart = "<figure><artwork>"
	FigEnd = "</artwork></figure>"
	return(FigStart + OutText + FigEnd)

# Replace the v2 full comment with the escaped replacement
if not  (V2FullMarker in FullDraftText):
	exit("Could not find '{0}' in the draft input. Exiting.".format(V2FullMarker))
FullDraftText = FullDraftText.replace(V2FullMarker, EscapedFigure(FullV2ExampleText))

# Do the conversion from v2 to v3
p = subprocess.Popen("./convertv2v3.pl -C < {0} > {1}".format(ExampleFullV2File, ExampleFullV3File),
	stdout=subprocess.PIPE, shell=True)
p.wait()
TheOutput = (p.stdout.read()).decode("ascii")
print("Running convertv2v3.pl said:\n{0}".format(TheOutput))
try:
	FullV3ExampleText = open(ExampleFullV3File, mode="r").read()
except:
	exit("Could not find '{0}'. Exiting.".format(ExampleFullV3File))
# Get rid of superfluous blank lines
FullV3ExampleText = FullV3ExampleText.replace("\r\r\r", "\r\r")

# Replace the v3 full comment with the escaped replacement
if not  (V3FullMarker in FullDraftText):
	exit("Could not find '{0}' in the draft input. Exiting.".format(V3FullMarker))
FullDraftText = FullDraftText.replace(V3FullMarker, EscapedFigure(FullV3ExampleText))

# Write out the coverted stuff
OutF = open(DraftOutputFile, mode="w")
OutF.write(FullDraftText)
OutF.close()

OutFileNameBase = DraftOutputFile[:-4]

# Prepare the .txt file
if not os.path.isfile(Xml2rfcBin):
	print("{0} does not exist, so the .txt file was NOT UPDATED.".format(Xml2rfcBin))
else:
	p = subprocess.Popen("{0} {1}.xml --filename={2}.txt --text".format(Xml2rfcBin, OutFileNameBase, OutFileNameBase),
		stdout=subprocess.PIPE, shell=True)
	p.wait()
	TheOutput = (p.stdout.read()).decode("ascii")
	print("Running xml2rfc said:\n{0}".format(TheOutput))

# Do the diff
ConvertedV2File = "/tmp/" + ExampleFullV2File
ConvertedV3File = "/tmp/" + ExampleFullV3File
try:
	OutConvV2File = open(ConvertedV2File, "w")
except:
	exit("Could not write to {0}. Exiting.".format(OutConvV2File))
try:
	OutConvV3File = open(ConvertedV3File, "w")
except:
	exit("Could not write to {0}. Exiting.".format(OutConvV3File))
def ConvForDiff(InText):
	return(InText.replace("'", '"').replace("\n\n\n", "\n\n"))
OutConvV2File.write(ConvForDiff(FullV2ExampleText))
OutConvV2File.close()
OutConvV3File.write(ConvForDiff(FullV3ExampleText))
OutConvV3File.close()
p = subprocess.Popen("diff {0} {1}".format(ConvertedV2File, ConvertedV3File),
	stdout=subprocess.PIPE, shell=True)
p.wait()
TheOutput = (p.stdout.read()).decode("ascii")
# No real need to print the diff any more.
# print("The diff said:\n{0}".format(TheOutput))
