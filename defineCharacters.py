#!/bin/python
# Should be used to change charactor's names string literals to RenPy's aliases 
import sys

with open(sys.argv[1], 'r') as f:
	for line in f:
		lComp = line.split('\t')
		print("define {} = Character(_({}))".format(lComp[2].strip(), lComp[1]))
	f.close()
