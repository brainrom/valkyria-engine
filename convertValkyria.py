#!/bin/python
# Main VN script convertor
import re
import sys
import os

r_splitArgs = ",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)"
r_parseCommand = "^%*([a-zA-Z_]{1,})\((.{0,})\);(.{0,})$"
r_parseNameWindowText = "【([^】]{0,})】"
r_parseCPlabel = "☆(\d{4})"
r_parseJumpTag = "#(\d{1})"

speakerName = ""
effectArgs = []
identation = 0
cpLabel = ""
charactors = {}

charactors_names = []

def cmd_ChangeBackGround(args):
	print_out("scene back{} with Dissolve({})".format(args[0].rjust(4, '0'), args[1].strip()))
	return True

def cmd_SetBackGround(args):
	print_out("scene back{}".format(args[0].rjust(4, '0')))
	return True

def cmd_EraseNameWindow(args):
	global speakerName
	speakerName = ""
	return True

def cmd_SetNameWindow(args):
	global speakerName
	speakerName = charactors_names[int(args[0])]
	return True

def cmd_SetMessage(args):
	replicaText = args[0].strip();
	replicaText = replicaText.replace('/s', '')
	replicaText = replicaText.replace('/r', '\\n')
	if (len(speakerName)>0):
		print_out ("{} \"{}\" {}".format(speakerName, replicaText, applyEffect()))
	else:
		print_out ("\"{}\" {}".format(replicaText, applyEffect()))
	return True

def cmd_SetWait(args):
	if (len(args)==0):
		return False
	waitMs = int(args[0])
	if (len(args)==1 or int(args[1])==0):
		print_out("pause {}".format(str(waitMs/1000)))
	else:
		isSkipable = int(args[1])
		print_out("$ renpy.pause({}, hard={})".format(str(waitMs/1000), "True" if isSkipable==1 else "False"))
	return True

def cmd_setOmake(args):
	print_out("$ omake_flag{} = True".format(args[0]))
	return True

def cmd_StopBGM(args):
	print_out("stop music") #Maybe with fadeout?
	return True

def cmd_SetBGM(args):
	print_out("play music \"{}\"".format("bgm/bgm{}.ogg".format(args[0])))
	return True

def cmd_SetCVEx(args):
	print_out("voice \"{}\"".format("snd{}/data{}.ogg".format(args[1].rjust(2, '0'), args[0])))
	return True

def cmd_SetSE(args):
	print_out("play sound \"{}\"".format("sfx/sfx{}.ogg".format(args[0])))
	return True

def cmd_SetEffect(args):
	global effectArgs
	effectArgs = args.copy()
	return True

def cmd_LoadScript(args):
	print_out("jump script_scrp{}".format(args[0]))
	return True

def cmd_CP_Start(args):
	global cpLabel
	if (len(cpLabel)==0):
		return False
	print_out("label CP_Start_{}:".format(cpLabel), True)
	cpLabel = ""
	return True

def cmd_CP_End(args):
	print_out("$ renpy.end_replay()")
	return True

def cmd_ChangeCharactor(args):
	global charactors
	imgIdxStr = args[0]
	xOffset = int(args[1]);
	showTime_Maybe = int(args[7])
	charaIdx = int(args[8])

	charaName = getCharaName(int(imgIdxStr))
	charactors[charaIdx] = charaName

	print_out("show {} {}:".format(charaName, imgIdxStr))
	print_out("    xpos {}".format(str(xOffset/800)))
	return True

def cmd_EraseCharactor(args):
	charaIdx = int(args[1]);
	print_out("hide {}".format(charactors[charaIdx]))
	return True

def cmd_EraseCharaAll(args):
	for i in charactors:
		print_out("hide {}".format(charactors[i]))
	return True

def cmd_SetTitle(args):
	print_out("# (I dunno how to save it to RenPy) Chapter: {}".format(args[0])) #TODO: use chapters in RenPy
	return True

def cmd_SetCount(args):
	print_out("$ var_{} = {}".format(args[0], args[1]))
	return True

def cmd_AddCount(args):
	print_out("$ var_{} = var_{} + {}".format(args[0], args[0], args[1]))
	return True
	
def cmd_GetCount(args):
	print_out("if var_{} == {}:".format(args[0], args[1]))
	print_out("    jump {}_jmp_{}".format(scriptName, str(0)))
	print_out("else:")
	print_out("    jump {}_jmp_{}".format(scriptName, str(1)))
	return True

def cmd_SetSelectEx(args):
	print_out("menu:")
	for i in range(0,2):
		print_out("    \"{}\":".format(args[i]))
		print_out("        jump {}_jmp_{}".format(scriptName, str(i)))
	return True

def cmd_stub(args):
	return True

def cmd_SetMenu(args):
	x = int(args[0])
	y = int(args[1])
	w = int(args[2])
	h = int(args[3])
	cutX = int(args[4])
	cutY = int(args[5])
	print_out("convert \"data01/data 0000.png\" -crop {}x{}+{}+{} btn.png".format(w,h,cutX,cutY))
	print_out("composite -geometry +{}+{} btn.png back0001_active.png back0001_active.png".format(x,y))

