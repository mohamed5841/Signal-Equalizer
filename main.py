import librosa
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
import pyqtgraph as pg
import numpy as np
import sounddevice as sd
import sys
from PyQt5 import uic
import time
from PyQt5.QtCore import Qt
from Mode import mode
Ui_MainWindow, QtBaseClass = uic.loadUiType("equalizer.ui")

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        
        animal_frequncy_slices={self.VerticalSlider_Channel_10:[4000,20000]
             ,self.VerticalSlider_Channel_9:[300,1500]
             ,self.VerticalSlider_Channel_8:[1000,4000]
             ,self.VerticalSlider_Channel_7:[0,1000]}
        uniform_frequncy_slices={self.VerticalSlider_Channel_10:[100,100]
             ,self.VerticalSlider_Channel_9:[85,95]
             ,self.VerticalSlider_Channel_8:[75,85]
             ,self.VerticalSlider_Channel_7:[65,75],
             self.VerticalSlider_Channel_6:[55,65]
             ,self.VerticalSlider_Channel_5:[45,55]
             ,self.VerticalSlider_Channel_4:[35,45]
             ,self.VerticalSlider_Channel_3:[25,35],
             self.VerticalSlider_Channel_2:[15,25]
             ,self.VerticalSlider_Channel_1:[5,15]
             }
        
        self.speed_factor=1
        self.tracking_index=0

        #assigin
        animal_obj=mode("Animal_mix.wav",True)
        animal_obj.freq_slices=animal_frequncy_slices
        music_obj=mode("music2.wav",True)
        uniform_obj=mode("mixed2_signal.csv",False)
        uniform_obj.freq_slices=uniform_frequncy_slices
        self.mode=uniform_obj
        self.mode.timer.start()
        self.mode.timer.timeout.connect(self.update_plot)
        self.ComboBox_Mode.setItemData(0, uniform_obj, Qt.UserRole)
        self.ComboBox_Mode.setItemData(1, music_obj, Qt.UserRole)
        self.ComboBox_Mode.setItemData(2, animal_obj, Qt.UserRole)
        self.ComboBox_Mode.setItemData(3, animal_obj, Qt.UserRole)
        self.Change_mode(0)
     
        self.plot_input = self.Widget_Signal_Input.plot(pen="r")
        self.plot_output= self.Widget_Signal_Output.plot(pen="r")
        



        self.ComboBox_Mode.currentIndexChanged.connect(lambda index :self.Change_mode(index))
        self.PushButton_Reset_Input.clicked.connect(lambda:self.reset())

        self.PushButton_PlayPause_Input.clicked.connect(lambda:self.play_pause())
        self.PushButton_PlayPause_Output.clicked.connect(lambda:self.play())
        self.HorizontalSlider_Speed_Input.setMinimum(2)
        self.HorizontalSlider_Speed_Input.setMaximum(40)
        self.HorizontalSlider_Speed_Input.setSingleStep(1)
        self.HorizontalSlider_Speed_Input.setValue(10)
        self.HorizontalSlider_Speed_Input.valueChanged.connect(lambda:self.set_speed())


        # Connect sliders to apply attenuation
        #initialize the sliders with the noram values
        # self.VerticalSlider_Channel_7.setMinimum(5)
        # self.VerticalSlider_Channel_7.setMaximum(100)
        # self.VerticalSlider_Channel_7.setSingleStep(10)
        
        self.VerticalSlider_Channel_1.valueChanged.connect(lambda:self.apply_attenuation( self.VerticalSlider_Channel_1,1))
        self.VerticalSlider_Channel_1.setValue(100)
        self.VerticalSlider_Channel_2.valueChanged.connect(lambda:self.apply_attenuation( self.VerticalSlider_Channel_2,2))
        self.VerticalSlider_Channel_2.setValue(100)
        
        self.VerticalSlider_Channel_3.valueChanged.connect(lambda:self.apply_attenuation(self.VerticalSlider_Channel_3,3))
        self.VerticalSlider_Channel_3.setValue(100)
        self.VerticalSlider_Channel_4.valueChanged.connect(lambda:self.apply_attenuation( self.VerticalSlider_Channel_4,4))
        self.VerticalSlider_Channel_4.setValue(100)
        self.VerticalSlider_Channel_5.valueChanged.connect(lambda:self.apply_attenuation( self.VerticalSlider_Channel_5,5))
        self.VerticalSlider_Channel_5.setValue(100)
        self.VerticalSlider_Channel_6.valueChanged.connect(lambda:self.apply_attenuation( self.VerticalSlider_Channel_6,6))
        self.VerticalSlider_Channel_6.setValue(100)
        

        self.VerticalSlider_Channel_7.valueChanged.connect(lambda:self.apply_attenuation(self.VerticalSlider_Channel_7,7))
        self.VerticalSlider_Channel_7.setValue(100)
        self.VerticalSlider_Channel_8.valueChanged.connect(lambda:self.apply_attenuation( self.VerticalSlider_Channel_8,8))
        self.VerticalSlider_Channel_8.setValue(100)
        self.VerticalSlider_Channel_9.valueChanged.connect(lambda:self.apply_attenuation( self.VerticalSlider_Channel_9,9))
        self.VerticalSlider_Channel_9.setValue(100)
        self.VerticalSlider_Channel_10.valueChanged.connect(lambda:self.apply_attenuation( self.VerticalSlider_Channel_10,10))
        self.VerticalSlider_Channel_10.setValue(100)
        


    def Change_mode(self , index):
        self.HorizontalSlider_Speed_Input.setValue(10)
        if self.mode.audio:
            self.stream.stop()
        self.mode.timer.stop()
        self.mode = self.ComboBox_Mode.itemData(index, Qt.UserRole)
        self.tracking_index=self.mode.tracking_index
        self.isplay=self.mode.isplaying
        self.timer=self.mode.timer
        self.mode.timer.timeout.connect(self.update_plot)
        self.mode.timer.start()
        self.audio_data = self.mode.audio_data
        self.modified_audio=self.audio_data
        self.cumulative_attenuation =  np.ones((10, len(self.audio_data)))
        self.audio_data_stretched=self.audio_data
        self.original_audio_data=self.audio_data
        self.timer.start()
        if self.mode.audio:
            self.stream = sd.OutputStream(
            samplerate=self.mode.signal.sample_rate,
            channels=1,
            callback=self.audio_callback)
            self.stream.start()

    def reset(self):
        self.tracking_index=0
        self.timer.start()
        if self.mode.audio:
            self.stream.start()
        
    def play_pause(self):
        if self.isplay:
            self.isplay=False
            self.timer.stop()
            if self.mode.audio:
                self.stream.stop()
        else:
            self.isplay=True
            self.timer.start()
            if self.mode.audio:
                self.stream.start()

    def set_speed(self):
        value=self.HorizontalSlider_Speed_Input.value()
        self.old_speed_factor=self.speed_factor
        self.speed_factor=value/10
        self.audio_data_stretched = librosa.effects.time_stretch(self.modified_audio, rate=self.speed_factor)
        self.tracking_index*=(self.old_speed_factor/self.speed_factor)
        self.tracking_index=int(self.tracking_index)
        
        
        


    def audio_callback(self, outdata, frames, time, status):
        """Callback function to send audio in chunks to the OutputStream."""
        # print(frames)
        self.mode.frames=frames

        end_index = self.tracking_index + (frames)

        if end_index <= len(self.audio_data_stretched): 
            outdata[:, 0] = self.audio_data_stretched[self.tracking_index:end_index]
        else:
            remaining_samples = len(self.audio_data_stretched) - self.tracking_index
            outdata[:remaining_samples, 0] = self.audio_data_stretched[self.tracking_index:]
            outdata[remaining_samples:, 0] = 0  # Zero padding for the rest

        self.tracking_index = end_index
        if self.tracking_index >= len(self.audio_data_stretched):
            self.stream.stop()  # Stop playback when done




    def update_plot(self):
        # Plot current chunk of data up to the tracking index for progress display
        tracking_index=int(self.tracking_index*self.speed_factor)
        if tracking_index < len(self.mode.signal.amplitude):
            # Plot progress using a separate line over the waveform
            self.plot_input.setData((self.mode.signal.time[:tracking_index]), self.mode.signal.amplitude[:tracking_index])
            self.plot_output.setData((self.mode.signal.time[:tracking_index]), self.modified_audio[:tracking_index])
            if not self.mode.audio:
                self.tracking_index+=self.mode.frames
                # self.speed_factor=1
            
        else:
            self.timer.stop()


    
    def attenuate_frequency_range(self, freq_start, freq_end, attenuation_factor,index):
        """Apply attenuation to the cumulative attenuation array based on frequency range and factor."""
        # fft_result = np.fft.fft(self.original_audio_data)
        frequencies = np.fft.fftfreq(len(self.mode.signal.amplitude), 1 / self.mode.signal.sample_rate)
        
        # Identify indices within the frequency range and apply the attenuation factor
        indices = np.where((frequencies >= freq_start) & (frequencies <= freq_end))[0]
        self.cumulative_attenuation[index-1][indices] *= attenuation_factor
        self.cumulative_attenuation[index-1][-indices] *= attenuation_factor  # Apply to negative frequencies as well

    def apply_attenuation(self,slider_obj,index):
        """Update the audio signal with cumulative attenuation from each slider."""
        # Reset cumulative attenuation before applying new values
        self.cumulative_attenuation[index-1] = np.ones(len(self.audio_data))
        
        # Apply each slider’s attenuation range
        self.attenuate_frequency_range(self.mode.freq_slices[slider_obj][0], self.mode.freq_slices[slider_obj][1], slider_obj.value() / 100,index)
        # Apply cumulative attenuation to the original audio data
        fft_result = np.fft.fft(self.mode.signal.amplitude)
        for i in range(10):
            fft_result *= self.cumulative_attenuation[i] 
        self.modified_audio = np.fft.ifft(fft_result).real
        self.set_speed()


        # Update the audio playback and plot
        # Update audio data for playback
        # self.Widget_Signal_Input.clear()
        # self.plot1.setData(self.mode.signal.time, self.modified_audio, pen="b")
        # self.play_audio(self.modified_audio)
         
        # Update the frequency plot
        # self.plot_frequency_spectrum(self.modified_audio)

    # def plot_frequency_spectrum(self, modified_audio):
    #     """Plot the frequency spectrum of the modified audio."""
    #     fft_result = np.fft.fft(modified_audio)
    #     frequencies = np.fft.fftfreq(len(fft_result), 1 / self.sample_rate)
    #     magnitude = np.abs(fft_result)
        
    #     self.Widget_Frequancy.clear()
    #     pos_frequencies = frequencies[:len(frequencies)//2]
    #     pos_magnitude = magnitude[:len(magnitude)//2]
    #     pos_plot = pg.PlotDataItem(pos_frequencies, pos_magnitude, pen=pg.mkPen('b', width=2))
    #     self.Widget_Frequancy.addItem(pos_plot)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
