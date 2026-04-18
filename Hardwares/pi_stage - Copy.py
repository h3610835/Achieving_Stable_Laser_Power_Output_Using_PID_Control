
from pipython import GCSDevice, pitools
import time
print(time.time())
STAGES = 'P-561.3CD'
REFMODES = None  # reference first axis or hexapod

pi_device = GCSDevice('E-727')
pi_device.ConnectUSB('0120064165')
print('connected: {}'.format(pi_device.qIDN().strip()))
print('initialize connected stages...')

pitools.startup(pi_device, stages=STAGES, refmodes=REFMODES)
print(pi_device.qSVO())
print(time.time())


pos = pi_device.read('POS? 1')
print('1')
print(pos)
pos = pi_device.read('POS? 2')
print('2')
print(pos)
pos = pi_device.read('POS? 3')
print('3')
print(pos)
pi_device.MOV([1, 2, 3], [50, 50, 100])
print('3')
time.sleep(2)
pos = pi_device.read('POS? 1')
print('1')
print(pos)
pos = pi_device.read('POS? 2')
print('2')
print(pos)
pos = pi_device.read('POS? 3')
print('3')
print(pos)

