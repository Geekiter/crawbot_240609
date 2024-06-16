from machine import Pin , PWM, ADC
import utime


class UltrasonicSensor():

    def __init__(self,motor, debug=False):
        self.debug = debug
        # Ultrasonic sensor setup
        self.trig = Pin(4, Pin.OUT)
        self.echo = Pin(5, Pin.IN)
        self.motor=motor

    def getDistance(self):
        self.trig.low()                    # Generate 10us square wave
        utime.sleep_us(2)
        self.trig.high()
        utime.sleep_us(10)
        self.trig.low()
        
        while self.echo.value() == 0:
            start = utime.ticks_us()
        while self.echo.value() == 1:
            end = utime.ticks_us()
        d = (end - start) * 0.0343 / 2 
        return d  

    def Dodge(self):
        turnDistance=30
        stop_time=0.1
        stop_time2=0.1
        speedpct1 = 35
        distance = self.getDistance()   # Get ultrasonic calculation distance
        if self.debug: 
            print("distance：{:.2f} cm".format(distance))
        utime.sleep(0.1)
        if distance < turnDistance:
            self.motor.rotateLeftSpd(speedpct1)          # Turn left 
            utime.sleep(stop_time)
            self.motor.stopMove()
            utime.sleep(stop_time2) 
            if self.debug: 
                print(f'move left at {speedpct1} +++++++++++++++  ')      
        else:
            self.motor.moveForwardSpd(speedpct1)  # Go forward   
            utime.sleep(stop_time)
            self.motor.stopMove()
            utime.sleep(stop_time2)  
            if self.debug:   
                print(f' ========== move forward at {speedpct1}===============')