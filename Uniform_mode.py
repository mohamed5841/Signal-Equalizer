from Mode import mode
class uniform_mode(mode):
    def __init__(self,path):
        self.signal=self.signal_creation(path)
    def signal_creation(self,path):
        return super().signal_creation()