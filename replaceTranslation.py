#!/bin/python
# Replaces strings in RenPy translation file accroding to supplied translation table
import sys
import os

trTxts = {}

with open(sys.argv[1], 'r') as f:
	for line in f:
		lComp = line.strip().split('\t')
		if (len(lComp)<2):
			continue
		try:
			trTxts[lComp[1]] = lComp[2]
		except:
			trTxts[lComp[1]] = ""
	f.close()

with open(sys.argv[2], 'r') as inF:
	with open(sys.argv[2]+"_tmp", 'w') as outF:
		for line in inF:
			if ('#' in line):
				outF.write(line)
				continue
			for orig, tr in trTxts.items():
				line=line.replace(orig, tr.replace('"','\\"'))
			outF.write(line)
		outF.close()
	inF.close()

os.remove(sys.argv[2])
os.rename(sys.argv[2]+"_tmp", sys.argv[2])
