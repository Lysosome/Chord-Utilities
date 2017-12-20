import re

#author: Ben Ma
#possibly helpful library: music21 http://web.mit.edu/music21/



def nm(name, x):  # named capture group
    return r'(?P<' + name + '>' + x + r')'


def numChordToLetterChord(numChord):
    noteNums = [('C#', 1), ('D#', 3), ('F#', 6), ('G#', 8), ('A#', 10), ('C', 0), ('D', 2), ('E', 4), ('F', 5),
                ('G', 7), ('A', 9), ('B', 11)]
    letterChord = numChord
    i=0 #have to use a while loop bc len(letterChord) is changing
    while i < len(letterChord):  # for each letter in the letterChord
        selectionSize=0
        if letterChord[i]=='w':
            #if the next digit is a 1 look for the next digit being 0 or 1 (i.e., 10 or 12)
            if letterChord[i+1]=='1' and i<len(letterChord)-2 and \
                (letterChord[i+2]=='0' or letterChord[i+2]=='1'):
                selectionSize=3;
            else:
                selectionSize=2;
            wdigit = int(letterChord[i+1:i+selectionSize])
            for note in noteNums:
                if note[1]==wdigit:
                    # replace the entire 'w'+digit with the corresponding note
                    letterChord = letterChord[0:i] + str(note[0]) + letterChord[i+selectionSize:len(letterChord)]
                    break
        i+=1
    return letterChord

def letterChordToNumChord(letterChord,noteNums):
    noteNums = [('C#', 1), ('D#', 3), ('F#', 6), ('G#', 8), ('A#', 10), ('C', 0), ('D', 2), ('E', 4), ('F', 5),
                ('G', 7), ('A', 9), ('B', 11)]
    numChord = letterChord
    for note in noteNums:  # for each note C, C#, D, ...
        for i in range(0, len(numChord)):  # for each letter in the numChord
            if len(note[0]) == 2:  # If it's a sharp note
                if i < len(numChord) - 1 and note[0] == numChord[i:i + 2]:  # If there's a substring match
                    numChord = numChord[0:i] + 'w' + str(note[1]) + numChord[i + 2:len(numChord)]
            else:  # for all the naturals
                if note[0] == numChord[i]:  # If there's a substring match
                    numChord = numChord[0:i] + 'w' + str(note[1]) + numChord[i + 1:len(numChord)]
    return numChord

def shiftNumber(num, shift):
    num+=shift
    if num<0:
        num+=12
    else:
        num = num%12
    return num

def makeFlatsSharps(note):
    temp_note = note
    temp_note = temp_note.replace('Ab','G#')
    temp_note = temp_note.replace('Bb','A#')
    temp_note = temp_note.replace('Eb','D#')
    temp_note = temp_note.replace('Db','C#')
    temp_note = temp_note.replace('Gb','F#')
    return temp_note

def shiftNumChord(origChord, shift):
    newChord = origChord
    i = 0  # have to use a while loop bc len(newChord) is changing
    while i < len(newChord):  # for each letter in the newChord
        selectionSize = 0
        if newChord[i] == 'w':
            # if the next digit is a 1 look for the next digit being 0 or 1 (i.e., 10 or 12)
            if newChord[i + 1] == '1' and i < len(newChord) - 2 and \
                    (newChord[i + 2] == '0' or newChord[i + 2] == '1'):
                selectionSize = 3;
            else:
                selectionSize = 2;
            wdigit = int(newChord[i + 1:i + selectionSize])
            newdigit = shiftNumber(wdigit,shift)
            newChord = newChord[0:i] + 'w' + str(newdigit) + newChord[i + selectionSize:len(newChord)]
        i += 1
    return newChord

