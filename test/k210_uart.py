import lcd
import sensor
import time
from fpioa_manager import fm
from machine import UART

lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)  # 如果分辨率大得多，内存就不够用了……
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)  # 必须关闭此功能，以防止图像冲洗…
sensor.set_auto_whitebal(False)  # 必须关闭此功能，以防止图像冲洗…
sensor.set_vflip(1)
clock = time.clock()

# 映射串口引脚
fm.register(6, fm.fpioa.UART1_RX, force=True)
fm.register(7, fm.fpioa.UART1_TX, force=True)

# 初始化串口
uart = UART(UART.UART1, 115200, read_buf_len=4096)
count = 0

while True:
    img = sensor.snapshot()
    lcd.display(img)
    read_data = uart.read(256)
    if read_data:
        print("k210 read_data:", read_data))

    uart.write('k210 count: %d\n' % count)
    count += 1
