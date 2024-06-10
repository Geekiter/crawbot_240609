# Untitled - By: integem - Tue Nov 21 2023
# AprilTags3D定位例程

import math
import time
from gc import mem_free

import KPU as kpu
import lcd
import sensor
from Maix import utils
from fpioa_manager import fm
from machine import UART

lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)  # 如果分辨率大得多，内存就不够用了……
sensor.skip_frames(time=2000)
#sensor.set_auto_gain(False)  # 必须关闭此功能，以防止图像冲洗…
#sensor.set_auto_whitebal(False)  # 必须关闭此功能，以防止图像冲洗…
sensor.set_vflip(1)
clock = time.clock()

# 映射串口引脚
fm.register(6, fm.fpioa.UART1_RX, force=True)
fm.register(7, fm.fpioa.UART1_TX, force=True)

# 初始化串口
uart = UART(UART.UART1, 115200, read_buf_len=4096)
uart.write('Hello pico!')

f_x = (2.8 / 3.984) * 160
f_y = (2.8 / 2.952) * 120
c_x = 160 * 0.5
c_y = 120 * 0.5

model_addr = 0x300000

# model_addr = "/sd/model-130053.kmodel"
task = kpu.load(model_addr)
labels = ['left', 'stop', 'right']
anchors = [1.84, 2.19, 2.06, 1.78, 1.5, 1.53, 2.47, 2.44, 3.03, 3.19]

kpu.init_yolo2(task, 0.5, 0.3, 5, anchors)


def degrees(radians):
    return (180 * radians) / math.pi


while (True):
    clock.tick()
    print("stack mem", mem_free() / 1024)  # stack mem
    print("heap mem", utils.heap_free() / 1024)  # heap mem
    output1 = ""
    img = sensor.snapshot()
    for tag in img.find_apriltags(fx=f_x, fy=f_y, cx=c_x, cy=c_y):  # defaults to TAG36H11
        img.draw_rectangle(tag.rect(), color=(255, 0, 0))
        img.draw_cross(tag.cx(), tag.cy(), color=(0, 255, 0))
        print_args = (tag.id(), tag.x_translation(), tag.y_translation(), tag.z_translation(), \
                      degrees(tag.x_rotation()), degrees(tag.y_rotation()), degrees(tag.z_rotation()))
        # 变换单位不详。旋转单位是度数。
        # print("id: %d, Tx: %f, Ty %f, Tz %f, Rx %f, Ry %f, Rz %f" % print_args)
        output1 = "id:" + str(tag.id()) + ",Tx: " + str(tag.x_translation()) + ",Ty: " + str(
            tag.y_translation()) + ",Tz: " + str(tag.z_translation()) + "\n"
        uart.write(output1)  # 数据回传

    img_size = 224
    img2 = img.resize(img_size, img_size)
    img2.pix_to_ai()
    objects = kpu.run_yolo2(task, img2)
    del img2
    if objects:
        for obj in objects:
            classid = labels[obj.classid()]
            pos = obj.rect()
            pos = (
                int(pos[0] * img.width() / img_size),
                int(pos[1] * img.height() / img_size),
                int(pos[2] * img.width() / img_size),
                int(pos[3] * img.height() / img_size),
            )
            img.draw_rectangle(pos, color=(0, 255, 255))
            img.draw_string(pos[0], pos[1], classid, color=(255, 0, 0), scale=2)
            output1 = "objId: " + str(obj.classid()) + "\n"
            uart.write(output1)  # 数据回传

    lcd.display(img)
    # print(clock.fps())
