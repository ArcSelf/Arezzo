from midiutil.MidiFile import MIDIFile
import Main
import os
import subprocess
import time
import cui.CUI as CUI
import Utils
import time
import Config as cfg


def generate_midi_file(notes,tempo,outputName) -> None:
    """Takes a list of note objects, and a tempo and creates a MIDI file."""

    if not cfg.CONFIG["DEBUG"]["generate_sheet_music"]:
        return
    

    CUI.progress("Generating MIDI")
    print(notes)



    earliestStartTime = __get_earliest_start_time(notes)


    midiFile = MIDIFile(len(notes))

    track = 0
    time = 0
    channel = 0
    volume = 100

    midiFile.addTrackName(track, time, "Track")
    midiFile.addTempo(track, time, tempo)



    for note in notes:
        midiFile.addNote(track, channel, note.midi, note.start - earliestStartTime, note.duration, volume)

    # write it to disk

    midiPath = "output\\midi\\{}.mid".format(outputName)

    CUI.diagnostic("MIDI:",midiPath)


    with open(midiPath, 'wb') as outf:
        midiFile.writeFile(outf)


    __generate_sheetmusic_musescore(midiPath)


def __generate_sheetmusic_musescore(midiPath: str) -> None:
    """Uses musescore to generate a pdf, given a midi file path."""
    CUI.progress("Generating Sheet music")
    
    # Help
    command = f'src\\MusescoreCaller.bat "{Main.MUSECORE4_PATH}" "output\\sheet music\\{Main.outputName}.{Main.EXPORT_TYPE}" "{midiPath}"'
  

    Utils.sys_call(command)






def __get_earliest_start_time(notes) -> float:
    earliest = 10_000

    for note in notes:
        if note.start < earliest:
            earliest = note.start
    return earliest