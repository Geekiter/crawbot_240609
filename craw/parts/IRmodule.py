from machine import Pin , PWM, ADC
import utime


class IR():

    def __init__(self,callback, debug=False):
        self.debug = debug
        # infrared remote
        self.IR_PIN = Pin(3, Pin.IN, Pin.PULL_UP)
        # exec_cmd
        self.N = 0
        self.callback=callback
        self.received=False

    def exec(self, data):
        self.callback(data)

    def IR_receive(self):
        if self.IR_PIN.value() == 0:
            print(self.IR_PIN.value())
            count = 0
            while self.IR_PIN.value() == 0 and count < 200:
                count += 1
                utime.sleep_us(60)
            count = 0
            while self.IR_PIN.value() == 1 and count < 80:
                count += 1
                utime.sleep_us(60)
            idx = 0
            cnt = 0
            data = [0,0,0,0]
            for i in range(0,32):
                count = 0
                while self.IR_PIN.value() == 0 and count < 15:
                    count += 1
                    utime.sleep_us(60)
                count = 0
                while self.IR_PIN.value() == 1 and count < 40:
                    count += 1
                    utime.sleep_us(60)
                if count > 8:
                    data[idx] |= 1<<cnt
                if cnt == 7:
                    cnt = 0
                    idx += 1
                else:
                    cnt += 1
            if data[0]+data[1] == 0xFF and data[2]+data[3] == 0xFF:
                print("Retrieve key: 0x%02x" %data[2])
                self.N=data[2]
                self.received=True
