import music21
import pretty_midi
import mido
from mido import MidiFile
from mido import tempo2bpm, tick2second, second2tick
import random as rand
from collections import Counter
from midiutil.MidiFile import MIDIFile

#######################################################################
# Solution of the 2nd assignment for Introduction to the practical AI #
# Adela Krylova BS20-02, a.krylova@innopolis.university, 07.05.2022   #
#######################################################################

####################
song = "input1.mid"
#################


OCTAVES = list(range(11))
mid = MidiFile(song)

CM_scale = [45, 47, 48, 50, 52, 53, 55, 57, 59]
DM_scale = [49, 50, 52, 54, 55, 57, 59, 61, 62]
EM_scale = [49, 51, 52, 54, 56, 47, 59, 61, 63]
FM_scale = [48, 50, 52, 53, 55, 57, 58, 60, 62]
GM_scale = [48, 50, 52, 54, 55, 57, 59, 60, 62]
BM_scale = [43, 45, 46, 48, 50, 51, 53, 55, 57]

Dm_scale = [48, 50, 52, 53, 55, 57, 58, 60, 62]
Em_scale = [48, 50, 52, 54, 55, 57, 59, 60, 62]
Am_scale = [45, 47, 48, 50, 52, 53, 55, 57, 59]
Gm_scale = [43, 45, 46, 48, 50, 51, 53, 55, 57]
Cism_scale = [49, 51, 52, 54, 56, 47, 59, 61, 63]
Hm_scale = [49, 50, 52, 54, 55, 57, 59, 61, 62]


# function returns Key and minor / major
def nameKey(songArg):
    score = music21.converter.parse(songArg)
    key = score.analyze('key')
    return key.tonic.name, key.mode


# returns tempo of the song
def get_tempo(SongArg):
    for t in SongArg.tracks:
        for msg in t:
            if msg.type == 'set_tempo':
                return msg.tempo
    else:
        return 500000


# returns number of bars in the song
def get_number_of_bars(songArg):
    for t in songArg.tracks:
        for msg in t:
            if msg.type == 'time_signature':
                return msg.numerator
    else:
        return 5

# key and minor / major
key_tonic, key_scale = nameKey(song)

# tempo of the song
tempo = get_tempo(mid)
tpb = mid.ticks_per_beat
bpm = round(second2tick(mid.length, tpb, tempo) / tpb)

# number of the bars per song
bars_num = get_number_of_bars(mid)
bars_num = bpm // bars_num


midi_data = pretty_midi.PrettyMIDI(song)

print(key_tonic, key_scale)
print(bars_num)
print(tempo)


################### Evolution algorithms ######################
used_notes = list()

if (key_tonic == "F" and key_scale == "major") or (key_tonic == "D" and key_scale == "minor"):
    used_notes = FM_scale
elif (key_tonic == "E" and key_scale == "minor") or (key_tonic == "G" and key_scale == "major"):
    used_notes = Em_scale
elif (key_tonic == "C#" and key_scale == "minor") or (key_tonic == "E" and key_scale == "major"):
    used_notes = Cism_scale
elif (key_tonic == "A" and key_scale == "minor") or (key_tonic == "C" and key_scale == "major"):
    used_notes = CM_scale
elif (key_tonic == "G" and key_scale == "minor") or (key_tonic == "B" and key_scale == "major"):
    used_notes = Gm_scale
elif (key_tonic == "H" and key_scale == "minor") or (key_tonic == "D" and key_scale == "major"):
    used_notes = DM_scale
else:
    used_notes = CM_scale

## START of the EVOLUTION ##

# (Here the pullum-et-ovum starts)

generation = list()  # gen_num generation / bars_num * 2 chords / 3 notes
gen_num = 10  # number of individuals in the population (generation)
chord_num = bars_num * 2  # number of chords for the song


def checkDistinct(chord):
    num = 0
    if (chord[0] == chord[1]):
        num += 1
    elif (chord[0] == chord[2]):
        num += 1
    elif (chord[1] == chord[2]):
        num += 1

    return num


#### Initial generation - GEN-0 (making the eggs) ####
run = True

for i in range(gen_num):
    complement = list()
    for j in range(chord_num):
        chord = list()
        for k in range(3):
            r = rand.randrange(0, 8, 1)
            chord.append(used_notes[r])

        complement.append(chord)
    generation.append(complement)


# Now we have created the egg, lets grow a chickens; an army of chickens!!!

## evaluation of the population ##

