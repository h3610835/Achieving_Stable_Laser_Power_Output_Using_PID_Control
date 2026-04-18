from __future__ import print_function
from pipython import GCSDevice, pitools
from time import sleep
import matplotlib.pyplot as plt
import numpy as np

# 1. 预设
STAGES = 'P-561.3CD'
REFMODES = None  # reference first axis or hexapod
NUMPOINTS = 1000  # number of points for one sine period as integer
STARTPOS = (0.0, 0.0, 0.0)  # start position of the circular motion as float for both axes
AMPLITUDE = (200, 200, 200)  # amplitude of the circular motion as float for both axes
NUMCYLES = 1  # number of cycles for wave generator output
TABLERATE = 10  # duration of a wave table point in multiples of servo cycle times as integer

# 2. 连接
pi_device = GCSDevice('E-727')
pi_device.ConnectUSB('0120064165')
print('connected: {}'.format(pi_device.qIDN().strip()))
print('initialize connected stages...')
pitools.startup(pi_device, stages=STAGES, refmodes=REFMODES)

# 3. 波形输出并记录位置
# print(pi_device.read('DRC? 2'))
print(pi_device.qSVO())
pi_device.send('RTR 1')
# pi_device.send('WAV 1 X LIN 10000 200 0 10000 0 0')
# pi_device.send('WAV 1 & LIN 10000 0 200 10000 0 0')
xmax = 70
xmin = 30
length = str(60000)


pi_device.send('WAV 2 X LIN ' + str(length) + ' ' + str(xmax - xmin) + ' ' + str(xmin) + ' ' + str(length) + ' ' + '0 0')
#pi_device.send('WAV 2 & LIN 1000 0 ' + str(xmax) + ' 1000 ' + str(xmax) + ' 0')
pi_device.send('WSL 3 2')
pi_device.MOV('3', 20)
sleep(5)
print(pi_device.read('POS?'))
# print(pi_device.read('WTR? 1'))
pi_device.send('WGR')
pi_device.send('WGO 3 1')
# print(pi_device.read('RTR?'))
data = pi_device.read('DRR? 1 27000 1')
print(data)

pi_device.send('WGO 3 0')
'''
data = data.split('\n')
#print(data)
pi_device.CloseConnection()

# 4. 存储数据
array = []
f = open('1000.txt', 'w')

for each in data:
    if each.startswith('#'):
        continue
    elif each == chr(10):
        continue
    else:
        f.write(each + '\n')
        try:
            array.append(float(each))
        except:
            pass

f.close()
print(len(array))
#print(array)
i = 0
dat_new = []
while i<4000:
    if i%10 == 0:
        dat_new.append(array[i])
    i = i + 1
print(len(dat_new))
# 5.画图
y1 = array
y2 = np.linspace(xmin, xmax, int(length))
a = np.zeros(5000)
a = a + xmax
y2 = np.r_[y2, a]
x = np.linspace(0, 0.49995, 10000)
# print(x)
plt.figure()
plt.plot(x, y1)
plt.plot(x, y2)
plt.xlabel('time\\s')
plt.ylabel('position\\micrometer')
plt.title('relationship between wave generator and position')
plt.grid()
plt.show()
'''

"""
assert 1 == len(pi_device.axes[:1]), 'this sample requires two connected axes'
wavegens = 1
wavetables = 1
print('define sine and cosine waveforms for wave tables {}'.format(wavetables))

pi_device.WAV_LIN(table=wavetables[0], firstpoint=0, numpoints=NUMPOINTS, append='X',
                    speedupdown=100, amplitude=AMPLITUDE[0], offset=STARTPOS[0], seglength=NUMPOINTS)
pi_device.WAV_SIN_P(table=wavetables[1], firstpoint=NUMPOINTS / 4, numpoints=NUMPOINTS, append='X',
                    center=NUMPOINTS / 2, amplitude=AMPLITUDE[1], offset=STARTPOS[1], seglength=NUMPOINTS)
pi_device.WAV_SIN_P(table=wavetables[2], firstpoint=NUMPOINTS / 4, numpoints=NUMPOINTS, append='X',
                    center=NUMPOINTS / 2, amplitude=AMPLITUDE[2], offset=STARTPOS[2], seglength=NUMPOINTS)



pitools.waitonready(pi_device)
if pi_device.HasWSL():  # you can remove this code block if your controller does not support WSL()
    print('connect wave generators {} to wave tables {}'.format(wavegens, wavetables))
    pi_device.WSL(wavegens, wavetables)

if pi_device.HasWGC():  # you can remove this code block if your controller does not support WGC()
    print('set wave generators {} to run for {} cycles'.format(wavegens, NUMCYLES))
    pi_device.WGC(wavegens, [NUMCYLES] * len(wavegens))

# startpos = (STARTPOS[0], STARTPOS[1] + AMPLITUDE[1] / 2.0, STARTPOS[2] + AMPLITUDE[2] / 2.0)

startpos = (STARTPOS[0])
print('move axes {} to their start positions {}'.format(pi_device.axes[:1], startpos))
pi_device.MOV(pi_device.axes[:1], startpos)
pitools.waitontarget(pi_device, pi_device.axes[:1])
print('start wave generators {}'.format(wavegens))
pi_device.WGO(wavegens, mode=[1] * len(wavegens))

while any(list(pi_device.IsGeneratorRunning(wavegens).values())):
  print('.', end='')
  sleep(1.0)
print('\nreset wave generators {}'.format(wavegens))
pi_device.WGO(wavegens, mode=[0] * len(wavegens))
print('done')
pi_device.CloseConnection()
print(data)
"""