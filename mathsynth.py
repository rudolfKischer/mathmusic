
import math
import wave
import struct
import pyaudio
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

# Define the parameters of the audio file
frequency = 440.0  # Hz
duration = 3.0    # seconds
sample_rate = 44100
amplitude = 1.0
maxVolume = 32767

def sinWAV(i, f, a):
    return a * math.sin(2.0 * math.pi * f * i / sample_rate)

def squareWAV(i, f, a):
    result = sinWAV(i, f, a)
    if result > 0:
        return a
    return -a

def soundFunction(i):
    return squareWAV(i, frequency, amplitude) * sinWAV(i, 0.5, amplitude) 

# Define the function that generates the waveform
def generate_waveform(duration, sample_rate):
    num_samples = int(sample_rate * duration)
    data = []
    for i in range(num_samples):
        sample = soundFunction(i) * maxVolume
        data.append(int(sample))
    return data

def plotWaveform(data, audio_data):

    # Convert the audio data to a numpy array
    audio_array = np.frombuffer(audio_data, dtype=np.int16)


    # Compute the spectrogram of the audio data
    frequencies, times, spectrogram = signal.spectrogram(audio_array, sample_rate)

    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Plot the spectrogram in the first subplot
    ax1.pcolormesh(times, frequencies, spectrogram)
    ax1.set_ylabel('Frequency (Hz)')
    ax1.set_xlabel('Time (s)')
    ax1.set_title('Spectrogram')

    # Plot a small portion of the waveform in the second subplot
    start_sample = 0
    end_sample = sample_rate * 3
    ax2.plot(data[start_sample:end_sample])
    ax2.set_xlabel('Time (samples)')
    ax2.set_ylabel('Amplitude')
    ax2.set_title('Zoomed waveform')

    # Adjust the spacing between the subplots
    plt.subplots_adjust(wspace=0.4)

    # Show the figure
    plt.show()



# Generate the waveform
data = generate_waveform(duration, sample_rate)

# Save the waveform to a WAV file
wave_file = wave.open('waveform.wav', 'w')
wave_file.setparams((1, 2, sample_rate, len(data), 'NONE', 'not compressed'))
for sample in data:
    wave_file.writeframes(struct.pack('h', sample))
wave_file.close()

audio_file = wave.open('waveform.wav', 'rb')
audio_data = audio_file.readframes(audio_file.getnframes())
audio_file.close()

plotWaveform(data, audio_data)

# Play the WAV file
audio_player = pyaudio.PyAudio()
stream = audio_player.open(format=audio_player.get_format_from_width(audio_file.getsampwidth()),
                           channels=audio_file.getnchannels(),
                           rate=audio_file.getframerate(),
                           output=True)
stream.write(audio_data)
stream.close()
audio_player.terminate()