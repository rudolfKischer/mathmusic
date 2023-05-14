
import math
import wave
import struct
import pyaudio
import PySimpleGUI as sg
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import time
import matplotlib.pyplot as plt
import keyboard

#GUI PARAMS
# Define the layout of the window
layout = [
    [sg.Text('Select a waveform:')],
    [sg.Combo(['Sine','Triangle', 'Square', 'Sawtooth', 'Custom'], default_value="Sine", key='-WAVEFORM-',enable_events=True)],
    [sg.Text("Enter a custom function here",visible=False,key="-CUSTOMTIP1-")],
    [sg.Text("freq=freq, amp = amplitude , phase= phase",visible=False, key="-CUSTOMTIP2-")],
    [sg.InputText("amp*math.sin(2*math.pi*freq*i/sample_rate)", key="-CUSTOM-",visible=False)],
    [sg.Text("Frequency")],
    [sg.Slider(range=(125, 20000), key='-FREQUENCY-', orientation='h', enable_events=True)],
    [sg.Text("Amplitude")],
    [sg.Slider(range=(1, 100), key='-AMPLITUDE-', orientation='h', default_value=50, enable_events=True)],
    [sg.Text("Phase")],
    [sg.Slider(range=(0, 4), key='-PHASE-', orientation='h')],
    [sg.Button('Start'),sg.Button('Generate Graph'), sg.Text("ready",key='-LOG-')],
    [sg.Button('<', pad=0, button_color="black"),sg.Button('>', pad=0,button_color="black"),sg.Button('C', pad=0,button_color="bisque"),sg.Button('D', pad=0,button_color="bisque"),sg.Button('E', pad=0,button_color="bisque"),
    sg.Button('F', pad=0,button_color="bisque"),sg.Button('G', pad=0,button_color="bisque"),sg.Button('A', pad=0,button_color="bisque"),sg.Button('B', pad=0,button_color="bisque")],
    [sg.Text("Octave = 4", key='-OCTAVE-')],
    [sg.Graph((640, 480), (0, 0), (640, 480), key="-GRAPH-", background_color='black')],
]




# Define the parameters of the audio file
prevTime = time.time()
sample_width = 2
buffer_size = 1024
wave_pos = 0

playingAudio = False


visualizerSamples = []
visualizerSampleLength = 1 #secons
visualizerPhase = 0

frequency = 440  # Hz
duration = 1    # seconds
sample_rate = 44100
amplitude = 1.0
maxVolume = 32767
phase = 0.0
windowWaveNumber = 1
masterSoundFunction = None
customFunctionString = "amp*math.sin(2*math.pi*freq*i/sample_rate)"
octave = 4
noteButtons = ['C','D', 'E', 'F', 'G', 'H', 'A', 'B']
#i is input, f is freuency, a is amplitude
def sineWAV(i, freq, amp, phase):
    return amp * math.sin(2.0 * math.pi * freq * i)

def squareWAV(i, freq, amp, phase):
    result = sineWAV(i, freq, amp, phase)
    if result > 0:
        return amp
    return -amp
def sawtoothWAV(i, freq, amp , phase):
    #wouldint x = y mod frequencywork just as well?
<<<<<<< HEAD
    return 2*amp*((freq/2*(i+phase)/sample_rate)%1)-amp
=======
    return amp*((freq/2*i)%1)-0.5*amp
>>>>>>> e26a2272fcd1c8f0979d3baa220ab4abac6c939a
def triangleWAV(i, freq, amp, phase):
    result = 4*amp*(abs(((freq*i)%1)-1/2)-1/4)
    return result

def customWAV(i, freq, amp, phase):
    try:
        return eval(customFunctionString)
    except:
        window['-LOG-'].update(value="BAD FUNCTION, goodboy saw played")
        return sawtoothWAV(i, freq, amp, phase)
    
