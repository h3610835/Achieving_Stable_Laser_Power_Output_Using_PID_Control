# import API classes into the current namespace
from pulsestreamer import PulseStreamer, Sequence, TriggerStart
import time

class PulseGenerator():
    def __init__(self):
        ip = '169.254.8.2'
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

    # the pulse generator will work on pulsed mode.
    def pulse(self,channel, high, low, n=[]):
        seq = self.ps.createSequence()
        sequence = [(high,1),(low, 0)]
        seq.setDigital(channel, sequence)
        if len(n)==0:
            self.ps.stream(seq)
        else:
            self.ps.stream(seq, n)
    
    # Set the pulse generator to be ready for run. Once the pulse generator receives the trigger signal, the pulse generator will work.
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

    # Turn on the channels listed in parameter 'channels'. Parameter 'channels' is a list.
    def high(self, channels):
        self.ps.constant((channels, 0, 0))

    # Upload the sequences to the pulse generator
    def upload_seq(self, SEQ = [], n_runs = []):
        self.seq = self.ps.createSequence()
        for sequence in SEQ:  # The parameter 'sequence' is for each channel, such as laser, MW, camera
            print(sequence[0])
            print(sequence[1])
            seq = sequence[1] * n_runs
            self.seq.setDigital(sequence[0], seq)
        self.ps.stream(self.seq,n_runs=1)
    
    # Internal trigger
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