import numpy as np
class signal:
    def __init__(self,name,amplitude,sample_rate):
        self.name=name
        self.amplitude=amplitude
        self.sample_rate=sample_rate
        self.time=np.linspace(0, len(self.amplitude) / self.sample_rate, len(self.amplitude)) 
        self.frequncies=None
        self.frequncies_magnitude=None
        self.updated_frequncies_magnitude=None
        self.updated_amplitude=None
        self.fft_magintude=None

        self.Spec_input_stft=None
        self.spec_step=None
        
    def set_freq(self , frequncies_magnitude , frequncies):
        self.frequncies_magnitude = frequncies_magnitude 
        self.frequncies = frequncies

    def get_freq(self ):
         return self.frequncies
        
    def get_freq_mag(self):
        return self.frequncies_magnitude 
    
        
        