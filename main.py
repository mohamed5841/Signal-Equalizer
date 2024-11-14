import librosa
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow , QFileDialog
import pyqtgraph as pg
import numpy as np
import sounddevice as sd
import sys
from PyQt5 import uic
import time
from PyQt5.QtCore import Qt
from Mode import mode
from Spec_Widget import spec_Widget
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget , QDesktopWidget
from scipy.fft import fft, ifft, fftfreq
import pandas as pd
import copy
Ui_MainWindow, QtBaseClass = uic.loadUiType("equalizer.ui")

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        screen_size=QDesktopWidget().screenGeometry()
        width=screen_size.width()
        height=screen_size.height()
        self.setGeometry(0,0,width , height-100)
        
    
        
        # animal_frequncy_slices={self.VerticalSlider_Channel_10:[4000,20000]
        #      ,self.VerticalSlider_Channel_9:[1000,4000]
        #      ,self.VerticalSlider_Channel_8:[300,1500]
        #      ,self.VerticalSlider_Channel_7:[0,1000]}
        animal_frequncy_slices={self.VerticalSlider_Channel_8:[4000, 10000]
             ,self.VerticalSlider_Channel_6:[1000,4000]
             ,self.VerticalSlider_Channel_4:[450, 1100]
             ,self.VerticalSlider_Channel_2:[0, 450]}
        
        self.hommos_frequcy_slices={self.VerticalSlider_Channel_8:[5000,16000]
                    ,self.VerticalSlider_Channel_6:[2000,5000]
                    ,self.VerticalSlider_Channel_4:[200,2000]
                    ,self.VerticalSlider_Channel_2:[20,200]}
        
        
        
        # Music_frequncy_slices={self.VerticalSlider_Channel_8:[400, 1000]
        #             ,self.VerticalSlider_Channel_6:[250, 400]
        #             ,self.VerticalSlider_Channel_4:[170, 250]
        #             ,self.VerticalSlider_Channel_2:[0, 170]}

        # ranges from malak 
        Music_frequncy_slices={self.VerticalSlider_Channel_8:[5000,16000]
                    ,self.VerticalSlider_Channel_6:[2000,5000]
                    ,self.VerticalSlider_Channel_4:[500,2000]
                    ,self.VerticalSlider_Channel_2:[20,500]}
        
        
        self.ECG_frequncy_slices={self.VerticalSlider_Channel_8:[100,300]
                    ,self.VerticalSlider_Channel_6:[20,60]
                    ,self.VerticalSlider_Channel_4:[5,20]
                    ,self.VerticalSlider_Channel_2:[0,50]}
        
        uniform_frequncy_slices={self.VerticalSlider_Channel_10:[100,100]
             ,self.VerticalSlider_Channel_9:[90,90]
             ,self.VerticalSlider_Channel_8:[80,80]
             ,self.VerticalSlider_Channel_7:[70,70],
             self.VerticalSlider_Channel_6:[60,60]
             ,self.VerticalSlider_Channel_5:[50,50]
             ,self.VerticalSlider_Channel_4:[40,40]
             ,self.VerticalSlider_Channel_3:[30,30],
             self.VerticalSlider_Channel_2:[20,20]
             ,self.VerticalSlider_Channel_1:[10,10]
             }
        
        

        
        
        self.speed_factor=1
        self.tracking_index=0
        self.last_ind=0
        self.num_frames=0

        #assigin
        animal_obj=mode("animal_mix.wav",True)
        animal_obj.freq_slices=animal_frequncy_slices
        
        music_obj=mode("musicFinal.wav",True)
        music_obj.freq_slices=Music_frequncy_slices

        uniform_obj=mode("mixed2_signal.csv",False)
        uniform_obj.freq_slices=uniform_frequncy_slices
        
        ecg_obj=mode("Normal_ECG.csv" , False)
        ecg_obj.freq_slices=self.ECG_frequncy_slices

        self.mode=uniform_obj 
        self.mode.timer.start()
        self.mode.timer.timeout.connect(self.update_plot)
        self.ComboBox_Mode.setItemData(0, uniform_obj, Qt.UserRole)
        self.ComboBox_Mode.setItemData(1, music_obj, Qt.UserRole)
        self.ComboBox_Mode.setItemData(2, animal_obj, Qt.UserRole)
        self.ComboBox_Mode.setItemData(3, ecg_obj, Qt.UserRole)

     
        self.plot_input = self.Widget_Signal_Input.plot(pen="r")
        self.plot_output= self.Widget_Signal_Output.plot(pen="r")


        self.checkBox.stateChanged.connect(self.toggle_spectrograms_visibility)
        


        self.ComboBox_Mode.currentIndexChanged.connect(lambda index :self.Change_mode(index))
        self.comboBox_Frequancy_Scale.currentIndexChanged.connect(self.plot_frequency_spectrum)
        self.PushButton_Reset_Input.clicked.connect(lambda:self.reset())
        
        self.PushButton_PlayPause_Input.clicked.connect(lambda:self.play_pause())
        self.PushButton_Upload_Signal.clicked.connect(lambda: self.Load_ECG_Signal())
       
        self.HorizontalSlider_Speed_Input.setMinimum(2)
        self.HorizontalSlider_Speed_Input.setMaximum(40)
        self.HorizontalSlider_Speed_Input.setSingleStep(5)
        self.HorizontalSlider_Speed_Input.setValue(10)
        self.HorizontalSlider_Speed_Input.valueChanged.connect(lambda:self.set_speed())
        self.PushButton_ZoomIn_Input.clicked.connect(lambda : self.zoom_in())
        self.PushButton_Zoomout_Input.clicked.connect(lambda : self.zoom_out())


        # Connect sliders to apply attenuation
        #initialize the sliders with the noram values
        # self.VerticalSlider_Channel_7.setMinimum(5)
        # self.VerticalSlider_Channel_7.setMaximum(100)
        # self.VerticalSlider_Channel_7.setSingleStep(10)

        for i in range(1, 11):
            getattr(self, f"VerticalSlider_Channel_{i}").valueChanged.connect(lambda _, i=i: self.apply_attenuation(getattr(self, f"VerticalSlider_Channel_{i}"), i))
        
        # self.VerticalSlider_Channel_1.valueChanged.connect(lambda:self.apply_attenuation( self.VerticalSlider_Channel_1,1))
        # self.VerticalSlider_Channel_1.setValue(100)
        # self.VerticalSlider_Channel_2.valueChanged.connect(lambda:self.apply_attenuation( self.VerticalSlider_Channel_2,2))
        # self.VerticalSlider_Channel_2.setValue(100)
        
        # self.VerticalSlider_Channel_3.valueChanged.connect(lambda:self.apply_attenuation(self.VerticalSlider_Channel_3,3))
        # self.VerticalSlider_Channel_3.setValue(100)
        # self.VerticalSlider_Channel_4.valueChanged.connect(lambda:self.apply_attenuation( self.VerticalSlider_Channel_4,4))
        # self.VerticalSlider_Channel_4.setValue(100)
        # self.VerticalSlider_Channel_5.valueChanged.connect(lambda:self.apply_attenuation( self.VerticalSlider_Channel_5,5))
        # self.VerticalSlider_Channel_5.setValue(100)
        # self.VerticalSlider_Channel_6.valueChanged.connect(lambda:self.apply_attenuation( self.VerticalSlider_Channel_6,6))
        # self.VerticalSlider_Channel_6.setValue(100)
        

        # self.VerticalSlider_Channel_7.valueChanged.connect(lambda:self.apply_attenuation(self.VerticalSlider_Channel_7,7))
        # self.VerticalSlider_Channel_7.setValue(100)
        # self.VerticalSlider_Channel_8.valueChanged.connect(lambda:self.apply_attenuation( self.VerticalSlider_Channel_8,8))
        # self.VerticalSlider_Channel_8.setValue(100)
        # self.VerticalSlider_Channel_9.valueChanged.connect(lambda:self.apply_attenuation( self.VerticalSlider_Channel_9,9))
        # self.VerticalSlider_Channel_9.setValue(100)
        # self.VerticalSlider_Channel_10.valueChanged.connect(lambda:self.apply_attenuation( self.VerticalSlider_Channel_10,10))
        
        self.spectrogram_widget1 = spec_Widget()
        self.spectrogram_widget2 = spec_Widget()

        # Set up layouts for spectrogram widgets
        self.setup_widget_layout(self.spectrogram_widget1, self.Widget_Spectrogram_Input)
        self.setup_widget_layout(self.spectrogram_widget2, self.Widget_Spectrogram_Output)

        self.Change_mode(0)





   
        
    
    def setup_widget_layout(self, spec_widget, target_widget):
        if isinstance(target_widget, QWidget):
            layout = QVBoxLayout(target_widget)
            layout.addWidget(spec_widget)
            target_widget.setLayout(layout)  
        else:
   
            print("Target widget is not a valid QWidget")

    def browse_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;CSV Files (*.csv);;DAT Files (*.dat);;XLSX Files (*.xlsx);;TXT Files (*.txt)", options=options)
        
        if fileName:
            print(f"Selected file: {fileName}")
            try:
                return fileName
            except Exception as e:
                print(f"Error opening file: {e}")
                return None
        else:
            print("No file selected")
            return None
  
    
    def Load_ECG_Signal(self):
        filename=self.browse_file()
        audio=self.mode.audio
        freq_slices=self.mode.freq_slices
        loaded_obj=mode(filename,audio)
        loaded_obj.freq_slices=freq_slices
        self.mode=loaded_obj
        self.mode.timer.start()
        self.mode.timer.timeout.connect(self.update_plot)
        self.ComboBox_Mode.setItemData(self.ComboBox_Mode.currentIndex(), loaded_obj, Qt.UserRole)
        self.Change_mode(self.ComboBox_Mode.currentIndex())


        




    def Change_mode(self , index):
        self.HorizontalSlider_Speed_Input.setValue(10)
        self.PushButton_PlayPause_Input.setText("Pause")
        if self.mode.audio:
            self.stream.stop()
        self.mode.timer.stop()
        self.mode = self.ComboBox_Mode.itemData(index, Qt.UserRole)
        self.tracking_index=self.mode.tracking_index
        self.frequncies=np.fft.fftfreq(len(self.mode.signal.amplitude), 1 / self.mode.signal.sample_rate) 
        self.fft_result = np.fft.fft( self.mode.signal.amplitude)

        self.isplay=self.mode.isplaying
        self.timer=self.mode.timer
        self.mode.timer.timeout.connect(self.update_plot)

        self.mode.timer.start()
        self.audio_data = self.mode.audio_data
        self.modified_audio=self.audio_data
        self.spectrogram_widget1.plot_spectrogram(self.mode.signal.amplitude, self.mode.signal.sample_rate )
        self.spectrogram_widget2.plot_spectrogram(self.mode.signal.amplitude, self.mode.signal.sample_rate )
       
        self.cumulative_attenuation =  np.ones((10, len(self.audio_data)))
       
        self.audio_data_stretched=self.audio_data
        self.original_audio_data=self.audio_data

        if self.mode.audio:
            self.stream = sd.OutputStream(
            samplerate=self.mode.signal.sample_rate,
            channels=1,
            callback=self.audio_callback)
            self.stream.start()
         
        # self.calculate_fft()
        self.Reset_slider()
        self.setup_sliders()

        self.timer.start()
        self.plot_frequency_spectrum()

    def reset(self):
        self.tracking_index=0
        self.timer.start()
        self.PushButton_PlayPause_Input.setText("Pause")
        self.isplay=True
        if self.mode.audio:
            self.stream.start()

       
        
    def play_pause(self):
        if self.isplay:
            self.isplay=False
            self.timer.stop()
            self.PushButton_PlayPause_Input.setText("play")
            if self.mode.audio:
                self.stream.stop()
        else:
            self.isplay=True
            self.timer.start()
            self.PushButton_PlayPause_Input.setText("Pause")
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
        remaining_samples = len(self.audio_data_stretched) - self.tracking_index

        # Ensure that the end index is within the bounds of the audio data
        if end_index <= len(self.audio_data_stretched):
            # If the end_index is within bounds, copy data directly
            outdata[:, 0] = self.audio_data_stretched[self.tracking_index:end_index]
        else:
            # If end_index is out of bounds, copy the remaining samples
            if remaining_samples > 0:
                outdata[:remaining_samples, 0] = self.audio_data_stretched[self.tracking_index:]

            if remaining_samples < frames:
                outdata[remaining_samples:, 0] = 0


        self.tracking_index = end_index
        if self.tracking_index >= len(self.audio_data_stretched):
            self.stream.stop()  # Stop playback when done




    def update_plot(self):
        # Plot current chunk of data up to the tracking index for progress display
        tracking_index=int(self.tracking_index*self.speed_factor)
        if tracking_index < len(self.mode.signal.amplitude) :
            
            # Plot progress using a separate line over the waveform
            self.plot_input.setData((self.mode.signal.time[:tracking_index]), self.mode.signal.amplitude[:tracking_index])
            self.plot_output.setData((self.mode.signal.time[:tracking_index]), self.modified_audio[:tracking_index])
            # self.spectrogram_widget1.plot_spec_parts(self.mode.signal.Spec_input_stft[:tracking_index] , self.mode.signal.sample_rate )
            
            # print(self.mode.frames)
            # print(len(self.modified_audio[:tracking_index] ) , len(self.mode.signal.amplitude[:tracking_index]))
           
            # print(self.mode.signal.Spec_input_stft.shape)
            
            # print(self.tracking_index , self.last_ind)
            # if tracking_index - self.last_ind == self.mode.signal.spec_step:
            #    self.last_ind=tracking_index
               
            # #    print("here")
            # #    print(len(self.mode.signal.Spec_input_stft[: ,self.num_frames]))
            #    self.spectrogram_widget1.plot_spec_parts(self.mode.signal.Spec_input_stft[:self.num_frames * self.mode.signal.spec_step] , self.mode.signal.sample_rate )
            #    self.num_frames+=1
            # self.spectrogram_widget2.plot_spectrogram(self.modified_audio[:tracking_index] , self.mode.signal.sample_rate , n_fft=self.mode.frames)
           
            if not self.mode.audio and tracking_index < len(self.mode.signal.amplitude):
                self.tracking_index+=self.mode.frames   
                # self.speed_factor=1
            
        else:
            self.timer.stop()


    
    def attenuate_frequency_range(self, freq_start, freq_end, attenuation_factor,index):
        """Apply attenuation to the cumulative attenuation array based on frequency range and factor."""
        # fft_result = np.fft.fft(self.original_audio_data)
        frequencies = self.frequncies
        
        # Identify indices within the frequency range and apply the attenuation factor
        indices = np.where((frequencies >= freq_start) & (frequencies <= freq_end))[0]
        self.cumulative_attenuation[index-1][indices] *= attenuation_factor
        self.cumulative_attenuation[index-1][-indices] *= attenuation_factor  # Apply to negative frequencies as well
        

    def apply_attenuation(self,slider_obj,index):
        fft_result=None
        """Update the audio signal with cumulative attenuation from each slider."""
        # Reset cumulative attenuation before applying new values
        self.cumulative_attenuation[index-1] = np.ones(len(self.audio_data))
        
        # Apply each slider’s attenuation range
        self.attenuate_frequency_range(self.mode.freq_slices[slider_obj][0], self.mode.freq_slices[slider_obj][1], slider_obj.value() / 100,index)
        fft_result =copy.copy (self.fft_result)
        # Apply cumulative attenuation to the original audio data
        # tst= np.fft.fft(self.mode.signal.amplitude)
        # tst2=np.fft.fft(self.modified_audio)
        # print(tst2)
        
        # if np.array_equal(fft_result, tst2):
        #     print("The arrays are the same.")
        # else:
        #     print("The arrays are different.")
        
        for i in range(10):
            fft_result *= self.cumulative_attenuation[i] 
        self.modified_audio = np.fft.ifft(fft_result).real
        self.set_speed()
        self.plot_frequency_spectrum()
        self.spectrogram_widget2.plot_spectrogram(self.modified_audio, self.mode.signal.sample_rate )
        

    # def calculate_fft(self):
    #     # print("here")
    #     freq_mag=np.fft.fft(self.mode.signal.amplitude)
    #     freq= np.fft.fftfreq(len(self.mode.signal.amplitude), 1 / self.mode.signal.sample_rate)
    #     self.mode.signal.set_freq(freq_mag ,freq)



    # def get_top_frequencies(self, signal_data, sample_rate, num_frequencies=10):
    #     """Extracts the top frequencies by magnitude from the signal."""
    #     # Compute FFT of the signal
    #     fft_result = fft(signal_data)
    #     frequencies = fftfreq(len(fft_result), 1 / sample_rate)
    #     magnitudes = np.abs(fft_result)

    #     # Filter positive frequencies and their magnitudes
    #     positive_frequencies = frequencies[frequencies >= 0]
    #     positive_magnitudes = magnitudes[frequencies >= 0]

    #     # Sort frequencies by magnitude and get the top N frequencies
    #     sorted_indices = np.argsort(positive_magnitudes)[::-1]
    #     top_frequencies = positive_frequencies[sorted_indices][:num_frequencies]
    #     # Convert to a sorted list to maintain ascending order
    #     return sorted(top_frequencies)


    



        # Update the audio playback and plot
        # Update audio data for playback
        # self.Widget_Signal_Input.clear()
        # self.plot1.setData(self.mode.signal.time, self.modified_audio, pen="b")
        # self.play_audio(self.modified_audio)
         
        # Update the frequency plot
        # self.plot_frequency_spectrum(self.modified_audio)

    def plot_frequency_spectrum(self):
        index=self.comboBox_Frequancy_Scale.currentIndex()
        """Plot the frequency spectrum of the modified audio."""
        fft_result = np.fft.fft(self.modified_audio)
        frequencies = np.fft.fftfreq(len(fft_result), (1 / self.mode.signal.sample_rate))
        magnitude = np.abs(fft_result)
        
        self.Widget_Frequancy.clear()
        pos_frequencies = frequencies[:len(frequencies)//2]
        pos_magnitude = magnitude[:len(magnitude)//2]
        
        
        sr=self.mode.signal.sample_rate
        log_frequency_bands = np.logspace(np.log10(50), np.log10(sr // 2), num=50)
        band_amplitudes = []

        # Calculate the average amplitude in each frequency band
        for band in log_frequency_bands:
            # Find indices of the frequencies that fall within each band
            band_indices = np.where((pos_frequencies >= band - 50) & (pos_frequencies <= band + 50))
            band_magnitude = np.mean(magnitude[band_indices])
            band_amplitudes.append(band_magnitude)
        if index==0:
            pos_plot = pg.PlotDataItem(pos_frequencies, pos_magnitude, pen=pg.mkPen('b', width=2))
        else: 
            pos_plot = pg.PlotDataItem(log_frequency_bands, band_amplitudes, pen=pg.mkPen('b', width=2))
        
        self.Widget_Frequancy.addItem(pos_plot)


        


    def toggle_spectrograms_visibility(self):
        # Check if the checkbox is checked
        if self.checkBox.isChecked():
            # Show the spectrogram widgets
            self.Widget_Spectrogram_Input.show()
            self.Widget_Spectrogram_Output.show()
        else:
            # Hide the spectrogram widgets
            self.Widget_Spectrogram_Input.hide()
            self.Widget_Spectrogram_Output.hide()
    
    def Reset_slider(self):
        index=self.ComboBox_Mode.currentIndex()
        if index==0:
            self.Widget_Frequancy.setXRange(0,120)
            for i in range(1, 11):
                getattr(self, f"VerticalSlider_Channel_{i}").setValue(100)
        elif index== 1 or index==2:
            for i in range(2 , 10 , 2):
                getattr(self, f"VerticalSlider_Channel_{i}").setValue(100)
        # music
        if index==1:
            self.Widget_Frequancy.setXRange(18,11000)
        # animal
        if index==2:
            self.Widget_Frequancy.setXRange(0,10000)
            # ECG
        if index==3:
            # for i in range(4 , 10 , 2):
            #     getattr(self, f"VerticalSlider_Channel_{i}").setValue(0)
            self.Widget_Frequancy.setXRange(0,400)


        self.HorizontalSlider_Speed_Input.setValue(10)

    


    def setup_sliders(self):
        if self.ComboBox_Mode.currentText() == 'Uniform Range Mode':
            self.frame_17.show()
            self.frame_19.show()
            self.frame_21.show()
            self.frame_23.show()
            self.frame_25.show()
            self.frame_26.show()

            self.label_6.setText("Ch(1)")
            self.label_8.setText("Ch(2)")
            self.label_12.setText("Ch(3)")
            self.label_14.setText("Ch(4)")
            self.label_16.setText("Ch(5)")
            self.label_18.setText("Ch(6)")
            self.label_20.setText("Ch(7)")
            self.label_22.setText("Ch(8)")
            self.label_24.setText("Ch(9)")
            self.label_26.setText("Ch(10)")

        else:
            self.frame_17.hide()
            self.frame_19.hide()
            self.frame_21.hide()
            self.frame_23.hide()
            self.frame_25.hide()
            self.frame_26.hide()



            if self.ComboBox_Mode.currentText() == 'Musical Instruments Mode':
                self.label_8.setText("Bass")
                self.label_14.setText("Guiter")
                self.label_18.setText("Violin")
                self.label_22.setText("Piano")
            
            elif self.ComboBox_Mode.currentText() == 'Animal Sound Mode':
                self.label_8.setText("Dog")
                self.label_14.setText("Wovle")
                self.label_18.setText("Crow")
                self.label_22.setText("Bat")

            elif self.ComboBox_Mode.currentText() == 'ECG Abnormalities Mode':
                self.label_8.setText("Normal")
                self.label_14.setText("BS")
                self.label_18.setText("PVC")
                self.label_22.setText("VF")




    def zoom_in(self ) :
        viewboxI=self.Widget_Signal_Input.getViewBox()
        viewboxO=self.Widget_Signal_Output.getViewBox()
        viewboxI.scaleBy((.8,.8))
        viewboxO.scaleBy((0.8,.8))


    def zoom_out(self):
           viewboxI=self.Widget_Signal_Input.getViewBox()
           viewboxO=self.Widget_Signal_Output.getViewBox()
           viewboxI.scaleBy((1/0.8, 1/0.8))
           viewboxO.scaleBy((1/0.8, 1/0.8))



if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
