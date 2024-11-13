from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import librosa.display

class spec_Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = FigureCanvas(Figure())
        
        # Set the canvas to expand fully
        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        # Set up layout without any margins or spacing
        vertical_layout = QVBoxLayout(self)
        vertical_layout.addWidget(self.canvas)
        vertical_layout.setContentsMargins(0, 0, 0, 0)  # Remove all margins
        vertical_layout.setSpacing(0)  # Remove spacing
        
        # Initialize the axes
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.setLayout(vertical_layout)

    
      

    def plot_spectrogram(self, data, sample_rate, x_label='Time', y_label='Frequency' ,  n_fft=2048):
        if data is None or len(data) == 0:
            return  # Exit the function if data is empty
        self.canvas.axes.clear()  # Clear previous plot
        n_fft = min(n_fft, len(data))
        try:
            spectrogram = librosa.amplitude_to_db(
                np.abs(librosa.stft(data, n_fft=n_fft)),
                ref=np.max
            )
        except ValueError as e:
            print("hereeee")
            return

        # Display the spectrogram with axes and labels
        librosa.display.specshow(
            spectrogram,
            sr=sample_rate,
            x_axis='time',
            y_axis='log',
            ax=self.canvas.axes,
            cmap='magma'  # Optional: set a color map
        )

        # Set labels if needed
        self.canvas.axes.set_xlabel(x_label)
        self.canvas.axes.set_ylabel(y_label)

        # Adjust padding to allow room for labels and ticks
        self.canvas.figure.subplots_adjust(left=0.1, right=1, top=0.9, bottom=0.2)
        self.canvas.draw()
    


    # def plot_spec_parts(self , data , sample_rate, x_label='Time', y_label='Frequency'):
    #     if data is None or len(data) == 0:
    #         print("error")
    #         return  # Exit the function if data is empty
    #     # print("hello")
    #     # print(data.shape)
    #     # if data.ndim == 1:
    #     #     data = data.reshape(1025, 1)
    #     print(f"{len(data)}")
    #     self.canvas.axes.clear()
    #     if data.size > 0:
    #         librosa.display.specshow(
    #             data,
    #             sr=sample_rate,
    #             x_axis='time',
    #             y_axis='log',
    #             ax=self.canvas.axes,
    #             cmap='magma'  # Optional: set a color map
    #         )

    #     # Set labels if needed
    #     self.canvas.axes.set_xlabel(x_label)
    #     self.canvas.axes.set_ylabel(y_label)

    #     # Adjust padding to allow room for labels and ticks
    #     self.canvas.figure.subplots_adjust(left=0.1, right=1, top=0.9, bottom=0.2)
    #     self.canvas.draw()




    

