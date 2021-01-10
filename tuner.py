import tensorflow as tf
from tensorflow.keras.layers import Input, Conv2D, MaxPool2D, Flatten, Dense, Reshape
from tensorflow.keras.models import Model
import librosa as lib
from librosa import load
from librosa.feature import spectral_centroid, chroma_stft, rms
import numpy as np
import matplotlib.pyplot as plt
from os import listdir, mkdir
from os.path import isdir
import re
import pickle
from utility import time_str

###      **** GLOBALS ****      ###

n_chroma = 36 #Number of spectrogram bins
T = 16000 #Length of training interval
thr = -50 #Triggering threshold
hop_len = 512 #Hope between STFT frames
sr = 16000 #Sample Rate
eps = 1e-8 #Small number to avoid log(0)

##################################

class PitchDetector:

    '''NN model to detect signal pitch.'''

    def __init__(self, sr, load_path=None):

        self.sr = sr

        i = Input(shape=(n_chroma, T//hop_len+1))
        x = Reshape((n_chroma, T//hop_len+1, 1))(i)
        x  = Conv2D(64, 4, activation='relu')(x)
        x = MaxPool2D()(x)
        x  = Conv2D(128, 4, activation='relu')(x)
        x = Flatten()(x)
        x = Dense(12, activation='softmax')(x)

        if load_path: self.model = tf.keras.models.load_model(load_path, compile=False)
        else: self.model = Model(i,x)
        
        self.model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')

    def STFT(self, audio):

        '''Computes STFT of audio signal
        \naudio -> mono audio signal in form of numpy array'''

        audio = self._make_mono(audio)
        stft = chroma_stft(audio, sr=self.sr, n_chroma=n_chroma, hop_length=hop_len)
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
        
    def _truncate_audio(self, audio):

        '''Truncates audio to desired length using a triggering threshold
        \naudio -> mone audio signal'''

        if len(audio) < T: raise ValueError('audio too short')
        frame_len = 2048
        level = 20*np.log10( rms(audio, frame_length=frame_len) +  eps)[0]
        start_idx = 0
        while level[start_idx] < thr: start_idx += 1 #Find onset
        start_idx *= frame_len #Convert to sample
        if start_idx+T >= len(audio): start_idx = len(audio) - (T+1) #Ensure sufficient length
        return audio[frame_len : frame_len+T]

    def _generate_training_data(self, audio_files, save_path=None):
        
        '''Generates training data from list of files
        \naudio_files -> list of training files
        \nsave_path -> location to save converted dataset'''

        train_data = []
        targets = []
        for file_path in audio_files:
            audio = load(file_path, sr=self.sr, mono=False)[0]
            audio = self._make_mono(audio)
            audio = self._truncate_audio(audio)
            stft = self.STFT(audio)
            train_data.append(stft)
            targets.append(self._parse_filename(file_path))
        
        if save_path:
            pickle.dump(np.array(train_data), open(save_path + "/train", 'wb'))
            pickle.dump(np.array(targets), open(save_path + "/targets", 'wb'))
        return np.array(train_data), np.array(targets)
   
    @staticmethod
    def _parse_filename(filename):

        '''Extracts note number from file name
        \nfilename -> filename string'''

        def pitch_to_num(pitch):
            return (pitch - 21)%12

        pitch = re.search('-...-', filename).group(0).replace('-','') #Find MIDI pitch number
        number = pitch_to_num(int(pitch)) #Convert to note number
        return number

    def train_on_files(self, folder, epochs, save_path=None):

        '''Train model from audio files in folder
        \nfolder -> folder path containing training files
        \nepochs -> number of training epochs
        \nsave_path -> location to saved converted dataset'''

        audio_files = [folder + '/' + file_path for file_path in listdir(folder) if '.wav' in file_path] #Find audio files
        train_data, targets = self._generate_training_data(audio_files, save_path=save_path) #Produce training set
        self.model.fit(train_data, targets, epochs=epochs)

    def train_on_dataset(self, dataset_path, epochs):

        '''Train model from converted dataset
        \ndataset_path -> folder path containing training dataset
        \nepochs -> number of training epochs'''

        train_data = pickle.load(open(dataset_path + "/train", 'rb'))
        targets = pickle.load(open(dataset_path + "/targets", 'rb'))
        self.model.fit(train_data, targets, epochs=epochs)
           
    def predict_pitch(self, audio):

        '''Predicts pitch of particular audio instance.
        \naudio -> audio in form of numpy array'''

        audio = self._truncate_audio(self._make_mono(audio))
        stft = self.STFT(audio)
        stft = np.expand_dims(stft, 0)
        logits = self.model.predict(stft)[0]
        return np.argmax(logits), logits
    
    def save_model(self, save_path):
        full_path = save_path + time_str(sec=False, year=False, isPath=True)
        if not isdir(full_path): mkdir(full_path)
        tf.keras.models.save_model(self.model, full_path)  
        
if __name__ == '__main__':

    detector = PitchDetector(sr)
    detector.train_on_files('Train Files', 50, 'Saved Models')
    
    
