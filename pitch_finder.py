from scipy.fft import fft
from scipy.signal import find_peaks
from librosa import load
from numpy import argmax, abs, min
from math import log10
import re

def get_pitch(signal, sr):

    '''Computes pitch (Hz) of input signal using fft.
    \nsignal -> audio signal
    \nsr -> sample rate of audio signal'''

    N = 65536 #Number of fft points
    spectrum = fft(signal, N)
    spectrum = abs(spectrum)
    spectrum = spectrum/max(spectrum)
    peak_bins = find_peaks(abs(spectrum), height=.5)[0] #Find lowest peak
    peak_bin = min(peak_bins)
    peak_freq = peak_bin/N * sr
    return peak_freq
    


def pitch_to_note(fn):

    '''Converts pitch in Hz to note number with remainder
    \nfn -> pitch
    '''

    f0 = 440 #A below middle C 
    a = 2 ** (1/12)
    n = log10(fn/f0) / log10(a) + 69
    n  
    note = (n + 3) % 12
    rounded_note = round(note)
    delta = note - rounded_note
    return rounded_note, delta

def parse_filename(filename):

    '''Extracts note number from file name
    \nfilename -> filename string'''

    def pitch_to_num(pitch):
        return (pitch - 21)%12

    pitch = re.search('-...-', filename).group(0).replace('-','') #Find MIDI pitch number
    number = pitch_to_num(int(pitch)) #Convert to note number
    return number

def tuner(audio, sr):

    '''Computes note for audio, with error catching
    \naudio -> audio in form of numpy array
    \nsr -> audio sample rate'''

    try:
        pitch = get_pitch(audio, sr)
        note, delta = pitch_to_note(pitch)
        return note, delta
    except ValueError:
        return None

if __name__ == '__main__':

    from os import listdir

    sr = 44100
    test_file_dir = "Train Files"
    test_files = [filename for filename in listdir(test_file_dir) if '.wav' in filename]
    passed = 0
    failed = 0
    unknown = 0
    for filename in test_files[:1000]:
        audio = load(test_file_dir + "/" + filename, sr=sr)[0]
        target_note = parse_filename(filename)
        try:
            pitch = get_pitch(audio, sr)
            predicted_note = pitch_to_note(pitch)[0]
            if target_note == predicted_note: #Pass
                passed += 1
                print("Passed!")
            else: #Fail
                failed += 1
                print("Failed: predicted=%s actual=%s ........ %s" % (predicted_note, target_note, filename))
        except ValueError:
            unknown += 1
            print("No peaks for file %s" % filename)
    
    print("-"*50)
    print("Final score: %s passed, %s failed, %s unknown, accuracy = %.2f%%" % (passed, failed, unknown, (100 * passed/(passed+failed+unknown))))
    print("-"*50)