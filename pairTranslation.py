#!/bin/python
# Should be used after translations is extracted from original VN script to dialogue.tab and translated to translated.tab file
outFile = open("translate_pair.csv", 'w')

origTexts={}
origNames={}

trTexts={}
trNames={}

my_idx = 0

with open("translate_names.csv", 'r') as f:
	for line in f:
		lComp = line.split('\t')
		trNames[lComp[1]] = lComp[2].strip()
	f.close()

print(trNames)

with open("translated.tab", 'r') as f:
	for line in f:
		lComp = line.split('\t')
		if (len(lComp[0])==0):
			print(line)
			lComp[0] = "script_my_idx_"+str(my_idx)
			my_idx += 1
		trTexts[lComp[0]] = lComp[1]
	f.close()

my_idx = 0

with open("dialogue.tab", 'r') as f:
	for line in f:
		lComp = line.split('\t')
		if (len(lComp[0])==0):
			print(line)
			lComp[0] = "script_my_idx_"+str(my_idx)
			my_idx += 1
		origTexts[lComp[0]] = lComp[2]
		origNames[lComp[0]] = lComp[1]
	f.close()

for h, text in origTexts.items():
	outFile.write(h)
	outFile.write('\t')
	outFile.write(text.strip())
	outFile.write('\t')
	try:
		outFile.write(trTexts[h].strip())
	except:
		pass
	outFile.write('\t')
	try:
		outFile.write(trNames[origNames[h].strip()].strip())
	except:
		pass

	outFile.write('\n')

outFile.close()
