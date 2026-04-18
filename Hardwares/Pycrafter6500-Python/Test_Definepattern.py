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
def definepattern(index,exposure,bitdepth,color,triggerin,darktime,triggerout,patind,bitpos):

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
        #self.read_errors()
def configurelut(imgnum,repeatnum): # Load the number of images and repeat times into the DMD
        WR= 'w'
        img=convlen(imgnum,11)
        repeat=convlen(repeatnum,32)
        string=repeat+'00000'+img
        commBytes = [0x31, 0x1A]    #[LSB, MSB]
        data = bitstobytes(string)
        Payload = commBytes + data
        print('configurelut:', Payload)


configurelut(2,3)
definepattern(0,105,1,'001',False,0,False,0, 0)