import pycrafter6500
import numpy
import PIL.Image
import usb

dev = usb.core.show_devices()
print('dev:',dev)

images=[]

images.append((numpy.asarray(PIL.Image.open("G:\\OneDrive - connect.hku.hk\\25-Python Program\\1-Rabi\\Examples\\Widefield\\Hardwares\\Pycrafter6500-Python\\Pycrafter6500-master\\Fringe_period176_ori90_phase240.bmp"))//129))

print(images[0].shape)

dlp=pycrafter6500.dmd()

dlp.stopsequence()

dlp.changemode(3)

exposure=[100000]*1
dark_time=[100000]*1
trigger_in=[False]*1
trigger_out=[False]*1

dlp.defsequence(images,exposure,trigger_in,dark_time,trigger_out,2)

dlp.startsequence()

