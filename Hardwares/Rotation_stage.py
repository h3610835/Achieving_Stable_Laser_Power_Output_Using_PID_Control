import pyvisa,time


'''
# 2. set time tagger and write command
tagger = createTimeTagger("1948000SAE")
tagger.reset()
tagger.setTriggerLevel(1, 1.0)
count = Counter(tagger, channels=[1,2], binwidth=int(100000000000), n_values=int(151))
'''
class Rotation_Stage():
    def __init__(self):
        # 1. connect controller
        ss = pyvisa.ResourceManager()
        print(ss.list_resources())
        self.stage = ss.open_resource('ASRL4::INSTR')
        # stage = ss.open_resource('ASRL6::INSTR')
        self.stage.baud_rate = 57600
        self.stage.write_termination = ''
        self.stage.read_termination = ''
        self.stage.timeout = 1000
    
    def set_max_speed(self, command='MX1000;'): # 30.2 s for 360 degrees
        for each in command:
            self.stage.write(each)
            # time.sleep(0.1)
            rcv=self.stage.read_bytes(1)
    
    def set_rotation_range(self, command = 'DX2304000;'): #command='DX576000;' # rotate 180 degrees
        for each  in command:
            # print(each)
            self.stage.write(each)
            #print(a)
            # time.sleep(0.1)
            rcv=self.stage.read_bytes(1)
            #print(rcv)
    
    def check_pos(self):
        # time.sleep(0.05)
        command = 'UX;'
        for each  in command:
            self.stage.write(each)
            #time.sleep(0.1)
            rcv=self.stage.read_bytes(1)
            #print(rcv)
        rcv=self.stage.read_bytes(9)
        pos = []
        for each in rcv:
            if chr(each) != ' ':
                pos.extend(chr(each))
        angle = ''.join(pos)
        return int(angle)
        # print(chr(rcv[0]))
        # print(chr(rcv[1]))
        # print(chr(rcv[2]))
        # print(chr(rcv[3]))
        # print(type(chr(rcv[2])))

if __name__ == '__main__':
    rs = Rotation_Stage()
    pos = rs.check_pos()
    rs.set_max_speed('MX1500;')
    range = 2 # degrees
    rs.set_rotation_range('DX-'+str(3200*range)+';')
    time.sleep(2)
    print(pos - rs.check_pos())

