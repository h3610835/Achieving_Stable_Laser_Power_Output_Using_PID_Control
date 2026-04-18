'''
This file is for the microwave source, SynthNV Pro.
'''
import serial
from PyQt5.QtWidgets import QMessageBox

class SynthNV_Pro_MicrowaveSource():

    def __init__(self):
        self.ser = serial.Serial('com12',9600, timeout=1)
        self.ser.write(bytes('f250', encoding = "utf8"))
        self.ser.write(bytes('W-20', encoding = "utf8"))
        self.ser.write(bytes('E0', encoding = "utf8"))

    def Query(self):
        self.ser.write(bytes('f?', encoding = "utf8"))
        self.ser.write(bytes('W?', encoding = "utf8"))
        self.ser.write(bytes('E?', encoding = "utf8"))
        freq_bytes, power_bytes, state_bytes = self.ser.readlines()
        freq = bytes.decode(freq_bytes)
        power = bytes.decode(power_bytes)
        state = bytes.decode(state_bytes)
        return freq[0:-1], power[0:-1], state[0:-1]
    
    def ON(self):
        self.ser.write(bytes('E1', encoding = "utf8"))
    
    def OFF(self):
        self.ser.write(bytes('E0', encoding = "utf8"))

    def Set(self, power = 0): # the type of power is a str
        #self.my_instrument.write(channel+':VOLTage '+Voltage)
        if float(power) <= 14:
            self.ser.write(bytes('W'+power, encoding = "utf8"))
        else:
            QMessageBox.warning(self,"Warning","The Power mustn't bigger than 14dBm!",QMessageBox.Yes | QMessageBox.No)
            print('less than 14dBm')

if __name__ == '__main__':
    pass
