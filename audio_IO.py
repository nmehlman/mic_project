import pyaudio
import wave

bit_depth = pyaudio.paInt16
chans = 1
sr = 44100
chunk = 4096
rec_len = 3
dev_idx = 1
output_file = 'test.wav'

audio = pyaudio.PyAudio()
stream = audio.open(format = bit_depth, rate = sr, channels = chans, input_device_index = dev_idx, input = True, frames_per_buffer=chunk)

input('Press any key to record.')
print("recording")
frames = []

# loop through stream and append audio chunks to frame array
for ii in range(0,int((sr/chunk)*rec_len)):
    data = stream.read(chunk)
    frames.append(data)


print("finished recording")

# stop the stream, close it, and terminate the pyaudio instantiation
stream.stop_stream()
stream.close()
audio.terminate()

# save the audio frames as .wav file
wavefile = wave.open(output_file,'wb')
wavefile.setnchannels(chans)
wavefile.setsampwidth(audio.get_sample_size(bit_depth))
wavefile.setframerate(sr)
wavefile.writeframes(b''.join(frames))
wavefile.close()