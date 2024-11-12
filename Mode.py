from PyQt5 import QtCore
import pandas as pd
from Signal import signal
import librosa
import numpy as np
import sounddevice as sd
class mode:
    def __init__(self,path,audio): 
        self.signal=self.signal_creation(path)
        self.isplaying=True
        self.tracking_index=0
        self.timer= QtCore.QTimer()
        self.timer.setInterval(50)
        self.stream=None
        self.audio_data=self.signal.amplitude
        self.frames=10
        self.audio=audio


    def signal_creation(self,path):
        """Load mixed signal data from CSV file."""

        if path.endswith('.csv'):
            data = pd.read_csv(path)
            if 'Time' in data.columns and 'Signal' in data.columns:
                time = data['Time'].values
                amplitude = data['Signal'].values
                sample_rate = time[1]-time[0]
            else:
                raise ValueError("CSV file must contain 'Time' and 'Signal' columns.")
       
        elif path.endswith('.wav'):
            amplitude , sample_rate = librosa.load(path , sr= None)
            time = np.linspace(0 , len(amplitude)/sample_rate ,sample_rate)

        return signal(path,amplitude,sample_rate)
    

    # def creat_stream(self):
    #     self.stream=sd.OutputStream(
    #         samplerate=self.signal.sample_rate,
    #         channels=1,
    #         callback=self.audio_callback
    #     )
    #     self.audio_data=self.signal.amplitude
    #     self.stream.start()
    #     return self.stream
    

    # def audio_callback(self, outdata, frames, time, status):
    #     """Callback function to send audio in chunks to the OutputStream."""
    #     # print(frames)
    #     self.frames=frames
    #     end_index = self.tracking_index + (frames)

    #     if end_index <= len(self.audio_data): 
    #         outdata[:, 0] = self.audio_data[self.tracking_index:end_index]
    #     else:
    #         remaining_samples = len(self.audio_data) - self.tracking_index
    #         outdata[:remaining_samples, 0] = self.audio_data[self.tracking_index:]
    #         outdata[remaining_samples:, 0] = 0  # Zero padding for the rest

    #     if self.tracking_index >= len(self.audio_data):
    #         self.stream.stop()  # Stop playback when done
    
    

    