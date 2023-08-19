import Graphing
import AudioProcessor
import Note
import Main
import ui.UI as UI

import librosa
import numpy as np
import copy


#https://en.wikipedia.org/wiki/Chroma_feature
# {C, C♯, D, D♯, E , F, F♯, G, G♯, A, A♯, B} => chroma
# 1, 5, 2, 7 => octave
# C4, A5, Db2 => note


# Rows, Frames

TEMPO_BOUNDRY = 140

CHROMA = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]

LOWEST_OCTAVE_DB = 5

HARMONIC_OCTAVE_MAX_DIFFERENCE_DB = 2


MAX_NOTE_DURATION = 4

MAX_N_VOICES = 4


IS_POLYPHONIC = True

def get_notes(processedAudioData):
    """Takes in spectrum, chroma, onsets and tempo and returns all of the voices with their respective notes."""
    global finishedNotes
    UI.progress("Generating Notes")
    
    spectrumRowCache = __cache_note_to_spectrum_row()
    UI.diagnostic("Cached Spectrum Rows", str(spectrumRowCache))
    UI.diagnostic("Onsets", str(processedAudioData.onsets))
    tempo = __fix_tempo(processedAudioData.tempo)

    frameCount = processedAudioData.spectrum.shape[1]



    #start = onsets[0]
   # for x in range(len(onsets)):
    #    onsets[x] -= start


    if IS_POLYPHONIC:
        for currentFrame in range(frameCount):
            #__get_notes_at_frame(currentFrame,processedAudioData)
            __process_info_at_frame(currentFrame,processedAudioData)

        UI.stop_spinner()
        return (finishedNotes,tempo)


    # IF HOMOPHONIC. Legacy
    notes = []
    for x,onset in enumerate(processedAudioData.onsets):



        strongestChroma = np.argsort(processedAudioData.chroma[:,onset])[::-1][:1]

        

        octave = __get_octave(CHROMA[strongestChroma[0]],onset,processedAudioData.spectrum)

        note = Note.Note(CHROMA[strongestChroma[0]],octave,onset,tempo,frameCount)
    
        if x == len(processedAudioData.onsets) -1:
            endSample = processedAudioData.onsets[-1] + 2
        else:
            endSample = processedAudioData.onsets[x+1]
        note.set_duration(endSample)

        notes.append(note)
    
    UI.stop_spinner()
    return (notes,tempo)


def __fix_tempo(rawTempo):
    """Correctly reduces tempo, based on TEMPO_BOUNDRY."""
    tempo = rawTempo

    while tempo > TEMPO_BOUNDRY:
        tempo //= 2
    
    UI.diagnostic("Corrected Tempo",tempo, "bpm")
    return tempo





def __row_to_note(row):
    freqs = np.arange(0, 1 + AudioProcessor.N_FFT / 2) * AudioProcessor.samplingRate / AudioProcessor.N_FFT

    return librosa.hz_to_note(freqs[row],unicode=False)

def __note_to_row(note):
    freqs = np.arange(0, 1 + AudioProcessor.N_FFT / 2) * AudioProcessor.samplingRate / AudioProcessor.N_FFT
    hz = librosa.note_to_hz(note)
    smallestDist = 10000
    smallestRow = -1

    for x,freq in enumerate(freqs):
        dist = abs(freq - hz)
        
        if dist < smallestDist:
            smallestRow = x
            smallestDist = dist
    
    if smallestRow == -1:
        UI.warning("Row corresponding to note not found!")
        return 0

   # UI.diagnostic("NOTE_TO_ROW","{} => {}".format(note,smallestRow))
    return smallestRow




def __cache_note_to_spectrum_row():
    freqs = np.arange(0, 1 + AudioProcessor.N_FFT / 2) * AudioProcessor.samplingRate / AudioProcessor.N_FFT
    cache = {}
    lowestNote = "A0"
    lowestNoteDetected = False
    for x in range(1,len(freqs)):

        freq = freqs[x]
        note = librosa.hz_to_note(freq,unicode=False)
        if note == lowestNote:
            lowestNoteDetected = True
        if not lowestNoteDetected:
            continue
       
        cache[note] = x

    return cache



def __get_octave(note,onset,spectrum):
    strongest = -1000
    strongestI = -1
    for i in range(1,9):
        val = np.mean([spectrum[__note_to_row(note + str(i)),onset],
                       spectrum[__note_to_row(note + str(i)),onset]+1,
                       spectrum[__note_to_row(note + str(i)),onset]+2])

        if val > strongest:
            strongest = val
            strongestI = i

       # if val > LOWEST_OCTAVE_DB:
        #    return i

    if strongestI == -1:
        UI.warning("Octave not found!")
        return 0
    return strongestI
        #if val > strongest:
        #    strongest = val
        #   strongestI = i
        
    #return strongestI






