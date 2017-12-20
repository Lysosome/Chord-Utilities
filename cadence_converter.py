"""
Ben Ma

Overall pseudocode:
1. open file
2. go through entire file line by line
	a. -Reset stage-
		Reset origChords and numChords
		Reset tonic key
	b. -Reading-
        if the line is an empty line "\n," just skip to next line
        if the line is not a SONGMARKER, then add the current line to the song_chords list
        Make sure to add \n's to the array so it prints lines and maintains the same format as input file
        once we've reached a SONGMARKER, then we can start processing
	c. -Processing-
        Check if there's anything in the song_chords list... if not, skip to reset stage
        Find the tonic key
        Simply replace each chord with its Roman Numeral (see below)

Steps to find Roman Numeral:
1. Find tonic chord, store number of that chord (e.g. D = 2)
2. Then scan through each chord in the song, converting it to number chord
	a. Now we have a sequential list of chords in the form like (w9m w5 w6dim)
3. Find relative semitones of all chords (pretty much casting it to C)
	a. Take chord e.g. w5, then subtract number of the chord (w5-2 = w3)
	b. This way the tonic will always end up at w0
4. Figure out intervals based on semitones
	a. e.g. 0 is I, 2 is II, 4 is III, 5 is IV, 7 is V, 9 is VI, 11 is VII

"""

import caster

def findTonicNum(songChords, keyTable): #songChords is a list, keyTable is a list of lists
    maxKey = 0 #0 thru 11 for C thru B
    maxScore = 0
    for i in range(0,len(keyTable)): #go thru each of the 12 keys--example for key of C: C Dm Em F G G7 Am Bdim
        curScore = 0
        key = keyTable[i]
        for chord in songChords:
            for j in range(0,len(key)): #go thru each note in the major scale of the key
                note = key[j]
                if chord==note:
                    if (j == 1 or j == 2 or j == 7):
                        curScore+=0.9 #tiebreaker: the ii, iii, and vii are weighted less
                    else:
                        curScore+=1 #if it's a match, add 1 to the "score" of the current key
                    break
        if curScore>maxScore:
            maxScore=curScore
            maxKey = i
    return maxKey #return key with most matches for the chords in the song

#global scope variables
noteNums = [('C#', 1), ('D#', 3), ('F#', 6), ('G#', 8), ('A#', 10), ('C', 0), ('D', 2), ('E', 4), ('F', 5), ('G', 7),
            ('A', 9), ('B', 11)]  # have to check the sharps first so it doesn't switch 'C#' into 'w0#'

# read in cadence casting table
with open('cadence_casting_UTF-8.txt', 'r') as f:
    inputs = []
    outputs = []
    exploLine = []
    for line in f:
        exploLine = line.split("\t")
        exploLine[0] = exploLine[0].replace('\xef\xbb\xbf', '')  # clean up special chars
        inputs.append(exploLine[0].replace('\ufeff', '').strip())  # clean up the special chars
        outputs.append(exploLine[1].replace('\n', '').strip())  # clean up special chars
    castingTable = list(zip(inputs, outputs))  # convert casting table to a list of tuples
    print("Opened Cadence Casting Table")
print(castingTable)  # test to make sure we've read in the table correctly

# read in key tables for finding tonic num
keyTable = []
with open('key_table_UTF-8.txt', 'r') as f:
    curLine = f.readline()
    while(curLine!=""):
        keyTable.append(curLine.split())
        curLine = f.readline()
print(keyTable) # test to make sure we've read table correctly

#read in chords from file, song by song
#split is by "  | | S O N G M A R K E R | |", and it starts with lyrics and the songmarker is AFTER each song

with open('chords_uku_english_only_songmarkers.txt', 'r') as f:
    with open('cadences_uku_english_only_songmarkers.txt', 'w') as out:
        curLine = f.readline()
        while (curLine!=""):
            #--STAGE 0: RESET--
            origChords = []
            numChords = []
            tonicNum = 0
            songmarker = ""

            #--STAGE 1: READING SONG--
            if (curLine!="\n" and curLine.find("| | S O N G M A R K E R | |")==-1):
                while(curLine.find("| | S O N G M A R K E R | |")==-1): #while we're not at the Songmarker
                    lineChords = curLine.split()
                    for chord in lineChords:
                        origChords.append(chord)
                    origChords.append('\n') #keep output of original file intact
                    curLine = f.readline()
                songmarker = curLine #make sure we print the songmarker line after each song
            # now we've hit a songmarker, so let's move on to processing!
            else:
                out.write(curLine) #keep the formatting of original file intact

            #--STAGE 2: PROCESSING--
            #only process if there actually are chords in origChords
            if(len(origChords)>0):
                #find tonic chord
                tonicNum = findTonicNum(origChords, keyTable)

                #convert all chords in song to number chords
                for origChord in origChords:
                    origChord = caster.makeFlatsSharps(origChord)
                    # shift numeral chord to relative to C (w0)
                    numChords.append(caster.shiftNumChord(caster.letterChordToNumChord(origChord, noteNums),-tonicNum))

                #cast to correct interval based on semitones
                #we convert each chord to its interval notation (e.g. V, vi, I, etc.)
                for i in range (0,len(numChords)):
                    for chord in castingTable:
                        if numChords[i] == chord[0]:
                            numChords[i] = chord[1]
                            break #break out of inner loop

                #print
                for numChord in numChords:
                    out.write(numChord)
                    if numChord != '\n':
                        out.write(" ")
                out.write(songmarker)
            curLine = f.readline();
