from math import sin, pi

def getFrequencyOffset(cent,freq):
    
    freqOffset = freq*(2**(cent/1200))
    return freqOffset

def sineWAV(i, freq, amp):
    return amp * sin(2.0 * pi * freq * i)

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

def avg_all_WAV(i, waves , frequency):
    totalSample = 0

    for modifyingOsci in waves.keys():
       oscillator = waves[modifyingOsci] 

       
       oscillatorFrequency = frequency + getFrequencyOffset(oscillator["freqOffset"], frequency)
       phaseOffset = (oscillator["phase"]/100)/frequency
       samplePoint =  (i + phaseOffset)

       sample = oscillator["waveform"](
                samplePoint,
                oscillatorFrequency,
                oscillator["amplitude"])
       
       totalSample = totalSample + sample
    return totalSample/(len(waves.keys()))