# returns list of winners (3winners) - their indexes in the population

# a function used by the fitness function to evaluate how much original chords are there within the complement
def checkOriginal(comp):
    import numpy as np
    array = np.array(comp)
    unique = np.unique(array)
    num_values = len(unique)
    return (num_values)


#  a function used by the fitness function to evaluate if the notes are not too closed to each other
def checkClosed(ch):
    eval = 0
    temp = ch
    temp = sorted(temp, reverse=True)

    if ((temp[0] - temp[1]) > 2):
        eval += 1

    if (temp[1] - temp[2] > 2):
        eval += 1

    return eval


# A fitness function
def fitnessFunction(genToEvaluate):
    winners = list()
    points = list()  # from -10 to 10

    # mark for every complement
    for a in range(0, gen_num):
        points.append(0)

    # for every complement within a genertion
    for a in range(0, gen_num):
        points[a] += checkOriginal(genToEvaluate[a])
        # for every chord
        for b in range(0, chord_num):
            # check distinct chords within a complement
            if checkDistinct(genToEvaluate[a][b]) > 0:
                points[a] -= 100
            points[a] += 100 * checkClosed(genToEvaluate[a][b])

    max1 = points.index(max(points))
    points[max1] = -1000
    max2 = points.index(max(points))
    points[max2] = -1000
    max3 = points.index(max(points))
    points[max3] = -1000

    winners.append(genToEvaluate[max1])

    winners.append(genToEvaluate[max2])

    winners.append(genToEvaluate[max3])
    return winners


## evaluate population

## Creating a new population ##


def makingEvolution(genToEvlutionare):
    newGen = list()
    winners = fitnessFunction(genToEvlutionare)

    # keep the best parents
    newGen.append(winners[0])
    newGen.append(winners[1])
    newGen.append(winners[2])

    # crossover the best ones
    newGen.append(crossover(winners[0], winners[1]))
    newGen.append(crossover(winners[2], winners[1]))
    newGen.append(crossover(winners[0], winners[2]))

    # make some mutations on the best ones
    newGen.append(mutate(winners[0]))
    newGen.append(mutate(winners[1]))
    newGen.append(mutate(winners[2]))

    r = rand.randint(0, gen_num - 1)

    # add one random (Pollice Verso)
    newGen.append(genToEvlutionare[4])

    return newGen


### Mutation ###

def mutate(comp):
    numMut = rand.randrange(chord_num // 2, chord_num, 1)
    newComplement = comp

    for a in range(numMut):
        position = rand.randrange(0, chord_num, 1)
        temp = list()
        temp.append(used_notes[rand.randrange(0, 8, 1)])
        temp.append(used_notes[rand.randrange(0, 8, 1)])
        temp.append(used_notes[rand.randrange(0, 8, 1)])

        newComplement[position] = temp

    return newComplement


### Crossover ###

def crossover(complement1, complement2):
    ind1 = rand.randrange(0, chord_num - 1, 1)
    ind2 = rand.randrange(ind1, chord_num, 1)

    if (not (ind1 + 1 < ind2)):
        ind1 = 0
        ind2 = chord_num // 2

    for a in range(ind1, ind2):
        cut = complement1[a]
        complement1[a] = complement2[a]
        complement2[a] = cut

    return complement1


########################### Terra Ludorum ##########################

lifeSpan = 100  # vita chrono

for v in range(lifeSpan):
    generation = makingEvolution(generation)

##################### Unwrapping of the Cat ##################

bestSong = fitnessFunction(generation)[0]

##################### Audiendo ad Musicam ####################

originalSong = mid  ## input file

track = mido.MidiTrack()

VELOCITY = 50
CHORD_TICKS = 768

for chord in bestSong:
    track.append(mido.Message('note_on', channel=0, note=chord[0], velocity=VELOCITY, time=0))
    track.append(mido.Message('note_on', channel=0, note=chord[1], velocity=VELOCITY, time=0))
    track.append(mido.Message('note_on', channel=0, note=chord[2], velocity=VELOCITY, time=0))

    track.append(mido.Message('note_off', channel=0, note=chord[0], velocity=VELOCITY, time=CHORD_TICKS))
    track.append(mido.Message('note_off', channel=0, note=chord[1], velocity=VELOCITY, time=0))
    track.append(mido.Message('note_off', channel=0, note=chord[2], velocity=VELOCITY, time=0))

mid.tracks.append(track)
mid.save(f'./midis/test.mid')

print("The song was successfully saved")