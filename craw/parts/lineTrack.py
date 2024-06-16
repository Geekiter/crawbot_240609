from machine import Pin , PWM
#from parts.motionControl import motorControl
from utime import sleep


class lineTracking():
    def __init__(self, motor, debug=False):
        self.debug = debug
        self.TrackingPin_R = 1     # IR tracking sensor(right)
        self.TrackingPin_L = 2     # IR tracking sensor(left)
        self.Track_L=0
        self.Track_R=0
        #define speed
        self.speedFwd = 30 #35
        self.speedTurn = 20 #20
        self.motor=motor

    def track_line_setup(self):
        self.Track_L = Pin(self.TrackingPin_L,Pin.IN,Pin.PULL_UP)
        self.Track_R = Pin(self.TrackingPin_R,Pin.IN,Pin.PULL_UP)



    def track_line(self):
        Track = self.Track_L.value() * 2 + self.Track_R.value()
        
        if self.debug:
            print(f'Track={Track}')


        if Track == 0:                # No black lines detected on the left and right
            self.motor.stopMove()
        elif Track == 1:                # Only the black line is detected on the right side
            # move to right
            self.motor.rotateRightSpd(self.speedTurn)
        elif Track == 2:                # Only the black line is detected on the left side
            # move to left
            self.motor.rotateLeftSpd(self.speedTurn)   
        elif Track == 3:                # Black lines are detected on both the left and right
            #move straight
            self.motor.moveForwardSpd(self.speedFwd)

