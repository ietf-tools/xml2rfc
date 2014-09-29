#!/usr/bin/python3
import subprocess

DraftInputFile = "draft-hoffman-rfcexamples-input.xml"
DraftOutputFile = "draft-hoffman-rfcexamples-latest.xml"
ExampleFullV2File = "example-full-v2.xml"
V2FullMarker = "<!-- INSERTV2FULL-->"

# Make sure the parts are there
try:
	FullDraftText = open(DraftInputFile, mode="r").read()
except:
	exit("Could not find '{}'. Exiting.".format(DraftInputFile))
try:
	FullV2ExampleText = open(ExampleFullV2File, mode="r").read()
except:
	exit("Could not find '{}'. Exiting.".format(ExampleFullV2File))

# Escaping is hard, let's go shopping
def EscapedFigure(InText):
	OutText = InText.replace("&", "&amp;")
	OutText = OutText.replace("<", "&lt;")
	FigStart = "<figure><artwork>"
	FigEnd = "</artwork></figure>"
	return(FigStart + OutText + FigEnd)

# Replace the v2 full comment with the escaped replacement
if not  (V2FullMarker in FullDraftText):
	exit("Could not find '{}' in the draft input. Exiting.".format(V2FullMarker))
FullDraftText = FullDraftText.replace(V2FullMarker, EscapedFigure(FullV2ExampleText))

# Write out the coverted stuff
OutF = open(DraftOutputFile, mode="w")
OutF.write(FullDraftText)
OutF.close()

OutFileNameBase = DraftOutputFile[:-4]

# Prepare the .txt file; this possibly only works on Paul's machine
p = subprocess.Popen("xml2rfc {}.xml --filename={}.txt --text".format(OutFileNameBase, OutFileNameBase),
	stdout=subprocess.PIPE, shell=True)
p.wait()
TheOutput = (p.stdout.read()).decode("ascii")
print("Running xml2rfc said:\n{}".format(TheOutput))
