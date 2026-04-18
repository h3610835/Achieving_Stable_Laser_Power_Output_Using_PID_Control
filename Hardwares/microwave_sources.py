'''
This file is to control the microwave source, ROHDE&SCHWARZ SMBV100A
'''

import pyvisa

class SMIQ():

    def __init__(self, visa_address=[]):
        rm = pyvisa.ResourceManager()
        self.my_instrument = rm.open_resource('GPIB0::28::INSTR')

    def SetMode(self):
        self.my_instrument.write('FREQ:MODE SWE')

    def GetMode(self):
        pass

    def SetFrequence(self, frequency):
        self.frequency = frequency
        self.my_instrument.write('FREQ ' + self.frequency)

    def GetFrequency(self):
        self.frequency = self.my_instrument.query('FREQ?')
        return self.frequency

    def SetPower(self, power):
        self.power = power
        self.my_instrument.write('SOUR:POW:POW ' + self.power)

    def GetPower(self):
        self.power = self.my_instrument.query('POW:PEP?')
        return self.power

    def on(self):
        self.my_instrument.write('OUTP ON')

    def off(self):
        self.my_instrument.write('OUTP OFF')
    
    # The format of list_para is [(110,-10),(130,-10),(150,-20),(150,-20)]. [(freq in MHz), (power in dBm)]
    def list_mode(self, list_para = []):
        self.my_instrument.write('SOUR1:LIST:SEL "New_List"')
        str_freq = 'SOUR1:LIST:FREQ'
        str_power = 'SOUR1:LIST:POW'
        for item in list_para:
            str_freq_temp = ' {} MHz,'.format(item[0])
            str_power_temp = ' {} dBm,'.format(item[1])
            str_freq += str_freq_temp
            str_power += str_power_temp
        str_freq = str_freq[:-1]
        str_power = str_power[:-1]
        #print(str_freq)
        #print(str_power)
        self.my_instrument.write(str_freq)
        self.my_instrument.write(str_power)
        self.my_instrument.write('SOUR1:LIST:MODE STEP')
        self.my_instrument.write('SOUR:LIST:TRIG:SOUR EXT')
        self.my_instrument.write('SOUR1:FREQ:MODE LIST')
    
    def deactive_list_mode(self):
        self.my_instrument.write('SOUR1:FREQ:MODE CW')

if __name__ == '__main__':
    smiq = SMIQ()
    smiq.SetPower('-20')
    power = smiq.GetPower()
    smiq.my_instrument.write('SOUR1:LIST:SEL "CW_ODMR"')
    smiq.my_instrument.write('SOUR1:LIST:FREQ 100 MHz, 110 MHz, 120 MHz')
    smiq.my_instrument.write('SOUR1:LIST:POW 2dBm, -1dBm, 0dBm')
    smiq.my_instrument.write('SOUR1:LIST:DWEL 2000ms')
    
    smiq.my_instrument.write('SOUR1:LIST:MODE STEP')
    smiq.my_instrument.write('SOUR:LIST:TRIG:SOUR EXT')
    smiq.my_instrument.write('SOUR1:FREQ:MODE LIST')
    #smiq.my_instrument.write('SOUR1:LIST:TRIG:EXEC')
    #smiq.my_instrument.write('SOUR1:FREQ:MODE CW')
    print(smiq.my_instrument.query('*IDN?'))
    print(power) 
    smiq.list_mode([(110,-10),(130,-10),(150,-20),(150,-20),(150,-20)])
    smiq.deactive_list_mode()