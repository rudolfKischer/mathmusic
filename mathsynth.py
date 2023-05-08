
import math
import wave
import struct
import pyaudio
import PySimpleGUI as sg
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

#GUI PARAMS
# Define the layout of the window
layout = [
    [sg.Text('Select a waveform:')],
    [sg.Combo(['Sine','Triangle', 'Square', 'Sawtooth', 'Custom'], default_value="Sine", key='-WAVEFORM-')],
    [sg.Text("Enter a custom function here")],
    [sg.Text("freq=freq, amp = amplitude , phase= phase")],
    [sg.InputText("math.sin(freq*i)", key="-CUSTOM-")],
    [sg.Text("Frequency")],
    [sg.Slider(range=(125, 4000), key='-FREQUENCY-', orientation='h')],
    [sg.Text("Amplitude")],
    [sg.Slider(range=(1, 100), key='-AMPLITUDE-', orientation='h', default_value=50)],
    [sg.Text("Phase")],
    [sg.Slider(range=(1, 4), key='-PHASE-', orientation='h')],
     [sg.Text("Duration of play")],
    [sg.Slider(range=(1, 5), key='-DURATION-', orientation='h')],
    [sg.Button('Start'), sg.Text("ready",key='-LOG-')]
]




# Define the parameters of the audio file
frequency = 440  # Hz
duration = 1    # seconds
sample_rate = 44100
amplitude = 1.0
maxVolume = 32767
phase = 0.0
windowWaveNumber = 1
#i is input, f is freuency, a is amplitude
def sineWAV(i, freq, amp, phase):
    return amp * math.sin(2.0 * math.pi * freq * (i + phase) / sample_rate)

def squareWAV(i, freq, amp, phase):
    result = sineWAV(i, freq, amp, phase)
    if result > 0:
        return amp
    return -amp
def sawtoothWAV(i, freq, amp , phase):
    #wouldint x = y mod frequencywork just as well?
    return (freq *(i + phase) / sample_rate)%amp - 0.5*amp

def triangleWAV(i, freq, amp, phase):
    result = sawtoothWAV(i, freq, amp , phase) 
    section = math.ceil((i/float(sample_rate))/(1/(2*freq))) 
    # print(section)
    if(section % 2 == 1):
        # print(result)
        return result 
    # print(-result)
    return -1*result 

def triangleWAV2(i, freq, amp, phase):
    result = 4*(abs(amp*((freq*i/sample_rate)%1)-amp/2)-amp/4)
    return result
    
def soundFunction(i, freq, amp, phase, waveform, custom):
    if(waveform == "Sine"):
        window['-LOG-'].update(value="Sine played at " + str(freq) + "hz!")
        return sineWAV(i, freq, amp, phase)
    if(waveform == "Triangle"):
        window['-LOG-'].update(value="Triangle played at " + str(freq) + "hz!")
        return triangleWAV2(i, freq, amp, phase)
    if(waveform == "Square"):
        window['-LOG-'].update(value="Square played at " + str(freq) + "hz!")
        return squareWAV(i, freq, amp, phase)
    if(waveform == "Sawtooth"):
        window['-LOG-'].update(value="Sawtooth played at " + str(freq) + "hz!")
        return sawtoothWAV(i, freq, amp, phase)
        
    if(waveform == 'Custom'):
        try:
            window['-LOG-'].update(value="Custom played at " + str(freq) + "hz!")
            return eval(custom)
        except:
            window['-LOG-'].update(value="BAD FUNCTION, goodboy saw played")
            return sawtoothWAV(i, freq, amp, phase) 
    return sineWAV(i, freq, amp, phase)





#program start
# Create the window
window = sg.Window('Waveform Selector', layout,background_color="thistle")

while True:
    event, values = window.read()
    freq = values['-FREQUENCY-']
    amp = values['-AMPLITUDE-']/100
    phase = values['-PHASE-']
    custom = values['-CUSTOM-']
    duration = values['-DURATION-']
    # If user closes window or clicks 'Exit', exit the program
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break

    # If user clicks 'start' start the calculations and waveform
    if event == 'Start':
        waveform = values['-WAVEFORM-']
        # Define the function that generates the waveform
        def generate_waveform(duration, sample_rate):
            num_samples = int(sample_rate * duration)
            data = []
            for i in range(num_samples):
                sample = soundFunction(i, freq, amp, phase, waveform, custom ) * maxVolume
                data.append(int(sample))
            return data




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


        # Play the WAV file
        audio_player = pyaudio.PyAudio()
        stream = audio_player.open(format=audio_player.get_format_from_width(audio_file.getsampwidth()),
                                channels=audio_file.getnchannels(),
                                rate=audio_file.getframerate(),
                                output=True)
        stream.write(audio_data)
        stream.close()
        audio_player.terminate()

        




# Close the window and exit the program
window.close()











#!!!!!!!!!!!!!!
# plotWaveform(data, audio_data)

#window plot ect
#!!!!!!!!!!!!!!!!!!
# def plotWaveform(data, audio_data):

#     # Convert the audio data to a numpy array
#     audio_array = np.frombuffer(audio_data, dtype=np.int16)


#     # Compute the spectrogram of the audio data
#     frequencies, times, spectrogram = signal.spectrogram(audio_array, sample_rate)

#     # Create a figure with two subplots
#     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

#     # Plot the spectrogram in the first subplot
#     ax1.pcolormesh(times, frequencies, spectrogram)
#     ax1.set_ylabel('Frequency (Hz)')
#     ax1.set_xlabel('Time (s)')
#     ax1.set_title('Spectrogram')

#     # Plot a small portion of the waveform in the second subplot
#     start_sample = 0
#     end_sample = sample_rate * 3
#     ax2.plot(data[start_sample:end_sample])
#     ax2.set_xlabel('Time (samples)')
#     ax2.set_ylabel('Amplitude')
#     ax2.set_title('Zoomed waveform')
#     ax2.set_xlim(0,2*windowWaveNumber*sample_rate/frequency)

#     # Adjust the spacing between the subplots
#     plt.subplots_adjust(wspace=0.4)

#     # Show the figure
#     plt.show()
