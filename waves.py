from math import sin, pi, sqrt, floor
from random import random

def getFrequencyOffset(cent,freq):
    
    freqOffset = freq*(2**(cent/1200))
    return freqOffset

def noiseWAV(i, freq, amp):
    return amp * (2.0 * random() - 1.0)

def sineWAV(i, freq, amp):
    return amp * sin(2.0 * pi * freq * i)

def squareWAV(i, freq, amp):
    result = sineWAV(i, freq, amp)
    if result > 0:
        return amp
    return -amp

def sawtoothWAV(i, freq, amp):
    return 2 * amp*(((freq*i)%1)-0.5)

def sharktoothWAV(i, freq, amp):
    return 2 * amp*(1-((freq*i)%1) - 0.5)

def triangleWAV(i, freq, amp):
    result = 4*amp*(abs(((freq*i)%1)-1/2)-1/4)
    return result

def staircaseWAVE(i, freq, amp):
    steps = 3
    return amp * floor((triangleWAV(i, freq, 1.0) * float(steps))) / float(steps)

def circleWAV(i , freq, amp):
    wavelength = 1/float(freq)

    position = (4.0 * i) % (2.0 * wavelength) - float(wavelength)
    semi_circle = sqrt(wavelength**2 - position**2)
    semi_circle_wave = (amp / wavelength) * semi_circle
    direction_wave = (-1)**(((2*i) // wavelength) % 2)
    result = semi_circle_wave * direction_wave

    return result


def get_LFO_wav_function(modifier):
    amplitude = modifier["amplitude"]
    frequency = modifier["frequency"]
    waveForm = modifier["waveform"]
    def waveFunc(i):
        return waveForm(i, frequency, amplitude)
    return waveFunc

def modify_frequency(i, frequency, wavFunc):
    if i == 0:
        return frequency
    return frequency + (wavFunc(i) / float(i))

def modify_amplitude(i, amplitude, wavFunc):
    return 0.5 * amplitude * (wavFunc(i) + 1 )

LFO_attribute_functions = {
    "frequency": modify_frequency,
    "amplitude": modify_amplitude
}

def get_oscillator_sound_function(oscillator, frequency):
    
    modifiers = oscillator["modifiers"]

    phaseOffset = (oscillator["phase"]/100)/frequency

    OSCfrequency = frequency + getFrequencyOffset(oscillator["freqOffset"], frequency)
    amplitude = oscillator["amplitude"]

    def soundFunction(i):

      samplePoint =  (i + phaseOffset)
      modified_frequency = OSCfrequency
      modified_amplitude = amplitude
      for modifier in modifiers:
          modifierAttribute = modifier["targetAttribute"]
          modifierWavFunction = get_LFO_wav_function(modifier)
            #change to only apply when it is targeted to this one
          if modifierAttribute == 'amplitude':
              modified_amplitude = LFO_attribute_functions[modifierAttribute](i, modified_amplitude, modifierWavFunction)
          
          if modifierAttribute == 'frequency':
              modified_frequency = LFO_attribute_functions[modifierAttribute](i, modified_frequency, modifierWavFunction)
        
      return oscillator["waveform"](samplePoint, modified_frequency, modified_amplitude)
    

    return soundFunction


def avg_all_WAV(i, waves , frequency):
    totalSample = 0

    for modifyingOsci in waves.keys():
       oscillator = waves[modifyingOsci] 

       oscillatorSoundFunction = get_oscillator_sound_function(oscillator, frequency)
       sample = oscillatorSoundFunction(i)
       
       totalSample = totalSample + sample
    return totalSample/(len(waves.keys()))