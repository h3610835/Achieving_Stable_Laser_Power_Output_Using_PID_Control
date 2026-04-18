from ctypes import*
import numpy

class CCD():
    def __init__(self):
        
        self.dll=windll.LoadLibrary("C:\\Program Files\\Andor SOLIS\\atmcd64d_legacy.dll")
        self.dll.Initialize()
        self.dll.SetShutter(1,1,0,0)
        self.dll.SetCountConvertMode(2)
        hbin = 1
        vbin = 1
        xstart = 1
        xend = 512
        ystart = 1
        yend = 512

        self.dll.SetImage(hbin,vbin,xstart,xend,ystart,yend)
        
        self.dll.SetPreAmpGain(2)
        self.dll.SetOutputAmplifier(1)

        self.cooler_on()
        self.set_fan_mode('off')
        self.set_number_prescans(1)
        self.set_number_accumulations(1)
        self.set_exposure(0.05)
        self.set_acquisition_mode('Single')
        self.set_trigger_mode('Internal')
        self.set_frame_transfer_mode('off')
        self.set_readout_mode()

    
    def set_exposure(self, exposure_time): # exposure time in ms unit
        exp = c_float(exposure_time/1000)
        self.dll.SetExposureTime(exp)
    
    def set_readout_mode(self):
        self.dll.SetReadMode(4)

    def set_acquisition_mode(self, mod = []):
        if mod == 'Single':
            self.dll.SetAcquisitionMode(1)
        elif mod == 'Accumulate':
            self.dll.SetAcquisitionMode(2)
        elif mod == 'Kinetic':
            self.dll.SetAcquisitionMode(3)
        elif mod == 'Fast Kinetics':
            self.dll.SetAcquisitionMode(4)
        elif mod == 'Run till abort':
            self.dll.SetAcquisitionMode(5)
    
    def set_frame_transfer_mode(self, mod = []):
        if mod == 'on':
            self.dll.SetFrameTransferMode(1)
        elif mod == 'off':
            self.dll.SetFrameTransferMode(0)
    
    def set_trigger_mode(self, mod = []):
        if mod == 'Internal':
            self.dll.SetTriggerMode(0)
        elif mod == 'External':
            self.dll.SetTriggerMode(1)
            print('external')
        elif mod == 'External Start':
            self.dll.SetTriggerMode(6)
        elif mod == 'Bulb': # External Exposure
            self.dll.SetTriggerMode(7)
        elif mod == 'External FVB EM':
            self.dll.SetTriggerMode(9)
        elif mod == 'Software Trigger':
            self.dll.SetTriggerMode(10)
    
    def set_number_accumulations(self, num = []):
        self.dll.SetNumberAccumulations(num)
    
    def set_number_prescans(self, num = []): 
        # This function will set the number of scans acquired before data is to be retrieved. This 
        # will only take effect if the acquisition mode is Kinetic Series. 
        self.dll.SetNumberPrescans(num)

    def set_output_amplifier(self, num):
        self.dll.SetOutputAmplifier(num)

    def get_number_amplifier(self):
        amp = c_int()
        self.dll.GetNumberAmp(byref(amp))
        print('current output amplifier:',amp)
        return amp

    def get_temperature(self):
        temperature = c_int()
        self.dll.GetTemperature(byref(temperature))
        return temperature

    def set_temperature(self, temperature = []):
        self.dll.SetTemperature(temperature)
    
    def cooler_on(self):
        self.dll.CoolerON()

    def cooler_off(self):
        self.dll.CoolerOFF()

    def set_fan_mode(self, mod = []):
        if mod == 'high':
            self.dll.SetFanMode(0)
        elif mod == 'low':
            self.dll.SetFanMode(1)
        elif mod == 'off':
            self.dll.SetFanMode(2)

    def set_frame_transfer_mode(self, mod = []):
        self.dll.SetFrameTransferMode(mod)
    
    def snapshot(self):
        self.set_acquisition_mode('Single')
        self.dll.StartAcquisition()
        dim=int(512*512)
        cimagearray=c_int*dim
        cimage=cimagearray()
        self.dll.WaitForAcquisition()
        print(self.dll.GetAcquiredData(pointer(cimage), dim))
        while self.dll.GetAcquiredData(pointer(cimage), dim) == 20072:
            pass
        frame = numpy.array(cimage)
        frame = frame.reshape(512,512)
        return frame
    
    def live_start(self):
        self.set_acquisition_mode('Run till abort')
        self.dll.StartAcquisition()
        
    def live_readout(self):
        dim=int(512*512)
        cimagearray=c_int*dim
        cimage=cimagearray()
        self.dll.WaitForAcquisition()
        self.dll.GetMostRecentImage(pointer(cimage), dim)
        while self.dll.GetMostRecentImage(pointer(cimage), dim) != 20002:
            pass
        frame = numpy.array(cimage)
        frame = frame.reshape(512,512)
        return frame
    
    def live_stop(self):
        self.dll.AbortAcquisition()
    
    def close(self):
        self.dll.ShutDown()

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    ccd = CCD()
    tem = ccd.get_temperature()
    ccd.set_temperature(-70)
    print('tem:',tem)
    ccd.get_temperature()
    tem = ccd.get_temperature()
    print('tem:',tem)
    ccd.cooler_on()
    tem = ccd.get_temperature()
    image = ccd.snapshot()
    plt.imshow(image)
    plt.show()
    print('tem:',tem)
    ccd.set_fan_mode('low')
    ccd.set_trigger_mode('External')
    frame = ccd.snapshot()
    plt.imshow(frame)
    plt.show()
    ccd.close()
    


    