soundFunctions = {
    "Sine": sineWAV,
    "Square": squareWAV,
    "Sawtooth": sawtoothWAV,
    "Triangle": triangleWAV,
    "Custom": customWAV
}
masterSoundFunction = soundFunctions["Sine"]

def soundFunction(i, freq, amp, phase):
    x = (i + phase) / sample_rate
    return masterSoundFunction(x, freq, amp, phase)
        
def soundCallBack(in_data, frame_count, time_info, status):
    global wave_pos
    global frequency, amplitude, phase
    global visualizerSamples

    buffer_end = wave_pos + frame_count
    out_data = b''
    visualizerSamples = []
    for i in range(wave_pos, buffer_end):
        sample = soundFunction(i, frequency, amplitude, phase)
        sample_data = struct.pack('h', int(sample * maxVolume))
        out_data += sample_data
        visualizerSamples.append(sample)
    
    wave_pos = buffer_end
    return (out_data, pyaudio.paContinue)
#checks if a note was pressed
def pianoHandler():
    if event == '<' or event == '>':
        global octave
        if event == '>' and octave < 10:
            octave = octave + 1    
        elif event == '<' and octave > 0:
            octave = octave - 1
        



    if event in noteButtons:
        
        noteNum = getNoteNumFromButton(event)
        
        noteFreq = 16.35*(2**(1/12))**noteNum
        window['-FREQUENCY-'].update(value=noteFreq)
        


def getNoteNumFromButton(note):
    
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

def draw_visualizer_line(graph, start, end):
        # Convert the start and end points to numpy arrays
    start = np.array(start)
    end = np.array(end)

    # Calculate the direction vector of the line
    direction = end - start

    # Normalize the direction vector
    norm = np.linalg.norm(direction)
    if norm == 0:
        return
    direction /= norm

    # Extend the line by 10 pixels in its direction of travel
    extension = 5
    extended_end = end + extension * direction
    graph.draw_line(tuple(start), tuple(extended_end),color="green", width=5)
    


def generate_waveform(duration, sample_rate):
            num_samples = int(sample_rate * duration)
            data = []
            for i in range(num_samples):
                sample = soundFunction(i, frequency, amplitude, phase) * maxVolume
                data.append(int(sample))
            return data

def octaveChange(x):
    global octave
    octave = octave + x

    
# keyboard.on_press_key("a", lambda _:sendNoteFromKeyBoard("a"))
# keyboard.on_press_key("s", lambda _:sendNoteFromKeyBoard("s"))
# keyboard.on_press_key("d", lambda _:sendNoteFromKeyBoard("d"))
# keyboard.on_press_key("f", lambda _:sendNoteFromKeyBoard("f"))
# keyboard.on_press_key("g", lambda _:sendNoteFromKeyBoard("g"))
# keyboard.on_press_key("h", lambda _:sendNoteFromKeyBoard("h"))
# keyboard.on_press_key("j", lambda _:sendNoteFromKeyBoard("j"))
# keyboard.on_press_key("w", lambda _:sendNoteFromKeyBoard("w"))
# keyboard.on_press_key("e", lambda _:sendNoteFromKeyBoard("e"))
# keyboard.on_press_key("t", lambda _:sendNoteFromKeyBoard("t"))
# keyboard.on_press_key("y", lambda _:sendNoteFromKeyBoard("y"))
# keyboard.on_press_key("u", lambda _:sendNoteFromKeyBoard("u"))
# keyboard.on_press_key("k", lambda _:sendNoteFromKeyBoard("k"))
# keyboard.on_press_key("o", lambda _:sendNoteFromKeyBoard("o"))
# keyboard.on_press_key("l", lambda _:sendNoteFromKeyBoard("l"))
# keyboard.on_press_key("p", lambda _:sendNoteFromKeyBoard("p"))
# keyboard.on_press_key(";", lambda _:sendNoteFromKeyBoard(";"))
# keyboard.on_press_key("'", lambda _:sendNoteFromKeyBoard("'"))
# keyboard.on_press_key("]", lambda _:sendNoteFromKeyBoard("]"))
# keyboard.on_press_key("z", lambda _:octaveChange(-1))
# keyboard.on_press_key("x", lambda _:octaveChange(+1))

