
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
import pynput


# Define the layout of the GUI

layout = [
    
    [sg.Text('Select a waveform:'),
     sg.Column([], key= '-osciBank-')],

    [sg.Combo(['Sine','Triangle', 'Square', 'Sawtooth'], default_value="Sine", key='-WAVEFORM-',enable_events=True)],
    [sg.Text("currentOsci : " , key = '-currentOsci-')],

    [sg.Text("Pitch")],
    [sg.Slider(range=(-1200, 1200), key='-FREQUENCY-', orientation='h', enable_events=True ,default_value=0,resolution=100)],
    [sg.Text("Amplitude")],
    [sg.Slider(range=(1, 100), key='-AMPLITUDE-', orientation='h', default_value=50, enable_events=True)],
    [sg.Text("Phase")],
    [sg.Slider(range=(0, 100), key='-PHASE-', orientation='h', enable_events= True)],
    [sg.Button('Start')],
    [sg.Text("Octave = 4", key='-OCTAVE-')],
    [sg.Button('addOscilator',key= "-addOscillator-")],
    [sg.Graph((640, 480), (0, 0), (640, 480), key="-GRAPH-", background_color='black')]    
]
#Variables for Sampling playing and graphic 

prevTime = time.time()
sample_width = 2
buffer_size = 1024
wave_pos = 0
duration = 1    # seconds
sample_rate = 44100
windowWaveNumber = 1
modifyingOsci = None
oscillatorNumber = 1
maxVolume = 32767
playingAudio = False
visualizerSamples = []
visualizerSampleLength = 1 #seconds
visualizerPhase = 0
frequency = 440  # Hz
octave = 4

#sound functions
def sineWAV(i, freq, amp):
    return amp * math.sin(2.0 * math.pi * freq * i)

def squareWAV(i, freq, amp):
    result = sineWAV(i, freq, amp)
    if result > 0:
        return amp
    return -amp
def sawtoothWAV(i, freq, amp):
    return amp*((freq/2*i)%1)-0.5*amp
def triangleWAV(i, freq, amp):
    result = 4*amp*(abs(((freq*i)%1)-1/2)-1/4)
    return result

defaultOscilattor = {
"freqOffset" : 0,
"phase" : 0,
"amplitude" : 0.5,
"waveform" : sineWAV
}

osci = {

}

waveStrToFnc = {
  "Sine"  : sineWAV,
  "Sawtooth" : sawtoothWAV,
  "Square" : squareWAV,
  "Triangle" : triangleWAV
}

fncToWaveStr = {value: key for key, value in waveStrToFnc.items()}



#variabe for what waveform is set
def getFrequencyOffset(cent,freq):
    
    freqOffset = freq*(2**(cent/1200))

   
    return freqOffset

def soundFunction(i):
    if len(osci.keys()) == 0:
        return 0
    totalSample = 0

    for modifyingOsci in osci.keys():
       oscillator = osci[modifyingOsci] 
       
       oscillatorFrequency = frequency + getFrequencyOffset(oscillator["freqOffset"], frequency)
       phaseOffset = (oscillator["phase"]/100)*frequency
       samplePoint =  (i + phaseOffset)/sample_rate
       sample = oscillator["waveform"](
                samplePoint,
                oscillatorFrequency,
                oscillator["amplitude"])
       totalSample = totalSample + sample
    return totalSample/(len(osci.keys()))

def soundCallBack(in_data, frame_count, time_info, status):
   
    global wave_pos
    global frequency, amplitude, phase
    global visualizerSamples

    buffer_end = wave_pos + frame_count
    out_data = b''
    tempVisual = []
    for i in range(wave_pos, buffer_end):


        sample = soundFunction(i)



        sample_data = struct.pack('h', int(sample * maxVolume))
        out_data += sample_data
        tempVisual.append(sample)
        
    visualizerSamples = tempVisual
    wave_pos = buffer_end
    return (out_data, pyaudio.paContinue)

        
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
#generates data from waveform equation   
def generate_waveform(duration, sample_rate):
            num_samples = int(sample_rate * duration)
            data = []
            for i in range(num_samples):
                sample = soundFunction(i, frequency, amplitude, phase) * maxVolume
                data.append(int(sample))
            return data
    

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
            "]" : 18,
            "z" : "down",
            "x" : "up"
        }

def on_press(key): 
            
    try:
            if key.char in noteMap.keys(): 

                if noteMap[key.char] == "down":
                    octaveChange(-1)
                   
                elif noteMap[key.char] == "up":
                    octaveChange(1)
                else:
                    sendNoteFromKeyBoard(key.char)

    except AttributeError:
            pass

listener_thread = pynput.keyboard.Listener(on_press=on_press,suppress = True)
listener_thread.start()


def sendNoteFromKeyBoard(key):
    global frequency
    def getNoteNumFromKey(key):
       

            return noteMap[key]+12*octave
    if(getNoteNumFromKey != False):
        
        noteNum = getNoteNumFromKey(key)
        
        noteFreq = 16.35*(2**(1/12))**noteNum
        frequency = noteFreq

# Call to change octave by x octaves
def octaveChange(x):
    global octave
    octave = octave + x


# Create the window
window = sg.Window('Waveform Selector', layout,background_color="thistle")
graph = window['-GRAPH-']

#event loop
while True:
    
    event, values = window.read(timeout=0)
    window['-OCTAVE-'].update(value="Octave = " + str(octave))
    
        

   
    
    
    # If user closes window or clicks 'Exit', exit the program
    if event == sg.WINDOW_CLOSED or event == 'Exit' or None:
        break
    

    if event == '-addOscillator-':
        oscillatorNumber += 1

   
    for i in range(1,oscillatorNumber):
        osciWAV = osci.get(i)
        
        if osciWAV ==None:
            modifyingOsci = i
            window['-currentOsci-'].update(value = "currentOsci : " + str(i))
            osci[i] = dict(defaultOscilattor)
            new_row = [sg.Text(f'Osci{i}'),sg.Button('Mute',key=f'-muteOsci{i}-'),sg.Button('Modify',key=f'-modify{i}-')]
            window.extend_layout(window['-osciBank-'], [new_row])


    
    for i in osci.keys():
        if event == '-modify' + str(i) + "-": 
            modifyingOsci = i
            window['-currentOsci-'].update(value = "currentOsci : " + str(i))

            #change values of sliders to mirror current oscilator
            window['-FREQUENCY-'].update(value= osci[modifyingOsci]["freqOffset"])
            window['-AMPLITUDE-'].update(value= osci[modifyingOsci]["amplitude"]*100)
            window['-PHASE-'].update(value= osci[modifyingOsci]["phase"])
        
        if event == '-FREQUENCY-':
             osci[modifyingOsci]["freqOffset"] = values['-FREQUENCY-']
        if event == '-AMPLITUDE-':   
            osci[modifyingOsci]["amplitude"] = values['-AMPLITUDE-']/100
        if event == '-PHASE-':
            osci[modifyingOsci]["phase"] = values['-PHASE-']
        if event == '-WAVEFORM-':
            osci[modifyingOsci]["waveform"] =  waveStrToFnc[values['-WAVEFORM-']]
    
        


  
   

    
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
            

    
    
    

        
        
    

        
# Close the window and exit the program
window.close()
pynput.keyboard.Listener.stop(self = listener_thread)


