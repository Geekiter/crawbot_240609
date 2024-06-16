
from machine import Pin , PWM
import random

class LED():
    def __init__(self, debug=False):
        self.debug = debug
        # setup LED
        self.Led_R = PWM(Pin(18))
        self.Led_G = PWM(Pin(14))
        self.Led_B = PWM(Pin(19))
        self.Led_E = Pin(22, Pin.OUT) #PWM(Pin(22))
        self.Led_R.freq(1000)
        self.Led_G.freq(1000)
        self.Led_B.freq(1000)

    #LED RGB function
    def RGB(self, R, G, B, E):
        if E==1:
            if R < 0:
                R = random.randint(0, 65535)
            elif R >= 65535:
                R = 65534
            if G < 0:
                G = random.randint(0, 65535)
            elif G >= 65535:
                G = 65534
            if B < 0:
                B = random.randint(0, 65535)
            elif B >= 65535:
                B = 65534
            # print(R,G,B)
            self.Led_R.duty_u16(65534-R)
            self.Led_G.duty_u16(65534-G)
            self.Led_B.duty_u16(65534-B)
            self.Led_E.value(1)
        else:
            self.Led_R.duty_u16(0)
            self.Led_G.duty_u16(0)
            self.Led_B.duty_u16(0)
            self.Led_E.value(0)