cmdStrings = {
	"SetBackGround"		:	cmd_SetBackGround,
	"ChangeBackGround"	:	cmd_ChangeBackGround,
	"SetMessage"		:	cmd_SetMessage,
	"SetNameWindow"		:	cmd_SetNameWindow,
	"EraseNameWindow"	:	cmd_EraseNameWindow,
	"SetWait"			:	cmd_SetWait,
	"SetOmake"			:	cmd_setOmake,

# Sound
	"StopBGM"			:	cmd_StopBGM,
	"SetBGM"			:	cmd_SetBGM,	
	"SetCVEx"			:	cmd_SetCVEx,
	"SetCV"				:	cmd_SetCVEx, #The same
	"SetSE"				:	cmd_SetSE,

	"SetTitle"			:	cmd_SetTitle,

	"SetEffect"			:	cmd_SetEffect,

	"LoadScript"		:	cmd_LoadScript,
	"CallScript"		:	cmd_LoadScript, # The same

	"CP_Start"			:	cmd_stub,
	"CP_End"			:	cmd_stub,

	"ChangeCharactor"	:	cmd_ChangeCharactor,
	"EraseCharactor"	:	cmd_EraseCharactor,
	"EraseCharaAll"		:	cmd_EraseCharaAll,

	"SetCount"			:	cmd_SetCount,
	"AddCount"			:	cmd_AddCount,
	"GetCount"			:	cmd_GetCount,

	"SetSelectEx"		:	cmd_SetSelectEx,

# Menu
	 "SetMenu"			:	cmd_SetMenu,

# Stubs
	"FadeIN"			:	cmd_stub,
	"FadeOUT"			:	cmd_stub,

	"SetBuffer"			:	cmd_stub,
	"SetMode"			:	cmd_stub,
	"MoveAll"			:	cmd_stub,
	"SetWindow"			:	cmd_stub, # Maybe should be handled
}

def getCharaName(idx): # Game-specific!
	if (idx>=5 and idx<=84):
		return "erena"
	if (idx>=85 and idx<=116):
		return "emiru"
	if (idx>=117 and idx<=127):
		return "karen"
	if (idx>=128 and idx<=139):
		return "ovi"
	return "data"

def applyEffect():
	global effectArgs
	if (len(effectArgs)==0):
		return ""
	if (effectArgs[0]=='2' and effectArgs[1]=='1'):
		waitMs = int(effectArgs[2])
		effectArgs = []
		return "with Shake((0, 0, 0, 0), {}, dist=30)".format(str(waitMs/1000))

def h_NameWindowText(l):
	global speakerName
	if (m := re.search(r_parseNameWindowText, l)):
		speakerName = '"'+m.group(1)+'"'
		return True
	return False

def h_CPlabel(l):
	global cpLabel
	if (m := re.search(r_parseCPlabel, l)):
		cpLabel = m.group(1)
		return True
	return False

def h_jumpTag(l):
	if (m := re.search(r_parseJumpTag, l)):
		print_out("label {}_jmp_{}:".format(scriptName, m.group(1)), True)
		return True
	return False

def h_cmd(l):
	if (m := re.search(r_parseCommand, l)):
		cmdName = m.group(1)
		args = re.split(r_splitArgs, m.group(2))
		comment = m.group(3)
		if (comment):
			print_out("# ↓ {}".format(comment.strip()))
		for i, s in enumerate(args):
			args[i] = s.replace('"','').strip()
		try:
			f = cmdStrings[cmdName]
		except KeyError:
			print("Haven't handler for {} command".format(cmdName))
			print_out("#TODO: {}".format(l))
			return True
		except:
			print ("Unknown Exception")
			return False
		#try:
		return f(args)
		#except:
		#	print ("ERROR: Unknown Exception during command handler execution")
	return False

def h_comment(l):
	#print("Don't know how to handle \"{}\". Applying as comment".format(l))
	print_out("#{}".format(l))

def print_out(l, suppressIdentation=False):
	if (len(l)>0):
		if (not suppressIdentation):
			outFile.write(" "*identation)
		outFile.write(l)
	outFile.write("\n")

def parseLine(l):
	l=l.strip()
	if (len(l)==0):
		return print_out(l)
	#if (h_NameWindowText(l)):
	#	return
	if (h_CPlabel(l)):
		return
	if (h_jumpTag(l)):
		return
	if (h_cmd(l)):
		return
	return h_comment(l)

if (len(sys.argv)==1):
	print("Usage: {} inputScript outputScript".format(sys.argv[0]))
	exit()

inFileName = sys.argv[1]
outFileName = sys.argv[2]

scriptName = os.path.basename(inFileName)
print("Script: " + scriptName)

outFile = open(outFileName, 'w')
print_out("label script_{}:".format(scriptName))
identation = 4

try:
	with open("translate_names.csv", 'r') as f:
		for line in f:
			lComp = line.strip().split('\t')
			try:
				charactors_names.append(lComp[2])
			except:
				charactors_names.append("")
		f.close()
except:
	print("Failed to open translate_names")

with open(inFileName, 'r') as f:
	for line in f:
		parseLine(line)
	f.close()

outFile.close()