def sendNoteFromKeyBoard(key):
    global frequency
    noteNum = getNoteNumFromKey(key)
    
    noteFreq = 16.35*(2**(1/12))**noteNum
    frequency = noteFreq

def getNoteNumFromKey(key):
    
    noteMap = { 
        "a" : 0,
        "w" : 1,
        "s" : 2,
        "e" : 3,
        "d" : 4,
        "f" : 5,
        "t" : 6,
        "g" : 7,
        "y" : 8,
        "h" : 9,
        "u" : 10,
        "j" : 11,
        "k" : 12,
        "o" : 13,
        "l" : 14,
        "p" : 15,
        ";" : 16,
        "'" : 17,
        "]" : 18
    }
    
    return noteMap[key]+12*octave
    
def updateSlider(noteFreq):
    window['-FREQUENCY-'].update(value=noteFreq)

# Create the window
window = sg.Window('Waveform Selector', layout,background_color="thistle")
graph = window['-GRAPH-']



#program event loop
while True:
    event, values = window.read(timeout=0)
    window['-OCTAVE-'].update(value="Octave = " + str(octave))
    
    if event == '-FREQUENCY-':
        frequency = values['-FREQUENCY-']

    
    
    # If user closes window or clicks 'Exit', exit the program
    if event == sg.WINDOW_CLOSED or event == 'Exit' or None:
        break
    
    updateSlider(frequency)


    amplitude = values['-AMPLITUDE-']/100
    phase = values['-PHASE-']
    custom = values['-CUSTOM-']
    waveform = values['-WAVEFORM-']
   
    #handles visibility of elements for use when custom is selected as waveform type
    if event == '-WAVEFORM-':
        if(waveform == "Custom"): 
            customFunctionString = custom
            window['-CUSTOM-'].update(visible=True)
            window['-CUSTOMTIP1-'].update(visible=True)
            window['-CUSTOMTIP2-'].update(visible=True) 
        else:
            window['-CUSTOM-'].update(visible=False)
            window['-CUSTOMTIP1-'].update(visible=False)
            window['-CUSTOMTIP2-'].update(visible=False)
        window['-LOG-'].update(value=waveform + " played at " + str(frequency) + "hz!")
        masterSoundFunction = soundFunctions[waveform]
    
    #handles the graphing of the waveform

    if playingAudio:
        graph.erase()
        num_samples = len(visualizerSamples)
        for sample in range(1,num_samples-10):
            x1 = sample/num_samples * 640
            y1 = ((visualizerSamples[sample])) * 480 + 480/2
            x2 = (sample+1)/num_samples * 640
            y2 = ((visualizerSamples[sample+1])) * 480 + 480/2
            # print(f"({x1},{y1}),({x2},{y2})")
            draw_visualizer_line(graph, (x1,y1),(x2,y2))
            

    # If user clicks 'start' start the calculations and waveform
    if event == 'Start':
        
        playingAudio = not playingAudio
        if(playingAudio):
            # Play the WAV file
            audio_player = pyaudio.PyAudio()
            stream = audio_player.open(format=audio_player.get_format_from_width(sample_width),
                                channels=1,
                                rate=sample_rate,
                                input=True,
                                output=True,
                                frames_per_buffer=buffer_size,
                                stream_callback=soundCallBack)
            stream.start_stream()
        else:
            stream.stop_stream()
            stream.close()
            audio_player.terminate()
            

    #handles generation of graph when button is pressed, checks if data is present to genreate    
    if event == 'Generate Graph':        
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
        try:
             plotWaveform(data, audio_data)
        except:
            window['-LOG-'].update(value="No Data to Graph")
    
    
    pianoHandler()
        
        
    

        
# Close the window and exit the program
window.close()


