#!/usr/bin/python
from __future__ import print_function
import sys

TheInText = sys.stdin.read()
TheOutText = TheInText.replace("&", "&amp;").replace("<", "&lt;")
sys.stdout.write(TheOutText)
