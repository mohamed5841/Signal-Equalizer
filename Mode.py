from PyQt5 import QtCore
from abc import ABC, abstractmethod

class mode(ABC):
    
    @abstractmethod
    def signal_creation(self):
        pass
    @abstractmethod       
    def playpause(self):

        pass
    @abstractmethod
    def reset(self):
        pass
    @abstractmethod
    def set_speed(self):
        pass
