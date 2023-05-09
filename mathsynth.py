
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
    [sg.Combo(['Sine','Triangle', 'Square', 'Sawtooth', 'Custom'], default_value="Sine", key='-WAVEFORM-',enable_events=True)],
    [sg.Text("Enter a custom function here",visible=False,key="-CUSTOMTIP1-")],
    [sg.Text("freq=freq, amp = amplitude , phase= phase",visible=False, key="-CUSTOMTIP2-")],
    [sg.InputText("amp*math.sin(2*math.pi*freq*i/sample_rate)", key="-CUSTOM-",visible=False)],
    [sg.Text("Frequency")],
    [sg.Slider(range=(125, 4000), key='-FREQUENCY-', orientation='h')],
    [sg.Text("Amplitude")],
    [sg.Slider(range=(1, 100), key='-AMPLITUDE-', orientation='h', default_value=50)],
    [sg.Text("Phase")],
    [sg.Slider(range=(0, 4), key='-PHASE-', orientation='h')],
    [sg.Text("Duration of play")],
    [sg.Slider(range=(1, 5), key='-DURATION-', orientation='h')],
    [sg.Button('Start'),sg.Button('Generate Graph'), sg.Text("ready",key='-LOG-')],
    [sg.Button('<', pad=0),sg.Button('>', pad=0),sg.Button('C', pad=0),sg.Button('D', pad=0),sg.Button('E', pad=0),sg.Button('F', pad=0),sg.Button('G', pad=0),sg.Button('A', pad=0),sg.Button('B', pad=0)],
    [sg.Text("Octave = 4", key='-OCTAVE-')]
]




# Define the parameters of the audio file
frequency = 440  # Hz
duration = 1    # seconds
sample_rate = 44100
amplitude = 1.0
maxVolume = 32767
phase = 0.0
windowWaveNumber = 1
octave = 4
noteButtons = ['C','D', 'E', 'F', 'G', 'H', 'A', 'B']
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
    return amp*((freq/2*(i+phase)/sample_rate)%1)-0.5*amp
    

def triangleWAV(i, freq, amp, phase):
    result = 4*amp*(abs(((freq*(i+phase)/sample_rate)%1)-1/2)-1/4)
    return result
    
    
def soundFunction(i, freq, amp, phase, waveform, custom):
    match waveform:
        case "Sine":
            window['-LOG-'].update(value="Sine played at " + str(freq) + "hz!")
            return sineWAV(i, freq, amp, phase)
        case "Triangle":
            window['-LOG-'].update(value="Triangle played at " + str(freq) + "hz!")
            return triangleWAV(i, freq, amp, phase)
        case "Sqaure":
            window['-LOG-'].update(value="Square played at " + str(freq) + "hz!")
            return squareWAV(i, freq, amp, phase)
        case "Sawtooth":
            window['-LOG-'].update(value="Sawtooth played at " + str(freq) + "hz!")
            return sawtoothWAV(i, freq, amp, phase)
        case "Custom":
            try:
                window['-LOG-'].update(value="Custom played at " + str(freq) + "hz!")
                return eval(custom)
            except:
                window['-LOG-'].update(value="BAD FUNCTION, goodboy saw played")
                return sawtoothWAV(i, freq, amp, phase) 
        case _:
            return sineWAV(i, freq, amp, phase)
#checks if a note was pressed
def pianoHandler():
    if event == '<' or event == '>':
        global octave
        if event == '>' and octave < 7:
            octave = octave + 1    
        elif event == '<' and octave > 0:
            octave = octave - 1
        window['-OCTAVE-'].update(value="Octave = " + str(octave))



    if event in noteButtons:
        
        noteNum = getNoteNum(event)
        
        noteFreq = 16.35*(2**(1/12))**noteNum
        window['-FREQUENCY-'].update(value=noteFreq)
        


def getNoteNum(note):
    
    noteMap = { 
        "C" : 0,
        "D" : 2,
        "E" : 4,
        "F" : 5,
        "G" : 7,
        "A" : 9,
        "B" : 11,
    }
    return noteMap[note]+12*octave
    
        
    

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
    ax2.set_xlim(0,2*windowWaveNumber*2*sample_rate/frequency)

    # Adjust the spacing between the subplots
    plt.subplots_adjust(wspace=0.4)

    # Show the figure
    plt.show()
       # Define the function that generates the waveform
def generate_waveform(duration, sample_rate):
            num_samples = int(sample_rate * duration)
            data = []
            for i in range(num_samples):
                sample = soundFunction(i, freq, amp, phase, waveform, custom ) * maxVolume
                data.append(int(sample))
            return data


# Create the window
window = sg.Window('Waveform Selector', layout,background_color="thistle")
#program event loop
while True:
    event, values = window.read()
    freq = values['-FREQUENCY-']
    amp = values['-AMPLITUDE-']/100
    phase = values['-PHASE-']
    custom = values['-CUSTOM-']
    duration = values['-DURATION-']
    waveform = values['-WAVEFORM-']
    # If user closes window or clicks 'Exit', exit the program
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
   
    #handles visibility of elements for use when custom is selected as waveform type
    if event == '-WAVEFORM-':
        if(waveform == "Custom"):  
            window['-CUSTOM-'].update(visible=True)
            window['-CUSTOMTIP1-'].update(visible=True)
            window['-CUSTOMTIP2-'].update(visible=True) 
        else:
            window['-CUSTOM-'].update(visible=False)
            window['-CUSTOMTIP1-'].update(visible=False)
            window['-CUSTOMTIP2-'].update(visible=False)

    # If user clicks 'start' start the calculations and waveform
    if event == 'Start':
        
 
       

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
    #handles generation of graph when button is pressed, checks if data is present to genreate    
    if event == 'Generate Graph':
        try:
             plotWaveform(data, audio_data)
        except:
            window['-LOG-'].update(value="No Data to Graph")
    
    
    pianoHandler()
        
        
    

        
# Close the window and exit the program
window.close()

















