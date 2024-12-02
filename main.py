import librosa
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow , QFileDialog
import pyqtgraph as pg
import numpy as np
import sounddevice as sd
import sys
from PyQt5 import uic

Ui_MainWindow, QtBaseClass = uic.loadUiType("Main_Program_UI.ui")

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # Load audio data and sample rate
        self.audio_data, self.sample_rate = librosa.load("animal_mix.wav", sr=None)
        print(self.sample_rate)
        self.time_axis = np.linspace(0, len(self.audio_data) / self.sample_rate, len(self.audio_data))
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
        

        # Initialize plot
        self.plot = self.Widget_1.plot()
        # self.plot.setData(self.time_axis, self.audio_data)  # Full waveform in the background

        # Overlay plot to display progress
        self.progress_plot = self.Widget_1.plot(pen="r")  # Progress plot in red

        # Set chunk size and timer interval for smooth playback
        self.chunk_duration = 0.05  # 50 ms per chunk for smoother playback
        self.chunk_size = int(self.chunk_duration * self.sample_rate)  # Samples per chunk
        self.tracking_index = 0

        # Set up timer for updating the plot
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.setInterval(int(self.chunk_duration * 1000))  # ms >> 0.05 * 1000 = 50 mssec
        self.timer.start()

        # Start playback with synchronized chunking
        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=self.audio_callback
        )
        self.stream.start()




    def audio_callback(self, outdata, frames, time, status):
        """Callback function to send audio in chunks to the OutputStream."""
        print(frames)
        end_index = self.tracking_index + frames

        if end_index <= len(self.audio_data): 
            outdata[:, 0] = self.audio_data[self.tracking_index:end_index]
        else:
            remaining_samples = len(self.audio_data) - self.tracking_index
            outdata[:remaining_samples, 0] = self.audio_data[self.tracking_index:]
            outdata[remaining_samples:, 0] = 0  # Zero padding for the rest

        self.tracking_index = end_index
        if self.tracking_index >= len(self.audio_data):
            self.stream.stop()  # Stop playback when done




    def update_plot(self):
        # Plot current chunk of data up to the tracking index for progress display
        if self.tracking_index < len(self.audio_data):
            # Plot progress using a separate line over the waveform
            self.progress_plot.setData(self.time_axis[:self.tracking_index], self.audio_data[:self.tracking_index])
        else:
            print("End of audio data reached. Stopping timer.")
            self.timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)  # تأكد من أن تطبيق Qt يتم إنشاؤه أولاً
    mainWindow = MainWindow()  # الآن يمكنك إنشاء MainWindow بعد QApplication
    mainWindow.show()  # إظهار النافذة
    sys.exit(app.exec_())  