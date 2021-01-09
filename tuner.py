import tensorflow as tf
from tensorflow.keras.layers import Input, Conv2D, MaxPool2D, Flatten, Dense, Reshape
from tensorflow.keras.models import Model
import librosa as lib
from librosa import load
from librosa.feature import spectral_centroid, chroma_stft, rms
import numpy as np
import matplotlib.pyplot as plt
from os import listdir
import re
import pickle

n_chroma = 36 #Number of spectrogram bins
T = 44100 #Length of training interval
thr = -50
hop_len = 512

class PitchDetector:

    '''NN model to detect signal pitch.'''

    def __init__(self, n_chroma, T, hop_len):

        self.n_chroma = n_chroma
        self.T = T
        self.hop_len = hop_len

        i = Input(shape=(n_chroma, T//hop_len+1))
        x = Reshape((n_chroma, T//hop_len+1, 1))(i)
        x  = Conv2D(64, 4, activation='relu')(x)
        x = MaxPool2D()(x)
        x  = Conv2D(128, 4, activation='relu')(x)
        x = Flatten()(x)
        x = Dense(12, activation='softmax')(x)

        self.model = Model(i,x)
        self.model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')

    def STFT(self, audio, sr=44100):

        '''Computes STFT of audio signal
        \naudio -> mono audio signal in form of numpy array
        \nsr -> sample rate'''

        audio = self._make_mono(audio)
        stft = chroma_stft(audio, sr, n_chroma=self.n_chroma, hop_length=self.hop_len)
        return stft

    @staticmethod
    def _make_mono(audio):

        '''Converts stereo audio to mono if required
        \naudio -> audio signal in form of numpy array with shape (n,) or (2,).'''

        if audio.ndim == 2:
            mono_audio = 1/2*(audio[0,:] + audio[1,:])
        elif audio.ndim == 1:
            mono_audio = audio
        else:
            raise AttributeError('invalid audio signal shape')
        return mono_audio
        
    def _truncate_audio(self, audio, thr):

        '''Truncates audio to desired length using a triggering threshold
        \naudio -> mone audio signal
        \nthr -> triggering threshold (dB)'''

        if len(audio) < T: raise ValueError('audio too short')
        frame_len = 2048
        level = 20*np.log10( rms(audio, frame_length=frame_len) )[0]
        start_idx = 0
        while level[start_idx] < thr: start_idx += 1 #Find onset
        start_idx *= frame_len
        return audio[frame_len : frame_len+self.T]

    def _generate_training_data(self, audio_files, thr, T, n_chroma, save_path=None):
        
        '''Generates training data from list of files
        \naudio_files -> list of training files
        \nthr -> triggering threshold (dB)'''

        train_data = []
        targets = []
        for file_path in audio_files:
            audio = load(file_path, sr=44100, mono=False)[0]
            audio = self._make_mono(audio)
            audio = self._truncate_audio(audio, thr)
            stft = self.STFT(audio, sr=44100)
            train_data.append(stft)
            targets.append(self._parse_filename(file_path))
        
        if save_path:
            pickle.dump(np.array(train_data), open(save_path+"/train", 'w'))
            pickle.dump(np.array(targets), open(save_path+"/targets", 'w'))
        return np.array(train_data), np.array(targets)

    def train(self, folder, thr, epochs):

        '''Train model from dataset in folder
        \nfolder -> folder path containing training dataset
        \nthr -> triggering threshold (dB
        \nepochs -> number of training epochs'''

        audio_files = [folder + '/' + file_path for file_path in listdir(folder) if '.wav' in file_path]
        train_data, targets = self._generate_training_data(audio_files, thr, self.T, self.n_chroma, "Processed Datasets")
        self.model.fit(train_data, targets, epochs=epochs)
        
    @staticmethod
    def _parse_filename(filename):

        '''Extracts note number from file name
        \nfilename -> filename string'''

        def pitch_to_num(pitch):
            return (pitch - 21)%12

        pitch = re.search('-...-', filename).group(0).replace('-','') #Find MIDI pitch number
        number = pitch_to_num(int(pitch)) #Convert to note number
        return number

        
        
if __name__ == '__main__':

    detector = PitchDetector(n_chroma, T, hop_len)
    #audio = load('Test Files/piano.wav', sr=44100, mono=False)[0]
    #audio = detector._make_mono(audio)
    #audio = detector._truncate_audio(audio,-20,T)
    detector.train('Train Files', thr, 100)
