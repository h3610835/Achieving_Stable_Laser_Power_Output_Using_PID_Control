import time
import numpy
import PIL.Image
import hid
import openpyxl
import numpy as np
import pandas as pd 
from matplotlib import pyplot as plt


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
string_pattern = '00 1d 0e 00 34 1a 00 00 40 42 0f 11 40 42 0f 00 00 00 00 00 f6 d5 27 77 00 00 00 00 00 00 00 00 00 00 00 00 d0 cc d4 00 78 7e c8 06 78 7e c8 06 68 ca d4 00 09 74 61 75 00 00 e6 00 00 00 00 00'
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


def convlen(a,l):
    b=bin(a)[2:]
    padding=l-len(b)
    b='0'*padding+b

    return b

##function that converts a bit string into a given number of bytes

def bitstobytes(a):
    bytelist=[]
    if len(a)%8!=0:
        padding=8-len(a)%8
        a='0'*padding+a
    for i in range(len(a)//8):
        bytelist.append(int(a[8*i:8*(i+1)],2))

    bytelist.reverse()

    return bytelist

##function that encodes a 8 bit numpy array matrix as a enhanced run lenght encoded string of bits

def mergeimages(images):
    mergedimage=numpy.zeros((1080,1920,3),dtype='uint8')

    for i in range(len(images)):
        if i<8:
            mergedimage[:,:,2]=mergedimage[:,:,2]+images[i]*(2**i)
            dataFrame = pd.DataFrame(images[i]*(2**i))
            '''
            with pd.ExcelWriter('D:\\OneDrive - connect.hku.hk\\25-Python Program\\21-Python Program（HKU LAB）\\1-images_raw_'+str(i)+'.xlsx') as writer: # 一个excel写入多页数据
                dataFrame.to_excel(writer, sheet_name='page1', float_format='%.6f')
            dataFrame = pd.DataFrame(images[i]*(2**i))
            with pd.ExcelWriter('D:\\OneDrive - connect.hku.hk\\25-Python Program\\21-Python Program（HKU LAB）\\1-images_2_i_'+str(i)+'.xlsx') as writer: # 一个excel写入多页数据
                dataFrame.to_excel(writer, sheet_name='page1', float_format='%.6f')
            '''
        if i>7 and i<16:
            mergedimage[:,:,1]=mergedimage[:,:,1]+images[i]*(2**(i-8))
        if i>15 and i<24:
            mergedimage[:,:,0]=mergedimage[:,:,0]+images[i]*(2**(i-16))

    return mergedimage

def encode(image): 


## header creation
    bytecount=0    
    bitstring=[]

    bitstring.append(0x53)
    bitstring.append(0x70)
    bitstring.append(0x6c)
    bitstring.append(0x64)
    
    width=convlen(1920,16)
    width=bitstobytes(width)
    for i in range(len(width)):
        bitstring.append(width[i])

    height=convlen(1080,16)
    height=bitstobytes(height)
    for i in range(len(height)):
        bitstring.append(height[i])


    total=convlen(0,32)
    total=bitstobytes(total)
    for i in range(len(total)):
        bitstring.append(total[i])        

    for i in range(8):
        bitstring.append(0xff)

    for i in range(4):    ## black curtain
        bitstring.append(0x00)

    bitstring.append(0x00)

    bitstring.append(0x02) ## enhanced rle

    bitstring.append(0x01)

    for i in range(21):
        bitstring.append(0x00)



    n=0
    i=0
    j=0

    while i <1080:
        while j <1920:
            if i>0 and numpy.all(image[i,j,:]==image[i-1,j,:]):
                while j<1920 and numpy.all(image[i,j,:]==image[i-1,j,:]):
                    n=n+1
                    j=j+1

                bitstring.append(0x00)
                bitstring.append(0x01)
                bytecount+=2
                
                if n>=128:
                    byte1=(n & 0x7f)|0x80
                    byte2=(n >> 7)
                    bitstring.append(byte1)
                    bitstring.append(byte2)
                    bytecount+=2
                    
                else:
                    bitstring.append(n)
                    bytecount+=1
                n=0

            
            else:
                if j<1919 and numpy.all(image[i,j,:]==image[i,j+1,:]):
                    n=n+1
                    while j<1919 and numpy.all(image[i,j,:]==image[i,j+1,:]):
                        n=n+1
                        j=j+1
                    if n>=128:
                        byte1=(n & 0x7f)|0x80
                        byte2=(n >> 7)
                        bitstring.append(byte1)
                        bitstring.append(byte2)
                        bytecount+=2
                        
                    else:
                        bitstring.append(n)
                        bytecount+=1

                    bitstring.append(image[i,j-1,0])
                    bitstring.append(image[i,j-1,1])
                    bitstring.append(image[i,j-1,2])
                    bytecount+=3
                    
                    j=j+1
                    n=0

                else:
                    if j>1917 or numpy.all(image[i,j+1,:]==image[i,j+2,:]) or numpy.all(image[i,j+1,:]==image[i-1,j+1,:]):
                        bitstring.append(0x01)
                        bytecount+=1
                        bitstring.append(image[i,j,0])
                        bitstring.append(image[i,j,1])
                        bitstring.append(image[i,j,2])
                        bytecount+=3
                        
                        j=j+1
                        n=0

                    else:
                        bitstring.append(0x00)
                        bytecount+=1

                        toappend=[]

                        
                        while numpy.any(image[i,j,:]!=image[i,j+1,:]) and numpy.any(image[i,j,:]!=image[i-1,j,:]) and j<1919:
                            n=n+1
                            toappend.append(image[i,j,0])
                            toappend.append(image[i,j,1])
                            toappend.append(image[i,j,2])
                            j=j+1

                        if n>=128:
                            byte1=(n & 0x7f)|0x80
                            byte2=(n >> 7)
                            bitstring.append(byte1)
                            bitstring.append(byte2)
                            bytecount+=2
                                
                        else:
                            bitstring.append(n)
                            bytecount+=1

                        for k in toappend:
                            bitstring.append(k)
                            bytecount+=1
                        n=0
        j=0
        i=i+1
        '''
        bitstring.append(0x00)
        bitstring.append(0x00)
        bytecount+=2
        '''
    bitstring.append(0x00)
    bitstring.append(0x01)
    bitstring.append(0x00)
    bytecount+=3

    while (bytecount)%4!=0:
        bitstring.append(0x00)
        bytecount+=1        

    size=bytecount

    total=convlen(size,32)
    total=bitstobytes(total)
    for i in range(len(total)):
        bitstring[i+8]=total[i]    
    print('bitstring--------------------------')
    #print(bitstring)
    return bitstring, bytecount

# try opening a device, then perform write and read
class DMD():
    def __init__(self, VendorID = 0x0451, ProductID = 0xc900):
        # enumerate USB devices
        for d in hid.enumerate():
            keys = list(d.keys())
            keys.sort()
        self.h = hid.device()
        self.h.open(VendorID, ProductID)
        self.h.set_nonblocking(1)
        self.seqByte = 0x00

    def command(self, WR = [], Payload = []):
        reportID = 0
        seqByte = 0x02
        if WR == 'r':
            flagByte = 0xC0
        elif WR == 'w':
            flagByte = 0x00
        else:
            print('Warning! No valid write or read sign!')
        temp=bitstobytes(convlen(len(Payload),16))
        lenBytes = [temp[0], temp[1]]
        commBytes = Payload[0:2]
        data = Payload[2:]
        buffer = [reportID, flagByte, seqByte] + lenBytes + commBytes
        '''
        print('Command data-------------------------------------------------------------')
        print(Payload)
        print('END-----------------------------------------------------------------')
        '''
        #print('Command data-------------------------------------------------------------')
        if len(buffer)+len(data)<66:
            for i in range(len(data)):
                buffer.append(data[i])

            for i in range(65-len(buffer)):
                buffer.append(0x00)

            #print('lenght of buffer', len(buffer))
            #print('Command:', buffer)
            self.h.write(buffer)

        else:
            for i in range(65-len(buffer)):
                buffer.append(data[i])
            #print('lenght of buffer', len(buffer))
            #print('Command:', buffer)
            self.h.write(buffer)
            buffer = [reportID]

            j=0
            while j<len(data)-58:
                buffer.append(data[j+58])
                j=j+1
                if j%64==0:
                    #print('lenght of buffer', len(buffer))
                    #print('Command:', buffer)
                    self.h.write(buffer)
                    buffer = [reportID]

            if j%64!=0:

                while j%64!=0:
                    buffer.append(0x00)
                    j=j+1

                #print('lenght of buffer', len(buffer))
                #print('Command:', buffer) 
                self.h.write(buffer)       
        #print('END-----------------------------------------------------------------')
        time.sleep(0.1)

    def defsequence(self,images,exp,ti,dt,to,rep):
        self.stop_display()
        arr=[]

        for i in images:
            arr.append(i)
        num=len(arr)
        encodedimages=[]
        sizes=[]

        for i in range((num-1)//24+1):
            print ('merging...')
            if i<((num-1)//24):
                imagedata=mergeimages(arr[i*24:(i+1)*24])
            else:
                imagedata=mergeimages(arr[i*24:])
            print ('encoding...')
            imagedata,size=encode(imagedata)
            encodedimages.append(imagedata)
            sizes.append(size)
        print('size of image: ',size)
        #print(imagedata)
        # 1A34  #0
        string_pattern = '00 1d 0e 00 34 1a 00 00 40 42 0f 11 40 42 0f 00 00 00 00 00 f6 d5 27 77 00 00 00 00 00 00 00 00 00 00 00 00 d0 cc d4 00 78 7e c8 06 78 7e c8 06 68 ca d4 00 09 74 61 75 00 00 e6 00 00 00 00 00'
        l = string_pattern.split(' ')
        block_pattern = []
        for each in l:
            block_pattern.append(eval('0x'+each))
        print(block_pattern)
        print('block_start_sequence:',len(block_pattern))
        block_pattern = [0]+block_pattern

        # 1A34  #1
        string_pattern = '00 1d 0e 00 34 1a 01 00 40 42 0f 11 40 42 0f 00 00 08 00 00 f6 d5 27 77 00 00 00 00 00 00 00 00 00 00 00 00 d0 cc d4 00 78 7e c8 06 78 7e c8 06 68 ca d4 00 09 74 61 75 00 00 e6 00 00 00 00 00'
        l = string_pattern.split(' ')
        block_pattern = []
        for each in l:
            block_pattern.append(eval('0x'+each))
        print(block_pattern)
        print('block_start_sequence:',len(block_pattern))
        block_pattern_1 = [0]+block_pattern

        # 1A2A
        string_BMP = '00 1d 08 00 2A 1a 00 00 3d ba 03 00 ff ff 00 00 00 00 00 00 f6 d5 27 77 00 00 00 00 00 00 00 00 00 00 00 00 d0 cc d4 00 78 7e c8 06 78 7e c8 06 68 ca d4 00 09 74 61 75 00 00 e6 00 00 00 00 00'
        l = string_BMP.split(' ')
        block_BMP = []
        for each in l:
            block_BMP.append(eval('0x'+each))
        print(block_BMP)
        print('block_start_sequence:',len(block_BMP))
        block_BMP = [0]+block_BMP

        self.h.write(block_pattern)
        self.h.write(block_pattern_1)
        self.h.write(block_BMP)
        '''
        self.h.write(block_start)
        for i in range(7):
            self.h.write(block_64)
        # 4032
        for j in range(7):
            self.h.write(block_middle_start)
            for i in range(7):
                self.h.write(block_64)
        # 4372
        self.h.write(block_end_start)
        for i in range(4):
            self.h.write(block_64)
        self.h.write(block_end)
        '''

        self.bmpload(imagedata, size)

        self.configurelut(num,rep)
        self.start_display()
    
    def configurelut(self,imgnum,repeatnum): # Load the number of images and repeat times into the DMD
        WR= 'w'
        img=convlen(imgnum,11)
        repeat=convlen(repeatnum,32)
        string=repeat+'00000'+img
        commBytes = [0x31, 0x1A]    #[LSB, MSB]
        data = bitstobytes(string)
        Payload = commBytes + data
        print('configurelut:', Payload)
        self.command(WR, Payload)
        self.read_errors()
    
    def definepattern(self,index,exposure,bitdepth,color,triggerin,darktime,triggerout,patind,bitpos):
        WR = 'w'
        payload=[]
        print('index first', index)
        index=convlen(index,16)
        print('index 16', index)
        index=bitstobytes(index)
        print('index bytes', index)
        print('Payload:', payload)
        for i in range(len(index)):
            payload.append(index[i])
            print(i,';Payload:', payload)

        print('exposure 1',exposure)
        exposure=convlen(exposure,24)
        print('exposure 2',exposure)
        exposure=bitstobytes(exposure)
        print('exposure 3',exposure)
        for i in range(len(exposure)):
            payload.append(exposure[i])
            print(i,';Payload:', payload)
        optionsbyte=''
        print('optionsbyte 1:',optionsbyte)
        optionsbyte+='1'
        print('optionsbyte 2:',optionsbyte)
        bitdepth=convlen(bitdepth-1,3)
        print('bitdepth:',bitdepth)
        optionsbyte=bitdepth+optionsbyte
        print('bitdepth+optionsbyte:',optionsbyte)
        optionsbyte=color+optionsbyte
        print('color+optionsbyte:',optionsbyte)
        if triggerin:
            optionsbyte='1'+optionsbyte
        else:
            optionsbyte='0'+optionsbyte

        payload.append(bitstobytes(optionsbyte)[0])
        print('Payload:', payload)
        darktime=convlen(darktime,24)
        darktime=bitstobytes(darktime)
        for i in range(len(darktime)):
            payload.append(darktime[i])
            print(i,';Payload:', payload)
        print('triggerout 1', triggerout)
        triggerout=convlen(triggerout,8)
        print('triggerout 2', triggerout)
        triggerout=bitstobytes(triggerout)
        print('triggerout 3', triggerout)
        print('triggerout[0]', triggerout[0])
        payload.append(triggerout[0])
        print('Payload:', payload)
        print('patind 1:', patind)
        patind=convlen(patind,11)
        print('patind 2:', patind)
        print('bitpos 1:', bitpos)
        bitpos=convlen(bitpos,5)
        print('bitpos 2:', bitpos)
        lastbits=bitpos+patind
        print('bitpos+patind:', lastbits)
        lastbits=bitstobytes(lastbits)
        print('lastbits:', lastbits)
        for i in range(len(lastbits)):
            payload.append(lastbits[i])
            print(i,';Payload:', payload)
        commBytes = [0x34, 0x1A]    #[LSB, MSB]
        data = payload
        print(len(data))
        print('definePattern')
        Payload = commBytes + data
        #print('Payload:', Payload)
        self.command(WR, Payload)
        #self.read_errors()

    def setbmp(self,index,size):
        WR = 'w'
        payload=[]

        index=convlen(index,5)
        index='0'*11+index
        index=bitstobytes(index)
        for i in range(len(index)):
            payload.append(index[i]) 


        total=convlen(size,32)
        total=bitstobytes(total)
        for i in range(len(total)):
            payload.append(total[i])         
        
        commBytes = [0x2A, 0x1A]    #[LSB, MSB]
        data = payload
        #print('setbmp:', data)
        Payload = commBytes + data
        self.command(WR, Payload)
        #self.read_errors()
    
    ## bmp loading function, divided in 56 bytes packages
## max  hid package size=64, flag bytes=4, usb command bytes=2
## size of package description bytes=2. 64-4-2-2=56

    def bmpload(self,image,size):
        WR = 'w'
        print('size-----------------------------------------------------------:',size)
        print('size of image:', len(image))
        packnum=size//504+1
        #print('packnum:',packnum)
        counter=0
        for i in range(packnum):
            if i %100==0:
                print (i,packnum)
            payload=[]
            if i<packnum-1:
                leng=convlen(504,16)
                bits=504
            else:
                leng=convlen(size%504,16)
                bits=size%504
            leng=bitstobytes(leng)
            for j in range(2):
                payload.append(leng[j])
            for j in range(bits):
                payload.append(image[counter])
                counter+=1
            
            commBytes = [0x2B, 0x1A]    #[LSB, MSB]
            data = payload
            #print('bmpload:',i)
            #print('length of images', len(payload))
            Payload = commBytes + data
            #print(Payload)
            #time.sleep(10000)
            self.command(WR, Payload)

            #self.read_errors()
    def change_mode(self, mode):
        print('change_mode')
        WR= 'w'
        lenBytes = [3, 0]   #[LSB, MSB]
        commBytes = [0x1B, 0x1A]    #[LSB, MSB]
        data = [mode]
        Payload = commBytes + data
        self.command(WR, Payload)
        self.read_errors()
    
    def read_errors(self):
        print('check errors')
        WR = 'r'
        lenBytes = [2, 0]
        commBytes = [0x00, 0x01]  #[LSB, HSB]
        data = []
        Payload = commBytes + data
        self.command(WR, Payload)
    
    def stop_display(self):
        print('stop_display')
        WR= 'w'
        lenBytes = [3, 0]   #[LSB, MSB]
        commBytes = [0x24, 0x1A]    #[LSB, MSB]
        data = [0x00]
        Payload = commBytes + data
        self.command(WR, Payload)
        self.read_errors()
    
    def pause_display(self):
        print('pause_display')
        WR= 'w'
        lenBytes = [3, 0]   #[LSB, MSB]
        commBytes = [0x24, 0x1A]    #[LSB, MSB]
        data = [0x01]
        Payload = commBytes + data
        self.command(WR, Payload)
        self.read_errors()
    
    def start_display(self):
        print('start_display')
        WR= 'w'
        lenBytes = [3, 0]   #[LSB, MSB]
        commBytes = [0x24, 0x1A]    #[LSB, MSB]
        data = [0x02]
        Payload = commBytes + data
        self.command(WR, Payload)
        self.read_errors()
    
    def close(self):
        self.h.close()
        print('The DMD has been closed!')

if __name__ == '__main__':
    images = []
    images.append((numpy.asarray(PIL.Image.open("D:\\OneDrive - connect.hku.hk\\25-Python Program\\21-Python Program（HKU LAB）\\Fringe_period100_ori135_phase0.bmp"))))
    #images.append((numpy.asarray(PIL.Image.open("D:\\OneDrive - connect.hku.hk\\25-Python Program\\21-Python Program（HKU LAB）\\Fringe_period76_ori45_phase120.bmp"))))

    dlp = DMD()
    dlp.change_mode(3)

    
    exposure=[1000000]*1
    dark_time=[500000]*1
    trigger_in=[False]*1
    trigger_out=[False]*1

    dlp.defsequence(images,exposure,trigger_in,dark_time,trigger_out,10)
    dlp.close()