if __name__ == "__main__":
    #read in text file with chords
    with open('chords_and_lyrics_UTF-8.txt', encoding="utf8") as f:
        fullText = f.read()
        print("Opened Chords and Lyrics file")
    print(fullText[0:100]); #test
    
    #read in chord casting table
    with open('chord_casting_UTF-8.txt', encoding="utf8") as f:
        inputs=[]
        outputs=[]
        exploLine=[]
        for line in f:
            exploLine = line.split("\t")
            inputs.append(exploLine[0].replace('\ufeff', '')) #clean up the special chars
            outputs.append(exploLine[1].replace('\n', '')) #clean up special chars
        castingTable = list(zip(inputs, outputs))
        print("Opened Chord Casting Table")
    print(castingTable) #test
    #identify chords in text file with regex and distill them into separate list of only chords
    '''
        Rules
        1. will be preceded by a whitespace
        2. will start with a capital letter from 'A' to 'G'
        3. the first character will be followed by zero or more of these endings:
            b. '#'
            c. 'b'
            d. a digit 1-13 (inclusive)
            e. 'min'
            f. a slash '/'
            g. 'maj'
            h. 'dim'
            i. 'aug'
            j. 'add'
            k. 'sus'
            l. 'm' (check LAST so it doesn't take out 'min' or 'maj')
        4. the expression must end with a whitespace,
        and ALL characters must be in the patterns above
        
        special case: check if "Am" is followed by whitespace then "I", as in "Am I lonely?"
        special slash case: if slash is found, analyze the interval
    '''
    #PARTS ADAPTED FROM POWERCHORD ONLINE PROJECT:
    #https://github.com/brunodigiorgi/powerchord/blob/master/powerchord/chord_regex.py
    
    #define re rules
    re_natural = r'[A-G]'
    re_modifier = r'#*b*'
    re_note = (re_natural + re_modifier)
    re_chord = (r'(maj|min|dim|aug|add|sus|m)')
    re_interval = (r'([1-9]|1[0-3])')
    re_slash = '/'
    re_optional = r'('+re_chord+'|'+re_interval+'|'+re_slash+'|'+re_note+')'
    returnablePattern = re_note + re_optional + r'*'
    chordPattern = (r'\s' + nm('chordRet', returnablePattern) + r'\s')
    
    #find matches
    matchIter = re.finditer(chordPattern, fullText)
    origChords = []
    for elem in matchIter:
        s = elem.start()
        e = elem.end()
        print('Found "%s" in the text from %d to %d ("%s")' % \
              (elem.re.pattern, s, e, elem.group('chordRet') ))
        #check for special case "Am I"
        if elem.group('chordRet') != 'Am' or fullText[e]!='I':
            origChords.append(elem.group('chordRet'))
    
    #make a new list with the cast of each chord, using the table, and count the amount of each chord
    castedChords = []
    #have to check the sharps first so it doesn't switch 'C#' into 'w0#'
    noteNums = [('C#',1),('D#',3),('F#',6),('G#',8),('A#',10),('C',0),('D',2),('E',4),('F',5),('G',7),('A',9),('B',11)]
    
    
    for origChord in origChords:
        #example of process: E/C# -> w4/w1 -> w0/w9 (store shift as 4) -> C/A -> Am -> w9m -> w1m -> C#m
        #convert origChord to numeral version
        tempChord = letterChordToNumChord(origChord,noteNums)
        #shift numeral chord to C numeral version
        if tempChord[1]=='1' and len(tempChord)>2 and \
            (tempChord[2]=='0' or tempChord[2]=='1'):
            rootNum = int(tempChord[1:3])
        else:
            rootNum = int(tempChord[1])
        shift = rootNum
        tempChord = shiftNumChord(tempChord, -shift)
        #convert C numeral version to C letter version
        tempChord = numChordToLetterChord(tempChord,noteNums)
        #cast C letter version using table
        for chord in castingTable:
            if tempChord == chord[0]:
                tempChord = chord[1]
                break
        #convert casted letter chord to casted numeral chord
        tempChord = letterChordToNumChord(tempChord)
        #shift casted numeral chord back
        tempChord = shiftNumChord(tempChord, shift)
        #convert casted numeral chord to casted letter chord
        tempChord = numChordToLetterChord(tempChord)
        print('Converted '+origChord+' to '+tempChord)
        castedChords.append(tempChord)
    print('Finished!')