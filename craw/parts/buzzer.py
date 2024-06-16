from machine import Pin , PWM
import time

class buzzer():
    def __init__(self, debug=False):
        self.debug = debug

        self.buzzer = PWM(Pin(0))
        Tone = [0, 392, 440, 494, 523, 587, 659, 698, 784]

        self.Song = [Tone[3], Tone[3], Tone[3], Tone[3], Tone[3], Tone[3],
                Tone[3], Tone[5], Tone[1], Tone[2], Tone[3],
                Tone[4], Tone[4], Tone[4], Tone[4], Tone[4], Tone[3], Tone[3], Tone[3],
                Tone[5], Tone[5], Tone[4], Tone[2], Tone[1], Tone[8]]

        self.Beat = [1, 1, 2, 1, 1, 2,
                1, 1, 1.5, 0.5, 4,
                1, 1, 1, 1, 1, 1, 1, 1,
                1, 1, 1, 1, 2, 2]

        self.Song2 = [Tone[3], Tone[3]]
        self.Beat2 = [1, 1]

    def Music(self):
        for i in range(0, len(self.Song)):
            self.buzzer.duty_u16(2000)
            self.buzzer.freq(self.Song[i])
            for j in range(1, self.Beat[i] / 0.1):
                time.sleep_ms(25)
            self.buzzer.duty_u16(0)
            time.sleep(0.01)

    def Greeting(self):
        for i in range(0, len(self.Song2)):
            self.buzzer.duty_u16(2000)
            self.buzzer.freq(self.Song2[i])
            for j in range(1, self.Beat2[i] / 0.1):
                time.sleep_ms(25)
            self.buzzer.duty_u16(0)
            time.sleep(0.01)