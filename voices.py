#!/usr/bin/env python3

from pyaudio import PyAudio
from audio import create_audio_callback
from waves import sineWAV, avg_all_WAV

from inputs import KeysPressed

import signal
import sys
import atexit

from config import (
    AUDIO_SAMPLE_WIDTH,
    AUDIO_SAMPLE_RATE,
    AUDIO_BUFFER_SIZE,
    AUDIO_MAX_VOLUME,
)


num_of_voices = 4
oldest_voice_played = None

wave_pos = [0]
masterAmplitude = 0.5
frequency = 700

defaultOscilattor = {
  "freqOffset" : 0,
  "phase" : 0,
  "amplitude" : 1.0,
  "waveform" : sineWAV,
  "modifiers": [
  ]
}

osci = {
    0: dict(defaultOscilattor),
}

def soundFunction(i):
    if len(osci.keys()) == 0:
        return 0
    return masterAmplitude * avg_all_WAV(i,osci,frequency)

default_voice_configuration = {
    # time in seconds
    # sustain as a percentage of amplitude
    'attack_time': 0.01,
    'decay_time': 0.1,
    'sustain_level': 0.8,
    'release_time': 0.1,
}


voice_configurations =  [
    dict(default_voice_configuration) 
]

active_voices = [
    
]
    
def test_callback(i):
    print(i)
    return i



def main():
    keys_pressed = KeysPressed()
    



    audio_player = PyAudio()
    stream = audio_player.open(format=audio_player.get_format_from_width(AUDIO_SAMPLE_WIDTH),
                                channels=1,
                                rate=AUDIO_SAMPLE_RATE,
                                input=True,
                                output=True,
                                frames_per_buffer=AUDIO_BUFFER_SIZE,
                                stream_callback=create_audio_callback(soundFunction, AUDIO_SAMPLE_RATE, AUDIO_MAX_VOLUME, wave_pos))
    stream.start_stream()
    def exit_handler():
        stream.stop_stream()
        stream.close()
        audio_player.terminate()

    def signal_handler(sig, frame):
        exit_handler()
        sys.exit(0)
    
    atexit.register(exit_handler)
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        print(keys_pressed.get_currently_pressed_keys())
        pass





if __name__ == '__main__':
    main()

