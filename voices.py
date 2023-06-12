#!/usr/bin/env python3

from pyaudio import PyAudio
from audio import create_audio_callback
from waves import sineWAV, avg_all_WAV

from inputs import KeysPressed

import signal
import sys
import atexit

from utils import (
    get_note_number_from_keyboard_key,
    get_frequency_from_keyboard_key,
)

from config import (
    AUDIO_SAMPLE_WIDTH,
    AUDIO_SAMPLE_RATE,
    AUDIO_BUFFER_SIZE,
    AUDIO_MAX_VOLUME,
    KEYBOARD_TO_NOTE_MAPPING
)


num_of_voices = 4
oldest_voice_played = None

wave_pos = [0]
masterAmplitude = 0.1
frequency = 400

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

keys_pressed = KeysPressed()

default_voice_configuration = {
    # time in seconds
    # sustain as a percentage of amplitude
    'attack_time': 0.3,
    'decay_time': 0.1,
    'sustain_level': 0.4,
    'release_time': 0.1,
}

def get_played_freq_to_amp(keys):
    keys = keys_pressed.get_currently_pressed_keys()
    played_note_frequencies = { get_frequency_from_keyboard_key(key, 4): value for key, value in keys.items() if key in KEYBOARD_TO_NOTE_MAPPING }
    freq_to_amp = { key: get_envelope_amplitude_from_duration(value, default_voice_configuration) for key, value in played_note_frequencies.items()}
    return freq_to_amp



def soundFunction(i):
    if len(osci.keys()) == 0:
        return 0
    freq_to_amp = get_played_freq_to_amp(keys_pressed.get_currently_pressed_keys())
    sample = 0.0
    for freq, amp in freq_to_amp.items():
        sample += avg_all_WAV(i,osci,freq) * amp
    if len(freq_to_amp) == 0:
        return 0
    sample = sample / len(freq_to_amp)
    return masterAmplitude * sample#avg_all_WAV(i,osci,frequency)



def get_envelope_amplitude_from_duration(duration, voice):
    # dont do release time for now
    if duration < voice['attack_time']:
        return duration / voice['attack_time']
    elif duration < voice['attack_time'] + voice['decay_time']:
        return 1 - ((duration - voice['attack_time']) / voice['decay_time']) * (1 - voice['sustain_level'])
    else:
        return voice['sustain_level']
    


voice_configurations =  [
    dict(default_voice_configuration) 
]

active_voices = [
    
]
    
def test_callback(i):
    print(i)
    return i



def main():
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
        keys = keys_pressed.get_currently_pressed_keys()

        # if keys are pressed
        if len(keys) > 0:
            print(keys_pressed.get_currently_pressed_keys())
            # # map the keys to the notes
            print([ get_note_number_from_keyboard_key(key, 4) for key in keys.keys() if key in KEYBOARD_TO_NOTE_MAPPING  ])
            # # map the keys to the frequencies
            print([ get_frequency_from_keyboard_key(key, 4) for key in keys.keys() if key in KEYBOARD_TO_NOTE_MAPPING ])
        pass





if __name__ == '__main__':
    main()

