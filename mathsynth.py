
from waves import sineWAV, squareWAV, sawtoothWAV, triangleWAV, avg_all_WAV, getFrequencyOffset, get_oscillator_sound_function, circleWAV, noiseWAV
from visualizer import draw_visualizer, draw_all_visualizer_segs
from audio import create_audio_callback
import pyaudio
import PySimpleGUI as sg
import pynput
import colorsys
#add color list

# Define the layout of the GUI

VISUALIZER_HEIGHT = 240
VISUALIZER_WIDTH = 240

layout = [

    [sg.Text("Pitch"),sg.Text("Octave"),sg.Text("Amplitude"),sg.Text("Phase")],
    [sg.Slider(range=(0, 1200), key='-FREQUENCY-', orientation='v', enable_events=True ,default_value=0,resolution=100,trough_color= 'dark goldenrod',background_color="grey10"),
     sg.Slider(range=(-3, 3), key='-PITCHOCTAVE-', orientation='v', enable_events=True ,default_value=0,resolution=1, trough_color = "mediumorchid4",background_color='grey10'),
     sg.Slider(range=(1, 100), key='-AMPLITUDE-', orientation='v', default_value=50, enable_events=True, trough_color = "cyan4",background_color='grey10'),
     sg.Slider(range=(0, 100), key='-PHASE-', orientation='v', enable_events= True, trough_color = "firebrick4",background_color='grey10'),
     sg.Column([[sg.Text("currentOsci : " , key = '-currentOsci-')]], key= '-osciBank-')],
    [sg.Button('Start'),sg.Button('addOscilator',key= "-addOscillator-"),
     sg.Combo(['Sine','Triangle', 'Square', 'Sawtooth', 'Circle', 'Noise'], default_value="Sine", key='-WAVEFORM-',enable_events=True)],
    [sg.Text("Keyboard Octave = 4", key='-OCTAVE-')],
    [sg.Graph((1.5*VISUALIZER_WIDTH, VISUALIZER_HEIGHT), (0, 0), (1.5*VISUALIZER_WIDTH, VISUALIZER_HEIGHT), key="-SUBGRAPHS-", background_color='black'),
        sg.Graph((1.5*VISUALIZER_WIDTH, VISUALIZER_HEIGHT), (0, 0), (1.5*VISUALIZER_WIDTH, VISUALIZER_HEIGHT), key="-GRAPH-", background_color='black'),
    sg.Column([[sg.Text("Wave #"),sg.Text("Sample#")],
               [sg.Slider(range=(1, 60), key='-VNUMWAVES-', orientation='v', resolution=1, default_value=10),

                                                                          sg.Slider(range=(1, 4000), key='-VNUMSAMPLES-', orientation='v', resolution=1, default_value=200)]],background_color= "grey10")
    

    ],   
    [sg.Text("Visualizer Settings")],
    [sg.Text("wave speed"),sg.Slider(range=(0, 0.1), key='-VWAVESPEED-', orientation='h', resolution=0.001, default_value=0.01)]

]
#Variables for Sampling playing and graphic 
sample_width = 2 #bytes to represent sample
buffer_size = 1024
wave_pos = [0]
sample_rate = 44100
windowWaveNumber = 1
modifyingOsci = None
oscillatorNumber = 1
maxVolume = 32767
playingAudio = False
frequency = 440  # Hz
octave = 4

visualizerSamples = []
visualizerSamplesScale = 0.4 #percentage of samples to use for visualizer 0-1
visualizerFitWave = True
num_of_waves = 3
v_num_of_samples = 2000
visualizerPhase = 0.0
visualizer_speed = 1.0

#sound functions


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
  "Triangle" : triangleWAV,
  "Circle" : circleWAV,
  "Noise" : noiseWAV
}

fncToWaveStr = {value: key for key, value in waveStrToFnc.items()}


def soundFunction(i):
    if len(osci.keys()) == 0:
        return 0
    return avg_all_WAV(i,osci,frequency)



      
def get_longest_wave():
    longest = float('-inf')
    longestWave = None
    for key in osci.keys():
        freq = osci[key]["freqOffset"]
        if freq > longest:
            longest = freq
            longestWave = key

    return longestWave
    

    

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
window = sg.Window('Waveform Selector', layout,background_color="grey10")
graph = window['-GRAPH-']
graphs = window['-SUBGRAPHS-']

def get_visualizer_duration():
    #get wavelength of longest wave
    longest_wave = get_longest_wave()
    wave_frequence = frequency
    if longest_wave:
      wave_frequence = frequency + getFrequencyOffset(osci[longest_wave]["freqOffset"], frequency)
    wavelength = (1.0/float(wave_frequence))

    # Calculate the window duration
    return wavelength * num_of_waves

