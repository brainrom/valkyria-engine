# Valkyria engine reverse

This document describes Valkyria engine reverse-engineering process.
This manual assumes, that you already unpacked scripts.
Commands arguments meaning are reversed by examining Mahou Shoujo Erena script.

# Convert to UTF-8
```
mkdir utf8
for f in *; do iconv --verbose -f SJIS-WIN -t utf-8 $f > utf8/$f; done;
```

# Get instruction set (unique commands)
`grep -ohEr "%[^\(]{1,}" . | cut -c 2- | sort | uniq`

# Get used resources for command
`grep -ohrE "SetSE\(.{0,}[0-9]{1,4}" . | cut -c 6- | awk '{$1=$1};1' | sort | uniq`

# Mahou Shoujo Erena unused resources
### BGM
- 0000 (empty)
- 0014 (empty)
### SE
- A LOT...

### BG
Mostly these BGs is a wiered green screen
- 0005
- 0010
- 0025
- 0026
- 0082
- 0083
- 0351
- 0352
- 0353

# Instructions
AddCount(counterIndex, value) // counterIndex=3, var2=1 // Increments counter
CP_Start() // Memory scene start
CP_End() // Memory scene end
CallScript ( scriptNumber ) // Load	script and then jumps to it's start
CallScript ( var1, var2, var3 ) // Used in menu scripts to do some jumps
ChangeBackGround (backgroundIndex, var1, var2) // var1=1,2 var=0,1
ChangeCharactor(charactorIndex, x1, y1, x2(?),y2(?), resX(?), resY(?), var1, var2) var1=0,2 (show time?) var2=0,1 (charactor number on scene?)
EraseCharaAll(var1, var2) // var1=3, var2=0 args
EraseCharactor(var1, var2) //var1=2, var2=0,1 (charactor number on scene?)
EraseMenubar() // Menu only.
EraseMessage(var1) var1=0
EraseNameWindow(var1) //var1=0,1
EraseWindow(var1) // var1=0,2
FadeIN (var1) //var1=0 
FadeIN (var1, timeS) // Menu only. timeS=2,3 var2=0
FadeOUT (backgroundIndex, var2, var3)  // backgroundIndex=0008,0009(black,white respectively), timeS=0,1,2,3, var3=0 
Game_END (used only once)
GetCount(counterIndex, value) // Jumps to #0 if counter equal to value, otherwise jumps to #1 (TODO: check)
GetLAverage(var1,var2,var3) // Menu only. Convert to percentage comment in code
GetLOmake+ (var1, var2, var3) // Menu only. Loop and check flags comment in code
GetOmake(flag1, flag2) // Menu only. Check flag. Jumps to #0 if true, otherwise jumps to #1
LoadScript(scriptNumber) // Loads script to memory (after current script is finished, executes loaded script)
MoveAll(var1) // var1=1
ReleaseScript() // Used twice in menu code...
Reset() // Used only in menu, maybe resets variables, etc.
SetBGM(bgmIndex) // Play music
SetBackGround(backgroundIndex, var1, var2) //var1=0, var2=0 May not affect?
SetBuffer(var1) //var 1=0,0001
SetCVEx(voiceIndex, charaNum) //charaNum=0,1,2,3 // Play voice. charaNum corresponds with the snd/data__.odn archive (on Mahou Shoujo Erena)
SetCount(var1,var2) //var1=3, var2=1 (used only once)
SetEffect(var1, var2 ,timeMs) //var1=2, var2=1, timeMs=500,1000 // 2,1 - shaking
SetInitialize("", "", "", "") (used only once)
SetLCount(varIndex, value) // Set variable?
SetMenu( scriptNumber ) // Jump to menu... script.
SetMenu( x, y, w, h, activeBtnImgX, activeBtnImgY, actionScript, btnIndex ) // Adds button to menu
SetMenubar ( scriptNumber, menubarText ) // Menubar return button?
SetMessage(messageText, colorR, colorG, colorB) // The most useful command. Displays VN messages
SetMode(modeIndex) modeIndex=0(game),1,17,23
SetNameWindow(charaNum,var2) // Sets charactor name sprite from image file. //charaNum=0-18 //var2=0
SetOmake(flagNumber) // sets flag. For gallery?
SetOptionSetup (used only once)
SetRButton(var1) // Menu only. var1=0008,0009,0010
SetSE(seNumber) // Play Sound Effect
SetSaveSysSetup(var1,var2) Only menu. Used only once. var1=14, var2=16
SetSelectEx(choice1Text, choice2Text, var1) // Displays choices. var1 are always 2 (maybe 2 choices). Jumps to #-indexed choice (0 or 1) 
SetTitle(chapterText) //Sets chapter name (for saves)
SetURL(urlText) // Set URL for open in browser (maybe, do open command)
SetWait(timeoutMs, skipable=0) // wait. When skipable=1, timeout can be skipped.
SetWindow(var1, var2) //var1=2, var2=1,10
StopBGM(var1) //var1=2

# Search commands usage 
`grep -r "commandname" .`

# Mahou Shoujo Erena archives
- data00 - background images
- data01 - foreground images
- data02 - main script and menu logic
- data03 - BGM
- data04 - sound effects
- data05 - not opens
- data06 - menu elements positions

# Rename sounds to resolve name
## BGM
`for f in data03/*; do mv $f data03/bgm$(basename $f | cut -c 5-); done;`

## SFX
`for f in data04/*; do mv $f data04/sfx$(basename $f | cut -c 5-); done;`

# Rename charactors images
```
for i in {0005..0084}; do mv data$i.png erena\ $i.png; done;
for i in {0085..0116}; do mv data$i.png emiru\ $i.png; done;
for i in {0117..0127}; do mv data$i.png karen\ $i.png; done;
for i in {0128..0139}; do mv data$i.png ovi\ $i.png; done;
```
# Convert gamescript
`for f in ~/erena/data02_utf8/gamescript/*; do ~/erena_workspace/convertValkyria.py $f ~/Mahou\ Shoujo\ Erena/game/gamescript/$(basename $f).rpy; done;`
## Fix names
`for f in ~/Mahou\ Shoujo\ Erena/game/gamescript/scrp*.rpy; do ~/erena_workspace/replaceTranslation.py ~/erena_workspace/translate_names.csv "$f"; done;`
## Inject translation
`for f in ~/Mahou\ Shoujo\ Erena/tl/Lang/gamescript/scrp*.rpy; do ~/erena_workspace/replaceTranslation.py ~/erena_workspace/translate_pair.csv "$f"; done`

# Porting sequence
1. Convert entire script to UTF-8
2. Separate menu logic from main gamescript
3. Convert gamescript to RenPy (convertValkyria.py). If you already have translate_names.csv file, names will be replaced to aliases, then do p.6, p.10
4. Extract charactors' names string literals from script and place it in translate_names.csv file, assign aliases to its
5. Replace charactors' names string literals to its aliases (replaceTranslation.py)
6. Generate translation via RenPy
7. And extract dialogs to table
8. Translate game (by MTL or manually)
9. Make original text - translated text dictionary table (pairTranslation.py)
10. Inject translation into RenPy's tl scripts (replaceTranslation.py)
