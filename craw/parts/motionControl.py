from machine import Pin , PWM, ADC, UART
from utime import sleep
from motorPCA9685 import MotorDriver
import random

class motorControl():

    def __init__(self, debug=False, uart_tx=16, uart_rx=17):
        self.debug = debug

        self.grabState = 0  # 0 unknown, 1 close, 2 open
        self.grabLastState = 0
        self.maxGrabLevel = 70
        self.minGrabLevel = 30
        self.currentGrabLevel = 70


        # define for arm and claw control
        self.ina1 = Pin(8,Pin.OUT)
        self.ina2 = Pin(7, Pin.OUT)
        self.pwma = PWM(Pin(6))
        self.pwma.freq(1000)

        self.uart2 = UART(0, baudrate=115200, tx=Pin(uart_tx), rx=Pin(uart_rx))

        self.inb1 = Pin(9,Pin.OUT)
        self.inb2 = Pin(10, Pin.OUT)
        self.pwmb = PWM(Pin(11))
        self.pwmb.freq(1000)
        self.m=1

    # set up arm and claw motion control
    def RotateACW(self,duty):
        self.ina1.value(1)
        self.ina2.value(0)
        duty_16 = int((duty*65536)/100)
        self.pwma.duty_u16(duty_16)

    def RotateACCW(self,duty):
        self.ina1.value(0)
        self.ina2.value(1)
        duty_16 = int((duty*65536)/100)
        self.pwma.duty_u16(duty_16)

    def RotateBCW(self, duty):
        self.inb1.value(1)
        self.inb2.value(0)
        duty_16 = int((duty*65536)/100)
        self.pwmb.duty_u16(duty_16)

    def RotateBCCW(self, duty):
        self.inb1.value(0)
        self.inb2.value(1)
        duty_16 = int((duty*65536)/100)
        self.pwmb.duty_u16(duty_16)
        
    def StopMotor(self):
        self.ina1.value(0)
        self.ina2.value(0)
        self.pwma.duty_u16(0)
        self.inb1.value(0)
        self.inb2.value(0)
        self.pwmb.duty_u16(0)

    def openClaw(self):
    #  open claw

        if self.grabLastState!=2:
            self.currentGrabLevel=self.maxGrabLevel
            
        else:
            self.currentGrabLevel=max(self.currentGrabLevel-10,self.minGrabLevel)
        
        if (self.debug):
            print(f"open Claw at {self.currentGrabLevel}")
        
        self.RotateBCW(self.currentGrabLevel)
        sleep(0.5)
        self.StopMotor()
        sleep(0.2)
        self.grabLastState=2

    def closeClaw(self):
    # close claw
        
        if self.grabLastState!=1:
            self.currentGrabLevel=self.maxGrabLevel
            
        else:
            self.currentGrabLevel=max(self.currentGrabLevel-10,self.minGrabLevel)
        
        if (self.debug):
            print(f"close Claw at {self.currentGrabLevel}")
        self.RotateBCCW(self.currentGrabLevel)
        sleep(0.5)
        self.StopMotor()
        sleep(0.2)
        self.grabLastState=1

    def armUp(self, duty_cycle):
    # arm up
        self.RotateACW(duty_cycle)
        sleep(0.1)
        self.StopMotor()
        sleep(0.1)

    def armDown(self, duty_cycle):
    # arm down
        self.RotateACCW(duty_cycle)
        sleep(0.05)
        self.StopMotor()
        sleep(0.2)

    # Wheel motion control functions
    def setup(self):
        self.m = MotorDriver()

    def moveForwardSpd(self,speedpct1):
        self.m.MotorRunInstant('MA', 'forward', speedpct1)
        self.m.MotorRunInstant('MB', 'forward', speedpct1)
        self.m.MotorRunInstant('MC', 'forward', speedpct1)
        self.m.MotorRunInstant('MD', 'forward', speedpct1)
        
    def moveBackwardSpd(self,speedpct1):
        self.m.MotorRunInstant('MA', 'backward', speedpct1)
        self.m.MotorRunInstant('MB', 'backward', speedpct1)
        self.m.MotorRunInstant('MC', 'backward', speedpct1)
        self.m.MotorRunInstant('MD', 'backward', speedpct1)
        
    def rotateRightSpd(self,speedpct1):
        self.m.MotorRunInstant('MA', 'forward', speedpct1)
        self.m.MotorRunInstant('MB', 'backward', speedpct1)
        self.m.MotorRunInstant('MC', 'forward', speedpct1)
        self.m.MotorRunInstant('MD', 'backward', speedpct1)
        
    def rotateLeftSpd(self, speedpct1):
        self.m.MotorRunInstant('MA', 'backward', speedpct1)
        self.m.MotorRunInstant('MB', 'forward', speedpct1)
        self.m.MotorRunInstant('MC', 'backward', speedpct1)
        self.m.MotorRunInstant('MD', 'forward', speedpct1)

    def parallelLeftSpd(self, speedpct1):
        self.m.MotorRunInstant('MA', 'forward', speedpct1)
        self.m.MotorRunInstant('MB', 'backward', speedpct1)
        self.m.MotorRunInstant('MC', 'backward', speedpct1)
        self.m.MotorRunInstant('MD', 'forward', speedpct1)

    def parallelRightSpd(self, speedpct1):
        self.m.MotorRunInstant('MA', 'backward', speedpct1)
        self.m.MotorRunInstant('MB', 'forward', speedpct1)
        self.m.MotorRunInstant('MC', 'forward', speedpct1)
        self.m.MotorRunInstant('MD', 'backward', speedpct1)

    def stopMove(self):
        
        self.m.MotorStop('MA')
        self.m.MotorStop('MB')
        self.m.MotorStop('MC')
        self.m.MotorStop('MD')
            

    def keepForward(self, sp):
        self.moveForwardSpd(sp)
        self.moveForwardSpd(sp - 5)
        self.moveForwardSpd(sp - 10)
        self.stopMove()


    def keepTurnLeft(self,sp):
        self.rotateLeftSpd(sp)
        self.rotateLeftSpd(sp - 5)
        self.rotateLeftSpd(sp - 8)
        self.rotateLeftSpd(sp - 10)
        self.stopMove()


    def keepTurnRight(self, sp):
        self.rotateRightSpd(sp)
        self.rotateRightSpd(sp - 5)
        self.rotateRightSpd(sp - 8)
        self.rotateRightSpd(sp - 10)
        self.stopMove()


    def keepBackward(self, sp):
        self.moveBackwardSpd(sp)
        self.moveBackwardSpd(sp - 5)
        self.moveBackwardSpd(sp - 10)
        self.stopMove()

    def keepTurnLeft(self, sp):
        self.rotateLeftSpd(sp)
        self.rotateLeftSpd(sp - 5)
        self.rotateLeftSpd(sp - 8)
        self.rotateLeftSpd(sp - 10)
        self.stopMove()


    def keepParallelTurnRight(self, sp):
        self.parallelRightSpd(sp)
        self.parallelRightSpd(sp - 5)
        self.parallelRightSpd(sp - 8)
        self.parallelRightSpd(sp - 10)
        self.stopMove()

    def keepParallelTurnLeft(self,sp):
        self.parallelLeftSpd(sp)
        self.parallelLeftSpd(sp - 5)
        self.parallelLeftSpd(sp - 8)
        self.parallelLeftSpd(sp - 10)
        self.stopMove()
