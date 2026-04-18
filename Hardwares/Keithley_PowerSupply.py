'''
This file is for the power supply, RS Pro RSPD 3303C.
'''
import pyvisa
from PyQt5.QtWidgets import QMessageBox

class Keithley_PowerSupply():

    def __init__(self):
        rm = pyvisa.ResourceManager()
        self.my_instrument = rm.open_resource('GPIB0::22::INSTR')

    def Query(self):
        Current = self.my_instrument.query('CURR?')
        Voltage = self.my_instrument.query('VOLTAGE? ')
        State = self.my_instrument.query('OUTPUT?')
        return Current, Voltage, State
    
    def ON(self):
        self.my_instrument.write('OUTPUT ON')
    
    def OFF(self):
        self.my_instrument.write('OUTPUT OFF')

    def Set(self, Voltage = 0, Current = 0):
        #self.my_instrument.write(channel+':VOLTage '+Voltage)
        # print(Voltage)
        # print(Current)
        if float(Voltage) <= 0.85:
            # print('11')
            self.my_instrument.write('VOLT '+Voltage+'V')
            self.my_instrument.write('CURR '+Current+'A')
        else:
            print(2)
            
            '''
            QMessageBox.warning(self,"Warning","The Voltage mustn't bigger than 0.08V!",QMessageBox.Yes | QMessageBox.No)
            '''



if __name__ == '__main__':
    power = Keithley_PowerSupply()
    #power.my_instrument.write('OUTPut CH1, ON')
    #power.my_instrument.write('CH1:VOLTage 1')
    power.my_instrument.write('VOLTAGE: 0.5')

