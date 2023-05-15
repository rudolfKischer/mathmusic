from pyaudio import paContinue
from struct import pack

def create_audio_callback(soundFunction, sample_rate, maxVolume, wave_pos):
    
    def soundCallBack(in_data, frame_count, time_info, status):

      buffer_end = wave_pos[0] + frame_count
      out_data = b''
      for i in range(wave_pos[0], buffer_end):


          sample = soundFunction(( i / float(sample_rate)))



          sample_data = pack('h', int(sample * maxVolume))
          out_data += sample_data
          
      wave_pos[0] = buffer_end
      return (out_data, paContinue)
    
    return soundCallBack