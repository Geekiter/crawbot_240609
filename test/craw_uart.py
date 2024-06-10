import time

from machine import UART, Pin, PWM

# 初始化串口
uart = UART(2, 115200, tx=23, rx=4)

count = 0

while True:

    read_data = uart.read(256)
    if read_data:
        print("craw read_data:", read_data)

    uart.write('craw count: %d\n' % count)
    count += 1
