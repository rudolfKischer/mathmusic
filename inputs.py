#!/usr/bin/env python3

from pynput.keyboard import Key, Listener
from time import time, sleep
import threading
 # a dictionary of when the key press started
press_interval = 0.1 # how often to update the time a key is pressed

class KeysPressed:
    def __init__(self):
        self.currently_pressed_keys = {}
        self.listen()

    def on_press(self, key):
        if key not in self.currently_pressed_keys:
            self.currently_pressed_keys[key] = time()

    def on_release(self, key):
        if key in self.currently_pressed_keys:
            del self.currently_pressed_keys[key]
    
    def get_currently_pressed_keys(self):
        #convert timestamp to duration pressed
        keys = dict(self.currently_pressed_keys)
        return {key: time() - keys[key] for key in keys}
    
    def listen(self):
        self.listener_thread = Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener_thread.daemon = True
        self.listener_thread.start()
    
    def stop_listening(self):
        self.listener.stop()
        self.listener.join()

def main():
    keys_pressed = KeysPressed()
    while True:
        print(keys_pressed.get_currently_pressed_keys())

if __name__ == '__main__':
    main()
