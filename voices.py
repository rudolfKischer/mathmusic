#!/usr/bin/env python3

from pyaudio import PyAudio
from audio import create_audio_callback
from waves import sineWAV, avg_all_WAV

from inputs import KeysPressed

import signal
import sys
import atexit
import math

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


num_of_voices = 10
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
    'attack_time': 0.5,
    'decay_time': 0.1,
    'sustain_level': 0.8,
    'release_time': 0.1,
    'assigned_key': None,
}

voices =  [dict(default_voice_configuration) for i in range(num_of_voices)]

voice_queue = [ voices[i] for i in range(num_of_voices) ]

def update_voices(keys):
    keys_pressed = dict(keys)
    # get the list of voice keys from the voices as a list
    voice_keys = [voice['assigned_key'] for voice in voices]

    unassigned_voices = []

    for voice in voices:
        # check that the current key is still being pressed
        if voice['assigned_key'] not in keys:
            voice['assigned_key'] = None
            unassigned_voices.append(voice)
        else:
            #remove the key from the list of keys
            keys_pressed.pop(voice['assigned_key'])

      # sort the keys by the oldest key
    keys_pressed = dict(sorted(keys_pressed.items(), key=lambda item: item[1]))
    for key in keys_pressed:
        # if there are no unassigned voices
        # add the voice with the oldest key to the unassigned voices
        # the oldest voice should always be the first voice in the queue
        # dont remove the voice from the queue
        if len(unassigned_voices) == 0:
            # move the oldest voice to the end of the queue
            oldest_voice = voice_queue.pop(0)
            voice_queue.append(oldest_voice)
            oldest_voice['assigned_key'] = None
            unassigned_voices.append(oldest_voice)


        unassigned_voices[0]['assigned_key'] = key
        unassigned_voices.pop(0)

def get_played_freq_to_amp(keys):
    # keys = keys_pressed.get_currently_pressed_keys()
    played_note_frequencies = { get_frequency_from_keyboard_key(key, 4): value for key, value in keys.items() if key in KEYBOARD_TO_NOTE_MAPPING }
    freq_to_amp = { key: get_envelope_amplitude_from_duration(value, default_voice_configuration) for key, value in played_note_frequencies.items()}
    return freq_to_amp

def get_note_level_mixing(i, freqs):
    #freqs = {key:frequencey, value:amplitude}
    # calculate the some of squares for each frequencys amplitude
    # if the sum of squares exceeds 1, then normalize the frequencies
    sample = 0.0
    sum_of_squares = 0
    for freq, amp in freqs.items():
        sum_of_squares += amp * amp

    for freq, amp in freqs.items():
        note_wave_sample = avg_all_WAV(i, osci, freq)

        if sum_of_squares > 1:
            scale_factor = math.sqrt(masterAmplitude/sum_of_squares)
            scaled_amp = amp * scale_factor
            sample += note_wave_sample * scaled_amp
        else:
            sample += note_wave_sample * amp
        
    return sample
    
    

def soundFunction(i):
    if len(osci.keys()) == 0:
        return 0
    freq_to_amp = get_played_freq_to_amp(keys_pressed.get_currently_pressed_keys())
    sample = get_note_level_mixing(i, freq_to_amp)
    return masterAmplitude * sample



def get_envelope_amplitude_from_duration(duration, voice):
    # dont do release time for now
    if duration < voice['attack_time']:
        return duration / voice['attack_time']
    elif duration < voice['attack_time'] + voice['decay_time']:
        return 1 - ((duration - voice['attack_time']) / voice['decay_time']) * (1 - voice['sustain_level'])
    elif duration < 0:
        # when duration is less than 0 that means the note has been released
        
    else:
        return voice['sustain_level']
    



    
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

        # # if keys are pressed
        # if len(keys) > 0:
            # print(keys_pressed.get_currently_pressed_keys())
            # # # map the keys to the notes
            # print([ get_note_number_from_keyboard_key(key, 4) for key in keys.keys() if key in KEYBOARD_TO_NOTE_MAPPING  ])
            # # # map the keys to the frequencies
            # print([ get_frequency_from_keyboard_key(key, 4) for key in keys.keys() if key in KEYBOARD_TO_NOTE_MAPPING ])
        pass





if __name__ == '__main__':
    main()

