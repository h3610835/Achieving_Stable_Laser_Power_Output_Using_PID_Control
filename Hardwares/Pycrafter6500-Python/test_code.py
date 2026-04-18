import pycrafter6500
import numpy
import PIL.Image


images=[]

#images.append((numpy.asarray(PIL.Image.open("testimage.tif"))//129))

dlp=pycrafter6500.dmd()
a = []
a.append(chr(0))
a.append(chr(0xC0))
a.append(chr(0x11))
a.append(chr(0x02))
a.append(chr(0))
a.append(chr(0))
a.append(chr(0x11))
dlp.test_comunication(a)
'''
dlp.stopsequence()

dlp.changemode(3)

exposure=[1000000]*30
dark_time=[0]*30
trigger_in=[False]*30
trigger_out=[1]*30

dlp.defsequence(images,exposure,trigger_in,dark_time,trigger_out,2)

dlp.startsequence()
'''
