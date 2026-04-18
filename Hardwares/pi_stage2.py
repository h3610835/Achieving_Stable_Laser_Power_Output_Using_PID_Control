from __future__ import print_function
from pipython import GCSDevice, pitools
from time import sleep

STAGES = 'P-562.3CD'
REFMODES = None  # reference first axis or hexapod

pi_device = GCSDevice('E-727')
pi_device.ConnectUSB('0117032110')
print('connected: {}'.format(pi_device.qIDN().strip()))
print('initialize connected stages...')
pitools.startup(pi_device, stages=STAGES, refmodes=REFMODES)

pi_device.dll.send('WAV 1 X LIN 1500 30 15 1500 0 370')
pi_device.dll.send('WSL 1 1')
pi_device.dll.send('WGO 1 1', 'WGR ')
pi_device.dll.send('#9')

pi_device.close()