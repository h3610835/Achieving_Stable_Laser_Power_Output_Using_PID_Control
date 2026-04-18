from pipython import GCSDevice, pitools
import time
import pandas as pd 

class PiStage():

    def __init__(self):
        STAGES = 'P-561.3CD'
        REFMODES = None  # reference first axis or hexapod
        self.pi_device = GCSDevice('E-727')
        self.pi_device.ConnectUSB('0120064165')
        #print('connected: {}'.format(self.pi_device.qIDN().strip()))
        #print('initialize connected stages...')
        pitools.startup(self.pi_device, stages=STAGES, refmodes=REFMODES)
        #print(self.pi_device.qSVO())
        print('The PI piezo stage has been initialized successfully!')
        '''
        time.sleep(20)
        self.pi_device.send('ATZ ')
        autozero = self.pi_device.send('ATZ? ')
        print(autozero)
        return autozero
        '''
    # return the x,y,z positions
    def check_position(self):
        Info = self.pi_device.read('POS? 1 2 3')
        Pos = Info.split('\n')
        position = []
        del Pos[-1]
        for item in Pos:
            temp = item.split('=')
            position.append(round(eval(temp[1]),3))
        return position

    # The unit of pos is micrometers.
    def move(self, pos):
        if pos[0] <= 100 and pos[1] <= 100 and pos[2] <= 100 and pos[0] >= 0 and pos[1] >= 0 and pos[2] >= 0:
            self.pi_device.MOV([1, 2, 3], pos)
            print('Move successfully!')
        else:
            print('Exceed the Pi Stage movement range!')
        #time.sleep(0.1)
        #print('1',self.check_position())
    
    def moveOneAxis(self, axis, pos):
        self.pi_device.send('MOV '+str(axis)+' '+str(pos))  # When the 'send' command is used, character 'LF' is not necessary.
        #time.sleep(0.1)
        #pos = self.check_position()
        #print(pos)
    
    def move_accuracy(self, pos = [], accuracy = 5):
        if pos[0] <= 100 and pos[1] <= 100 and pos[2] <= 100 and pos[0] >= 0 and pos[1] >= 0 and pos[2] >= 0:
            self.pi_device.MOV([1, 2, 3], pos)
            print('Move successfully!')
        else:
            print('Exceed the Pi Stage movement range!')
        pos_real = self.check_position()
        time.sleep(0.05)
        while abs(pos_real[0] - pos[0]) > accuracy and abs(pos_real[1] - pos[1]) > accuracy and abs(pos_real[2] - pos[2]) > accuracy:
            pos_real = self.check_position()

    # the unit for scan_start, scan_range and speed are um, um and um/s.
    def scanning(self, axis = 1, scan_start = [], scan_range = [], speed = []): # Refer to E727T0005-UserManual-E-727.pdf, Page 102
        PointLength = int(scan_range/speed/0.00005)
        self.pi_device.send('WAV 1 & LIN '+str(PointLength)+' '+str(scan_range)+' '+str(scan_start)+' '+str(PointLength)+' 0 0')
        # xmax = 80
        # xmin = 50
        # length = str(5000)

        # self.pi_device.send('WAV 1 X LIN ' + length + ' ' + str(xmax - xmin) + ' ' + str(xmin) + ' ' + length + ' ' + '0 0')
        # self.pi_device.send('WSL '+str(axis)+' 1')
        #pi.pi_device.send('WTR 0 '+str(speed)+' 1')
        self.pi_device.send('WGR')
        self.pi_device.send('WGO 1 1')
        data = self.pi_device.read('DRR? 1 10000 1')
        return data
    
    def stop_scanning(self):
        pi.pi_device.send('WGO 1 1')

    def close_connection(self):
        self.pi_device.CloseConnection()
        

    
if __name__ == '__main__':
    pi = PiStage()
    #data = pi.scanning(1, 20, 30, 10)
    # data = data.split('\n')
    # print(data)
    # print(len(data))
    #pi.stop_scanning()
    # pi.pi_device.send('RTR 1')
    # pi.pi_device.send('WTR 0 3 1')
    #pi.pi_device.send('WTR?\n')
    #pi.close_connection()
    pi.move([13,17,43])
    time.sleep(5)
    time_seq = []
    pos = []
    pi.move([13,12,43])
    t = time.time()
    for i in range(100):
        time_seq.append(time.time() - t)
        p = pi.check_position()
        pos.append(p[1])
    data = [time_seq, pos]
    dataFrame = pd.DataFrame(data) # data must cannot exceed two one dimensions, two dimensions are acceptable
    with pd.ExcelWriter('E:\\1-Experiment Data\\170-20210902(Kai_Event_Camera_Magnetic_particle)\\raw.xlsx') as writer: # 一个excel写入多页数据
        dataFrame.to_excel(writer, sheet_name='page1', float_format='%.6f')


    # pi.moveOneAxis(3,10)
    # pi.pi_device.send('WAV 4 X SIN_P 2000 20 10 2000 0 1000')
    # pi.pi_device.send('WSL 1 4')
    # pi.pi_device.send('WGO 1 1')
    #pi.pi_device.send('WGO 1 0')



