import numpy
from Evolve_512_Delta_Camera import CCD

class Calculator():
    def __init__(self):
        pass
    
    def add(self, a, b):
        c = a+b
        return c
    
    def subtract(self, a, b):
        c = a-b
        return c

if __name__ == '__main__':
    cal = Calculator()
    print(cal.add(5,6))
    print(cal.subtract(5,6))
    print(cal)
    print(dir(cal))
    print(Calculator)
    print(dir(Calculator))
    print(dir(CCD))