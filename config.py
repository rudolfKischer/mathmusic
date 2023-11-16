from pynput.keyboard import KeyCode as KC

KEYBOARD_TO_NOTE_MAPPING = {
          KC.from_char("a") : 0,
          KC.from_char("w") : 1,
          KC.from_char("s") : 2,
          KC.from_char("e") : 3,
          KC.from_char("d") : 4,
          KC.from_char("f") : 5,
          KC.from_char("t") : 6,
          KC.from_char("g") : 7,
          KC.from_char("y") : 8,
          KC.from_char("h") : 9,
          KC.from_char("u") : 10,
          KC.from_char("j") : 11,
          KC.from_char("k") : 12,
          KC.from_char("o") : 13,
          KC.from_char("l") : 14,
          KC.from_char("p") : 15,
          KC.from_char(";") : 16,
          KC.from_char("'") : 17,
          KC.from_char("]") : 18,
          KC.from_char("z") : "down",
          KC.from_char("x") : "up"
      }


AUDIO_SAMPLE_WIDTH = 2
AUDIO_SAMPLE_RATE = 44100
AUDIO_BUFFER_SIZE = 1024
AUDIO_MAX_VOLUME = 32767