def getNewColor():
        if len(osci.keys()) < 1:
                return "#a34b86"
        else:
                
                lastHexColor = osci[i-1]['color']
                    # Remove the '#' symbol from the hex color string
                lastHexColor = lastHexColor.lstrip('#')
                # Extract the red, green, and blue components from the hex color
                r = int(lastHexColor[0:2], 16)
                g = int(lastHexColor[2:4], 16)
                b = int(lastHexColor[4:6], 16)

                r /= 255.0
                g /= 255.0
                b /= 255.0
                lastHSVColor = colorsys.rgb_to_hsv(r, g, b)
                lastHue = lastHSVColor[0]
                newHue = (lastHue + 0.1) % 1.0
                newRGBColor = colorsys.hsv_to_rgb(newHue,lastHSVColor[1],lastHSVColor[2] )
                newHexColor = '#%02x%02x%02x' % (
                int(newRGBColor[0] * 255),
                int(newRGBColor[1] * 255),
                int(newRGBColor[2] * 255)
                )
                return newHexColor
#event loop
while True:
    
    event, values = window.read(timeout=0)
    window['-OCTAVE-'].update(value="Octave = " + str(octave))
    
        

   
    
    
    # If user closes window or clicks 'Exit', exit the program
    if event == sg.WINDOW_CLOSED or event == 'Exit' or None:
        break
    
    # visualizerSamplesScale = values['-VSCALE-']
    num_of_waves = values['-VNUMWAVES-']
    visualizer_speed = values['-VWAVESPEED-']
    v_num_of_samples = values['-VNUMSAMPLES-']
    

    if event == '-addOscillator-':
        oscillatorNumber += 1

   
    for i in range(1,oscillatorNumber):
        osciWAV = osci.get(i)

        if osciWAV == None:
            modifyingOsci = i
            colorSet = getNewColor()
            osci[i] = dict(defaultOscilattor)
            osci[i]['color'] = colorSet
            window['-currentOsci-'].update(value = "currentOsci : " + str(i), background_color = osci[i]['color'])
            new_row = [
                 sg.Text(f'Osci{i}',background_color= osci[i]['color']),
                 sg.Button('Mute',key=f'-muteOsci{i}-', button_color= osci[i]['color']),
                 sg.Button('Modify',key=f'-modify{i}-', button_color= osci[i]['color'])]
            window.extend_layout(window['-osciBank-'], [new_row],)



    for i in osci.keys():
        if event == '-modify' + str(i) + "-": 
            
            modifyingOsci = i
           
            colorSet = osci[i]['color']
         
            
            window['-currentOsci-'].update(value = "currentOsci : " + str(i), background_color = colorSet)
            octaveNumber = (osci[modifyingOsci]["freqOffset"] - osci[modifyingOsci]["freqOffset"]%1200 )  /1200
            octaveDelta = octaveNumber*1200
            #change values of sliders to mirror current oscilator
            window['-FREQUENCY-'].update(value= osci[modifyingOsci]["freqOffset"] - octaveDelta)
            window['-PITCHOCTAVE-'].update(value= octaveNumber)
            window['-AMPLITUDE-'].update(value= osci[modifyingOsci]["amplitude"]*100)
            window['-PHASE-'].update(value= osci[modifyingOsci]["phase"])

        if event == '-FREQUENCY-' or event == '-PITCHOCTAVE-':
             osci[modifyingOsci]["freqOffset"] = values['-FREQUENCY-']+1200*values['-PITCHOCTAVE-']
        if event == '-AMPLITUDE-':   
            osci[modifyingOsci]["amplitude"] = values['-AMPLITUDE-']/100
        if event == '-PHASE-':
            osci[modifyingOsci]["phase"] = values['-PHASE-']
        if event == '-WAVEFORM-':
            osci[modifyingOsci]["waveform"] =  waveStrToFnc[values['-WAVEFORM-']]
        
    #handles the graphing of the waveform
    if playingAudio:

        window_duration = get_visualizer_duration()
        
        # Update the visualizer phase for wave speeed
        visualizerPhase = visualizerPhase + window_duration * visualizer_speed

        draw_visualizer(graph, window_duration, visualizerPhase, v_num_of_samples, soundFunction)

        draw_all_visualizer_segs(graphs, window_duration, visualizerPhase, v_num_of_samples, osci, frequency)
            

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
                                stream_callback=create_audio_callback(soundFunction, sample_rate, maxVolume, wave_pos))
            stream.start_stream()
        else:
            stream.stop_stream()
            stream.close()
            audio_player.terminate()
            

    
    
    

        
        
    

        
# Close the window and exit the program
window.close()
pynput.keyboard.Listener.stop(self = listener_thread)


