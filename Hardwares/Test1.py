import time
import numpy
import PIL.Image
import hid
import openpyxl
import numpy as np
import pandas as pd 
from matplotlib import pyplot as plt

VendorID = 0x0451
ProductID = 0xc900
for d in hid.enumerate():
    keys = list(d.keys())
    keys.sort()
h = hid.device()
h.open(VendorID, ProductID)
h.set_nonblocking(1)

imagedata = []
block_64 = []

string = '00 13 fc 01 2b 1a f8 01 53 70 6c 64 80 07 38 04 e4 10 00 00 ff ff ff ff ff ff ff ff 00 00 00 00 00 02 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 0f 00 00 01 00 01 80'
l = string.split(' ')
block_start = []
for each in l:
    block_start.append(eval('0x'+each))
block_start = [0]+block_start
print(block_start)
print(len(block_start))

block_image = [0x0f, 0x00, 0x01, 0x80]
for i in range(16):
    block_64.extend(block_image)
block_64 = [0]+block_64
print(block_64)
print(len(block_64))


# middle block start
string = '00 1a fc 01 2b 1a f8 01 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80'
l = string.split(' ')
block_middle_start = []
for each in l:
    block_middle_start.append(eval('0x'+each))
print(block_middle_start)
print(len(block_middle_start))
block_middle_start = [0] + block_middle_start

# last block start
string = '00 1b 58 01 2b 1a 54 01 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80'
l = string.split(' ')
block_end_start = []
for each in l:
    block_end_start.append(eval('0x'+each))
print(block_end_start)
print(len(block_end_start))
block_end_start = [0] + block_end_start

# last block
string = '0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 80 0f 00 01 00 70 c8 d4 00 7c c8 d4 00 f6 d5 27 77 00 00 00 00 00 00 00 00 00 00 00 00 60 c9 d4 00 e8 7d c8 06 e8 7d c8 06'
l = string.split(' ')
block_end = []
for each in l:
    block_end.append(eval('0x'+each))
print(block_end)
print(len(block_end))
block_end = [0]+block_end

# start sequence
string = '00 1d 03 00 24 1a 02 00 00 00 00 00 04 d4 c4 06 1c ca d4 00 f6 d5 27 77 00 00 00 00 00 00 00 00 00 00 00 00 d0 cc d4 00 78 7e c8 06 78 7e c8 06 68 ca d4 00 09 74 61 75 00 00 e6 00 00 00 00 00'
l = string.split(' ')
block_start_sequence = []
for each in l:
    block_start_sequence.append(eval('0x'+each))
print(block_start_sequence)
print('block_start_sequence:',len(block_start_sequence))
block_start_sequence = [0]+block_start_sequence

# stop sequence
string = '00 1d 03 00 24 1a 00 00 00 00 00 00 04 d4 c4 06 1c ca d4 00 f6 d5 27 77 00 00 00 00 00 00 00 00 00 00 00 00 d0 cc d4 00 78 7e c8 06 78 7e c8 06 68 ca d4 00 09 74 61 75 00 00 e6 00 00 00 00 00'
l = string.split(' ')
block_stop_sequence = []
for each in l:
    block_stop_sequence.append(eval('0x'+each))
print(block_stop_sequence)
print('block_start_sequence:',len(block_stop_sequence))
block_stop_sequence = [0]+block_stop_sequence

# set on-the-fly pattern mode
string_mode = '00 1d 03 00 1b 1a 03 00 00 00 00 00 04 d4 c4 06 1c ca d4 00 f6 d5 27 77 00 00 00 00 00 00 00 00 00 00 00 00 d0 cc d4 00 78 7e c8 06 78 7e c8 06 68 ca d4 00 09 74 61 75 00 00 e6 00 00 00 00 00'
l = string_mode.split(' ')
block_mode = []
for each in l:
    block_mode.append(eval('0x'+each))
print(block_mode)
print('block_start_sequence:',len(block_mode))
block_mode = [0]+block_mode

# 1A34
string_pattern = '00 1d 0e 00 34 1a 00 00 40 42 0f 11 00 00 00 00 00 00 00 00 f6 d5 27 77 00 00 00 00 00 00 00 00 00 00 00 00 d0 cc d4 00 78 7e c8 06 78 7e c8 06 68 ca d4 00 09 74 61 75 00 00 e6 00 00 00 00 00'
l = string_pattern.split(' ')
block_pattern = []
for each in l:
    block_pattern.append(eval('0x'+each))
print(block_pattern)
print('block_start_sequence:',len(block_pattern))
block_pattern = [0]+block_pattern

# 1A2A
string_BMP = '00 1d 08 00 2A 1a 00 00 14 11 00 00 ff ff 00 00 00 00 00 00 f6 d5 27 77 00 00 00 00 00 00 00 00 00 00 00 00 d0 cc d4 00 78 7e c8 06 78 7e c8 06 68 ca d4 00 09 74 61 75 00 00 e6 00 00 00 00 00'
l = string_BMP.split(' ')
block_BMP = []
for each in l:
    block_BMP.append(eval('0x'+each))
print(block_BMP)
print('block_start_sequence:',len(block_BMP))
block_BMP = [0]+block_BMP

# 1A31
string_LUT = '00 1d 08 00 31 1a 01 00 00 00 00 00 04 d4 00 00 00 00 00 00 f6 d5 27 77 00 00 00 00 00 00 00 00 00 00 00 00 d0 cc d4 00 78 7e c8 06 78 7e c8 06 68 ca d4 00 09 74 61 75 00 00 e6 00 00 00 00 00'
l = string_LUT.split(' ')
block_LUT = []
for each in l:
    block_LUT.append(eval('0x'+each))
print(block_LUT)
print('block_start_sequence:',len(block_LUT))
block_LUT = [0]+block_LUT




# 
h.write(block_mode)
h.write(block_pattern)
h.write(block_BMP)

# 504

h.write(block_start)
for i in range(7):
    h.write(block_64)
# 4032
for j in range(7):
    h.write(block_middle_start)
    for i in range(7):
        h.write(block_64)
# 4372
h.write(block_end_start)
for i in range(4):
    h.write(block_64)
h.write(block_end)

h.write(block_LUT)

h.write(block_stop_sequence)
#h.write(block_start_sequence)
