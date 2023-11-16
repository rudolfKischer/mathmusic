from config import KEYBOARD_TO_NOTE_MAPPING

def get_frequency_from_note_number(note_number):
    """
    Returns the frequency of a note given its note number and octave.
    """
    return round(16.35*(2**(1/12))**note_number, 2)

def get_note_number_from_keyboard_key(key, octave):
    """
    Returns the note number of a key on the keyboard.
    """
    return KEYBOARD_TO_NOTE_MAPPING[key]+12*octave

def get_frequency_from_keyboard_key(key, octave):
    """
    Returns the frequency of a key on the keyboard.
    """
    return get_frequency_from_note_number(get_note_number_from_keyboard_key(key, octave))



    