def __harmonic_octave_detection():
    pass

def __get_key_signature():
    pass

def __get_time_signature():
    pass




currentNotes = {}
finishedNotes = []



def __guess_voice_count_at_sample(spectrum,sample):



    notes = {}
    for octave in range(1,7):
        for chroma in CHROMA:
            
            note = chroma + str(octave)
            row = spectrum[__note_to_row(note),sample]

            if row < 15:
                continue
            
            notes[note] = row


    #print(notes)

    # Check for chromatic neighbours
    keys = notes.keys()
    #print(keys)
    notesDeletionQueue = []
    skipNeighbour = False
    for note in keys:
        if skipNeighbour:
            skipNeighbour = False
            continue
        
        chroma = note[:-1]
        octave = int(note[-1:])
        for i in range(octave+1,7):
            octaveNote = chroma + str(i)
            if octaveNote in notes:
                notesDeletionQueue.append(octaveNote)

        # Check fifth
        

        noteIndex = CHROMA.index(chroma)
        
        # B4 => C5
        if noteIndex == 11:
            noteIndex = -1
            octave += 1
        
        chromaticNextNeighbour = CHROMA[noteIndex+1] + str(octave)

        #print(note,chromaticNextNeighbour)

        
        if not chromaticNextNeighbour in notes:
            continue
        row = notes[note]
        neighbourRow = notes[chromaticNextNeighbour]
    
        difference = row - neighbourRow

        # Neighbour is greater
        if difference < -2.5:
            notesDeletionQueue.append(note)

        # Row is greater
        if difference > 2.5:
            notesDeletionQueue.append(chromaticNextNeighbour)
                

    #print("Deleted", notesDeletionQueue)
    for note in notesDeletionQueue:
        notes.pop(note)


    nVoices = 0
    for note in notes:
        nVoices += 1

    #UI.diagnostic("Voice count",nVoices)
    return nVoices


def __linearalise_db(db):
    return 10**(db/10)


previousNotes = []
def __remove_invalid_notes(notes,strengths,frame,processedAudioData):
    global previousNotes

    for x, note in enumerate(notes):
        if x == len(notes) - 1:
            break


        nextNote = notes[x+1]
        
        strength = strengths[x]
        nextStrength = strengths[x+1]

        chroma = note[:-1]
        nextChroma = nextNote[:-1]
        
        chromaIndex = CHROMA.index(chroma)
        nextchromaIndex = CHROMA.index(nextChroma)


        ## Neighbour check
        if abs(chromaIndex - nextchromaIndex) % 10 != 1:
            continue
    
        ## Both are strong enough
        if strength > 0.7 and nextStrength > 0.7:
            continue

        
    
        


    pass

def __process_info_at_frame(frame,processedAudioData):
    global currentNotes,finishedNotes
    spectrum = processedAudioData.spectrum
    chroma = processedAudioData.chroma
    onsets = processedAudioData.onsets
    #for x,row in enumerate(spectrum[:,sample]):
    notes, strengths = __get_notes_at_frame(frame,processedAudioData)

    ## Find new notes
    if frame in processedAudioData.onsets:
       

        for note in notes.keys():
            if note not in currentNotes:
                chroma = note[:-1]
                octave = int(note[-1:])
                startStrength = __linearalise_db(spectrum[__note_to_row(note),frame])
                currentNotes[note] = Note.Note(chroma,octave,frame,processedAudioData,startStrength)

        
    
        notesToRemove = []

        for note in currentNotes.keys():
            currentStrength = __linearalise_db(spectrum[__note_to_row(note),frame])
            #if currentStrength / currentNotes[note].startStrength < 0.96:

            if note not in notes and currentNotes[note].startFrame != frame:
                notesToRemove.append(note)
                if frame - currentNotes[note].startFrame < 4:
                    continue
                if currentNotes[note].set_duration(frame):
                    finishedNotes.append(currentNotes[note])


        for note in notesToRemove:
            currentNotes.pop(note)

        
        for note in currentNotes.keys():
            chromaIndex = CHROMA.index(note[:-1])
            currentNotes[note].lifeTimeStrengths = np.append(currentNotes[note].lifeTimeStrengths, processedAudioData.chroma[chromaIndex,frame])



def __get_notes_at_frame(frame,processedAudioData):
    chroma = processedAudioData.chroma

    strongestNotes = []
    strengths = []

    for x,row in enumerate(chroma[:,frame]):
        if row < 0.25:
            continue
        
        chroma = CHROMA[x]
        octave = __get_octave(chroma,frame,processedAudioData.spectrum)
        strongestNotes.append((chroma + str(octave)))
        strengths.append(row)

        
    if frame in processedAudioData.onsets:
        print(strongestNotes)
    return (strongestNotes,strengths)