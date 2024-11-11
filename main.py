import librosa
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
import pyqtgraph as pg
import numpy as np
import sounddevice as sd
import sys
from PyQt5 import uic

Ui_MainWindow, QtBaseClass = uic.loadUiType("equalizer.ui")

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # Load audio data and sample rate
        self.audio_data, self.sample_rate = librosa.load("animal_mix.wav", sr=None)
        print(self.sample_rate)
        self.time_axis = np.linspace(0, len(self.audio_data) / self.sample_rate, len(self.audio_data))

        # Initialize plot
        self.plot = self.Widget_Signal_Input.plot()
        # self.plot.setData(self.time_axis, self.audio_data)  # Full waveform in the background

        # Overlay plot to display progress
        self.progress_plot = self.Widget_Signal_Input.plot(pen="r")  # Progress plot in red

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
            self.timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
