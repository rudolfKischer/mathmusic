
from waves import (
     sineWAV, 
     squareWAV, 
     sawtoothWAV, 
     triangleWAV, 
     avg_all_WAV, 
     getFrequencyOffset, 
     get_oscillator_sound_function, 
     circleWAV, 
     noiseWAV,
     staircaseWAVE,
     sharktoothWAV
     )
from visualizer import draw_visualizer, draw_all_visualizer_segs
from audio import create_audio_callback
import pyaudio
import PySimpleGUI as sg
import pynput
import colorsys
import numpy as np
#add color list

# Define the layout of the GUI

VISUALIZER_HEIGHT = 240
VISUALIZER_WIDTH = 240
LFOList = ['amplitude','frequency'] 
layout = [

    [sg.Text("     Fine    Course   Oct        Amp      Phase",background_color="grey10")],
    [
     sg.Slider(range=(0, 100), key='-FINEFREQUENCY-', orientation='v', enable_events=True ,default_value=0,resolution=1,trough_color= '#6a938b',background_color="grey10",expand_y=True), 
     sg.Slider(range=(0, 12), key='-FREQUENCY-', orientation='v', enable_events=True ,default_value=0,resolution=1,trough_color= '#8cb596',background_color="grey10",expand_y=True),
     sg.Slider(range=(-3, 3), key='-PITCHOCTAVE-', orientation='v', enable_events=True ,default_value=0,resolution=1, trough_color = "#f0c1aa",background_color='grey10',expand_y=True),
     sg.Slider(range=(1, 100), key='-AMPLITUDE-', orientation='v', default_value=50, enable_events=True, trough_color = "#faf6d7",background_color='grey10',expand_y=True),
     sg.Slider(range=(0, 100), key='-PHASE-', orientation='v', enable_events= True, trough_color = "#c8a67c",background_color='grey10',expand_y=True),
     sg.Column([[sg.Text("currentOsci : " , key = '-currentOsci-')]], key= '-osciBank-', element_justification = "center"),
     sg.Graph((1.5*VISUALIZER_WIDTH, VISUALIZER_HEIGHT), (0, 0), (1.5*VISUALIZER_WIDTH, VISUALIZER_HEIGHT), key="-SUBGRAPHS-", background_color='black')
     ],
    [sg.Button('Start'),sg.Button('addOscilator',key= "-addOscillator-"),
     sg.Combo(['Sine','Triangle', 'Square', 'Sawtooth', 'Circle', 'Noise', 'staircase', 'sharktooth'], default_value="Sine", key='-WAVEFORM-',enable_events=True)],
    [sg.Text("Keyboard Octave = 4", key='-OCTAVE-')],
    [sg.Text("Fine     Frequency        Amp      ",background_color="grey10")],
    [sg.Column([[sg.Slider(range=(0, 100), key='-LFO-FREQUENCY-FINE-', orientation='v', enable_events=True ,default_value=0,resolution=0.01,trough_color= '#8cb596',background_color="grey10",expand_y=True),
     sg.Slider(range=(0, 32), key='-LFO-FREQUENCY-', orientation='v', enable_events=True ,default_value=0,resolution=0.01,trough_color= '#8cb596',background_color="grey10",expand_y=True),
     sg.Slider(range=(0, 100), key='-LFO-AMPLITUDE-', orientation='v', default_value=50, resolution=0.01, enable_events=True, trough_color = "#faf6d7",background_color='grey10',expand_y=True),
     sg.Column([[sg.Text("current-LFO : " , key = '-current-LFO-')]], key= '-LFO-Bank-', element_justification = "center")],[sg.Button('addLFO',key= "-addLFO-"),
     sg.Combo(['Sine','Triangle', 'Square', 'Sawtooth', 'Circle', 'Noise', 'staircase', 'sharktooth'], default_value="Sine", key='-LFO-WAVEFORM-',enable_events=True),
     sg.Combo(LFOList, default_value="amplitude", key='-LFO-TARGET-ATTRIBUTE-',enable_events=True)]]),
     
     sg.Column([[     sg.Slider(range=(0, 100), key='-Envelope-Attack-', orientation='v', enable_events=True ,default_value=0,resolution=1,trough_color= '#8cb596',background_color="grey10",expand_y=True),
     sg.Slider(range=(0, 100), key='-Envelope-Decay-', orientation='v', enable_events=True ,default_value=0,resolution=1,trough_color= '#8cb596',background_color="grey10",expand_y=True),
     sg.Slider(range=(0, 100), key='-Envelope-Sustain', orientation='v', default_value=0, resolution=1, enable_events=True, trough_color = "#faf6d7",background_color='grey10',expand_y=True),
     sg.Slider(range=(0, 100), key='-Envelope-Release-', orientation='v', default_value=0, resolution=1, enable_events=True, trough_color = "#faf6d7",background_color='grey10',expand_y=True),
     sg.Column([[sg.Text("Current-Envelope : " , key = '-Current-Envelope-')]], key= '-Envelope-Bank-', element_justification = "center")],[     sg.Button('Add Envelope',key= "-Add-Envelope-"),
     sg.Combo(LFOList, default_value="amplitude", key='-ENVELOPE-TARGET-ATTRIBUTE-',enable_events=True)]])
     ],
    [sg.Text("Keyboard Octave = 4", key='-OCTAVE-')],
    [sg.Graph((1.5*VISUALIZER_WIDTH, VISUALIZER_HEIGHT), (0, 0), (1.5*VISUALIZER_WIDTH, VISUALIZER_HEIGHT), key="-GRAPH-", background_color='black'),
    sg.Column([
        [sg.Text("Volume"),sg.Text("Wave #"),sg.Text("Sample#")],
        [
            sg.Slider(range=(0, 0.5), key='-VOLUME-', orientation='v', resolution=0.0025, default_value=0.15),
            sg.Slider(range=(1, 60), key='-VNUMWAVES-', orientation='v', resolution=1, default_value=10),
            sg.Slider(range=(1, VISUALIZER_WIDTH), key='-VNUMSAMPLES-', orientation='v', resolution=1, default_value=200)
        ]
    ],background_color= "grey10")
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
modifyingLFO = None
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
masterAmplitude = 0.5
#sound functions

defaultLFO = {
      "frequency" : 10,
      "waveform" : triangleWAV,
      "amplitude" : 1.0,
      "target" : 0,
      "targetAttribute": 'amplitude',
      "modifiers":[
      ]
    }

defaultOscilattor = {
  "freqOffset" : 0,
  "phase" : 0,
  "amplitude" : 1.0,
  "waveform" : sineWAV,
  "modifiers": [
  ]
}

defualtEnvolope = {
    "attack" : 0,
    "decay"  : 0,
    "sustain" : 1,
    "release" : 1,
    "target" : 0,
    "targetAttribute": 'amplitude',
    "modifiers": [
         
    ]
    
}
LFO = {
}
Envelope = {
     
}

osci = {

}

waveStrToFnc = {
  "Sine"  : sineWAV,
  "Sawtooth" : sawtoothWAV,
  "Square" : squareWAV,
  "Triangle" : triangleWAV,
  "Circle" : circleWAV,
  "Noise" : noiseWAV,
  "staircase" : staircaseWAVE,
  "sharktooth" : sharktoothWAV
}
#lowPass Filter



fncToWaveStr = {value: key for key, value in waveStrToFnc.items()}
def resonant_lowpass_filter(signal, fs, cutoff_freq, resonance):
    # Normalize the cutoff frequency
    normalized_cutoff = 2 * cutoff_freq / fs

    # Calculate the filter coefficients
    omega_c = 2 * np.pi * normalized_cutoff
    a1 = np.exp(-omega_c)
    b0 = (1 - a1) * (resonance ** 2) / (1 + resonance ** 2)
    b1 = 2 * b0
    b2 = b0
    a2 = -2 * a1 * resonance ** 2 / (1 + resonance ** 2)

    # Apply the filter
    filtered_signal = np.zeros_like(signal)
    for n in range(2, len(signal)):
        filtered_signal[n] = (
            b0 * signal[n] +
            b1 * signal[n - 1] +
            b2 * signal[n - 2] -
            a1 * filtered_signal[n - 1] -
            a2 * filtered_signal[n - 2]
        )

    return filtered_signal
    
def soundFunction(i):
    if len(osci.keys()) == 0:
        return 0
    return masterAmplitude * avg_all_WAV(i,osci,frequency)
      
def get_longest_wave():
    longest = float('inf')
    longestWave = None
    for key in osci.keys():
        freq = osci[key]["freqOffset"]
        if freq < longest:
            longest = freq
            longestWave = key

    return longestWave
    
def on_press(key): 
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
    global octave
    def getNoteNumFromKey(key):
                return noteMap[key]+12*octave
    def sendNoteFromKeyBoard(key):
        if(getNoteNumFromKey != False):
            global frequency
            noteNum = getNoteNumFromKey(key)
            
            noteFreq = 16.35*(2**(1/12))**noteNum
            frequency = noteFreq
    try:
            if key.char in noteMap.keys(): 

                if noteMap[key.char] == "down":
                    octave = octave - 1
                   
                elif noteMap[key.char] == "up":
                     octave = octave + 1
                else:
                    sendNoteFromKeyBoard(key.char)
    except AttributeError:
            pass

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
                newHue = (lastHue + 0.05) % 1.0
                newRGBColor = colorsys.hsv_to_rgb(newHue,lastHSVColor[1],lastHSVColor[2] )
                newHexColor = '#%02x%02x%02x' % (
                int(newRGBColor[0] * 255),
                int(newRGBColor[1] * 255),
                int(newRGBColor[2] * 255)
                )
                return newHexColor


listener_thread = pynput.keyboard.Listener(on_press=on_press,suppress = True)
listener_thread.start()
# Create the window
window = sg.Window('Waveform Selector', layout,background_color="grey10")
graph = window['-GRAPH-']
graphs = window['-SUBGRAPHS-']

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

    masterAmplitude = values['-VOLUME-']

    if event == '-addLFO-':
        i = len(LFO) + 1
        modifyingLFO = i
        LFO[i] = dict(defaultLFO)
        window['-current-LFO-'].update(value = "currentLFO : " + str(i), background_color = 'grey10')
        new_row = [
                 sg.Text(f'LFO{i}',background_color= 'grey10'),
                 sg.Button('Mute',key=f'-muteLFO{i}-', button_color= 'grey10'),
                 sg.Button('Modify',key=f'-modifyLFO{i}-', button_color= 'grey10')]
        window.extend_layout(window['-LFO-Bank-'], [new_row])

    
    if event == '-Add-Envelope-':
        i = len(Envelope) + 1
        modifyingEnvelope = i
        Envelope[i] = dict(defualtEnvolope)
        window['-Current-Envelope-'].update(value = "currentEnvelope : " + str(i), background_color = 'grey10')
        new_row = [
                 sg.Text(f'Envelope{i}',background_color= 'grey10'),
                 sg.Button('Mute',key=f'-muteEnvelope{i}-', button_color= 'grey10'),
                 sg.Button('Modify',key=f'-modifyEnvelope{i}-', button_color= 'grey10')]
        window.extend_layout(window['-Envelope-Bank-'], [new_row])



    if modifyingLFO != None:
        if event == '-LFO-FREQUENCY-':
              LFO[modifyingLFO]["frequency"] = values['-LFO-FREQUENCY-']
        
        if event == '-LFO-FREQUENCY-FINE-':
            LFO[modifyingLFO]["frequency"] = values['-LFO-FREQUENCY-'] + values['-LFO-FREQUENCY-FINE-']/100
        
        if event == '-LFO-AMPLITUDE-':
            LFO[modifyingLFO]["amplitude"] = values['-LFO-AMPLITUDE-']/100
        
        if event == '-LFO-WAVEFORM-':
            LFO[modifyingLFO]["waveform"] =  waveStrToFnc[values['-LFO-WAVEFORM-']]
        
        if event == '-LFO-TARGET-ATTRIBUTE-':
            LFO[modifyingLFO]["targetAttribute"] = values['-LFO-TARGET-ATTRIBUTE-']

    for i in LFO.keys():
        if event == f'-modifyLFO{i}-':
             
            modifyingLFO = i
            window['-current-LFO-'].update(value = "currentLFO : " + str(i), background_color = 'grey10') 
            
            freq = LFO[modifyingLFO]["frequency"]

            window['-LFO-FREQUENCY-'].update(value= LFO[modifyingLFO]["frequency"])
            window['-LFO-FREQUENCY-FINE-'].update(value= (LFO[modifyingLFO]["frequency"] - (LFO[modifyingLFO]["frequency"]%1))*100)
            window['-LFO-AMPLITUDE-'].update(value= LFO[modifyingLFO]["amplitude"]*100)
            window['-LFO-WAVEFORM-'].update(value= fncToWaveStr[LFO[modifyingLFO]["waveform"]])
            window['-LFO-TARGET-ATTRIBUTE-'].update(value= LFO[modifyingLFO]["targetAttribute"])
            
    for i in Envelope.keys():
        if event == f'-modifyEnvelope{i}-':
             
            modifyingEnvelope = i
            window['-Current-Envelope-'].update(value = "current Envelope : " + str(i), background_color = 'grey10') 
            
          

            window['-Envelope-Attack-'].update(value= LFO[modifyingEnvelope]["Attack"])
            window['-Envelope-Decay-'].update(value= (LFO[modifyingEnvelope]["Sustain"]))
            window['-Envelope-Sustain-'].update(value= LFO[modifyingEnvelope]["Decay"])
            window['-Envelope-Release'].update(value= fncToWaveStr[LFO[modifyingEnvelope]["Release"]])
       
    

    if event == '-addOscillator-':
        oscillatorNumber += 1
 
        LFOList.append("osci" + str(oscillatorNumber - 1) + " Freq")
        LFOList.append("osci" + str(oscillatorNumber - 1) + " Amp")

        currentTarget = values['-LFO-TARGET-ATTRIBUTE-']
        window['-LFO-TARGET-ATTRIBUTE-'].update(value = currentTarget , values=LFOList)
      

   
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
  
    for iOscillator in osci.keys():
        
         osci[iOscillator]["modifiers"] = []
         for ilfo in LFO.keys():
                #should append only if apllies to current osci
                osci[iOscillator]["modifiers"].append(dict(LFO[ilfo]))
              
              

    for i in osci.keys():
        if event == '-modify' + str(i) + "-": 
            
            modifyingOsci = i
           
            colorSet = osci[i]['color']
         
            
            window['-currentOsci-'].update(value = "currentOsci : " + str(i), background_color = colorSet)
            octaveNumber = (osci[modifyingOsci]["freqOffset"] - osci[modifyingOsci]["freqOffset"]%1200 )  /1200
            octaveDelta = octaveNumber*12
            fineFreqNumber = osci[modifyingOsci]["freqOffset"]%100
            #change values of sliders to mirror current oscilator
            window['-FINEFREQUENCY-'].update(value= fineFreqNumber)
            window['-FREQUENCY-'].update(value= (osci[modifyingOsci]["freqOffset"] - (osci[modifyingOsci]["freqOffset"]%100))/100 - octaveDelta)
            window['-PITCHOCTAVE-'].update(value= octaveNumber)
            window['-AMPLITUDE-'].update(value= osci[modifyingOsci]["amplitude"]*100)
            window['-PHASE-'].update(value= osci[modifyingOsci]["phase"])
            window['-WAVEFORM-'].update(value= fncToWaveStr[osci[modifyingOsci]["waveform"]])
        
        if event == '-FREQUENCY-' or event == '-PITCHOCTAVE-' or event == '-FINEFREQUENCY-':
             osci[modifyingOsci]["freqOffset"] = 100*values['-FREQUENCY-']  + 1200*values['-PITCHOCTAVE-'] + values['-FINEFREQUENCY-']
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

        draw_visualizer(graph, window_duration, visualizerPhase, v_num_of_samples, soundFunction, masterAmplitude)

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


