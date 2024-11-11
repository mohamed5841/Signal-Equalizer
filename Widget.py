import pyqtgraph as pg
class widget:
    def __init__(self,widget,x_label="time",y_label="Amplitude"):
        self.widget=widget
        self.pen=pg.mkPen(color=(86, 140, 249), width=2)
        self.plot=widget.plot(pen=self.pen)        
        
        self.widget.setLabel('left', y_label)  
        self.widget.setLabel('bottom', x_label) 
        self.widget.setBackground('b')
        
    
 
