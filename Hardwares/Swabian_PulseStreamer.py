# import API classes into the current namespace
from pulsestreamer import PulseStreamer, Sequence, TriggerStart
import time

class PulseGenerator():
    def __init__(self):
        ip = '147.8.182.173'
        self.ps = PulseStreamer(ip)
        self.ps.setTrigger(start = TriggerStart.IMMEDIATE)
        self.sequence = Sequence()
        '''
        self.ps.setTrigger()
        '''
        #print(self.ps.getTriggerStart())
        #print(self.ps.getTriggerRearm())
    
    def setTrigger(self, manner=[]): # the type of manner is string.
        if manner == 'internal_immediate':
            self.ps.setTrigger(start = TriggerStart.IMMEDIATE)
        elif manner == 'internal_software':
            self.ps.setTrigger(start = TriggerStart.SOFTWARE)
        elif manner == 'external_rising':
            self.ps.setTrigger(start = TriggerStart.HARDWARE_RISING)
        elif manner == 'external_falling':
            self.ps.setTrigger(start = TriggerStart.HARDWARE_FALLING)
        elif manner == 'external_rising_and_falling':
            self.ps.setTrigger(start = TriggerStart.HARDWARE_RISING_AND_FALLING)
        else:
            pass
    # Example: PulseGenerator.setTrigger('internal')

    def getTrigger(self):
        start_status = self.ps.getTriggerStart()
        return start_status.name

    def pulse(self,channel, high, low, n=[]):
        seq = self.ps.createSequence()
        sequence = [(high,1),(low, 0)]
        seq.setDigital(channel, sequence)
        if len(n)==0:
            self.ps.stream(seq)
        else:
            self.ps.stream(seq, n)
    
    def setSequence_v1(self, unit_seq = [], repetitions = []):
        '''
        Format:
        unit_seq = ([channel_num1, sequence], [channel_num2, sequence], ... , [channel_num3, sequence])
        channel_num1 doesn't need to be 1; The different sequences on differenct channel should have the same length of time.
        The variable "repetitions" is the number of times that unit_seq is repeated.

        Channel Information:
        Laser - 0
        MW - 1
        CCD - 2
        DMD - 3
        '''
        self.seq = self.ps.createSequence()
        for each_seq in unit_seq:
            self.seq.setDigital(each_seq[0], each_seq[1]*int(repetitions))

    def setSequence(self, sequence_laser = [], sequence_MW = [], sequence_CCD = [], repetitions = []):
        #print(sequence_laser)
        #print(sequence_MW)
        #print(sequence_CCD)
        #print(type(sequence_MW))
        Laser_seq, MW_seq = self.complement_sequence(sequence_laser, sequence_MW)
        #print(Laser_seq)
        #print(MW_seq)
        self.seq = self.ps.createSequence()
        sequence_laser_repeated = Laser_seq * int(repetitions)
        sequence_MW_repeated = MW_seq * int(repetitions)
        sequence_CCD_repeated = sequence_CCD * int(repetitions)
        
        #sequence_laser_repeated.insert(0,(100000000, 0))
        #sequence_MW_repeated.insert(0,(100000000, 0))
        #sequence_CCD_repeated.insert(0,(100000000, 0))
        '''
        print('sequence checking')
        print(sequence_laser_repeated)
        print(sequence_MW_repeated)
        print(sequence_CCD_repeated)
        time.sleep(15)
        '''
        self.seq.setDigital(0, sequence_laser_repeated)
        self.seq.setDigital(1, sequence_MW_repeated)
        self.seq.setDigital(2, sequence_CCD_repeated)

    def run(self):
        A = None
        self.ps.stream(self.seq,n_runs=1)
        print('triggered')
        if A is None:
            A = self.seq
        if A == self.seq:
            print('Yes')
        else:
            print('NO')

    '''
    在下面代码中，产生了repetitions次sequence，目的是看一下sequence写入到pulsestreamer中的速度。
    同时比较一下，写入一万次，和重复执行一万次的区别，脉冲质量是否有区别，有无时间误差
    '''
    def generate_sequence(self, all_channel_sequence, repetitions):
        seq = self.ps.createSequence()

        self.ps.stream(seq,n_runs=1)

    def test(self):
        pulse_patt = [(10000000, 0), (20000000000, 1)]
        seq = self.ps.createSequence()
        seq.setDigital(1, pulse_patt)
        #self.sequence.setDigital(0, pulse_patt)
        n_runs = 1
        self.ps.stream(seq,n_runs=n_runs)
        #self.sequence.plot()
        print(self.ps.getTriggerStart())
        
    def pulse_high(self, exposure_time):
        Camera = [(1000000000, 0), (exposure_time, 1)]
        Laser = [(1000000000, 1), (exposure_time, 1)]
        MW = [(1000000000, 1), (exposure_time, 1)]
        seq = self.ps.createSequence()
        seq.setDigital([0], Laser)
        seq.setDigital([1], MW)
        seq.setDigital([2], Camera)
        #self.sequence.setDigital(0, pulse_patt)
        n_runs = 1
        self.ps.stream(seq,n_runs=n_runs)

    def high(self, channels):
        self.ps.constant((channels, 0, 0))

    def complement_sequence(self, Laser_seq, MW_seq):
        total_time_laser = 0
        total_time_MW = 0
        for seq in Laser_seq:
            total_time_laser = seq[0] + total_time_laser
        for seq in MW_seq:
            total_time_MW = seq[0] + total_time_MW
        gap = total_time_laser - total_time_MW
        if total_time_laser > total_time_MW:
            MW_seq.append([gap, 0])
        else:
            Laser_seq.append([-gap, 0])
        print('complement')
        print(Laser_seq)
        print(MW_seq)
        print(type(MW_seq))
        return Laser_seq, MW_seq

    def Sequence(self, sequences = [], n_runs = []): # The format is [[0, seq1], [3, seq3]]
        self.seq = self.ps.createSequence()
        SEQ = self.sequence_processing(sequences)
        for sequence in SEQ:  # The parameter 'sequence' is for each channel, such as laser, MW, camera
            print(sequence[0])
            print(sequence[1])
            seq = sequence[1] * n_runs
            seq.insert(0,(400000000, 0))  # Insert a 400ms period for each channel, such as laser, MW, camera
            #print(sequence[0])
            #print(seq)
             #print('SWABIAN')
            #print(seq)
            self.seq.setDigital(sequence[0], seq)
        
    def sequence_processing(self, sequences):
        total_time = []
        channels = []
        for sequence in sequences:
            single_total_time = 0
            for seq in sequence[1]:
                single_total_time = single_total_time + seq[0]
            total_time.append(single_total_time)
            channels.append(sequence[0])
        max_time = max(total_time)
        max_index = total_time.index(max_time)
        max_channel = channels[max_index]
        for sequence in sequences:
            if max_channel != sequence[0]:
                t = 0
                for seq in sequence[1]:
                    t = t + seq[0]
                gap = max_time - t
                sequence[1].append((gap, 0))

        if channels.count(2) == 0:  #If the sequence for camera has been defined in advance, this paragraph will be ignored.
            sequences.append([2, [(max_time, 1)]])

        return sequences
    
    def upload(self, SEQ = [], n_runs = []):
        self.seq = self.ps.createSequence()
        for sequence in SEQ:  # The parameter 'sequence' is for each channel, such as laser, MW, camera
            print(sequence[0])
            print(sequence[1])
            seq = sequence[1] * n_runs
            self.seq.setDigital(sequence[0], seq)
        self.ps.stream(self.seq,n_runs=1)
    
    def start_now(self):
        self.ps.startNow()
    
    def isRunning(self): # Return true if the pulse generator is running.
        return self.ps.isStreaming()

    def forceFinal(self):
        self.ps.forceFinal()

if __name__=='__main__':
    instrument=PulseGenerator()
    t1 = time.time()
    instrument.test()
    t2 = time.time()
    print(t2 - t1)
    #instrument.high([])

'''  
# A pulse with 10¸ts HIGH and 30¸ts LOW levels
pattern = [(10000, 1), (30000, 0)]




from pulsestreamer import PulseStreamer
ps = PulseStreamer('pulsestreamer')
seq = ps.createSequence()
seq.setDigital(0, pulse_patt)
seq.setDigital(2, pulse_patt)
seq.setAnalog(0, analog_patt)

'''