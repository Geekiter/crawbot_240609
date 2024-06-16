import json
import time

import neopixel
import utime
from machine import UART, Pin, PWM

from parts.mqttWifi import wifiConnect

# Initialize UART
# UART 2, baud rate: 115200, TX pin number: 23, RX pin number: 4
uart = UART(2, 115200, tx=23, rx=4)
target_id = 86
zoomfactor = 40
# 0, left, 1, right, 2, go, 3, stop
last_direction = 3
buzzer = PWM(Pin(33))
motor1 = PWM(Pin(12))
motor2 = PWM(Pin(13))
motor3 = PWM(Pin(14))
motor4 = PWM(Pin(15))

Tone = [0, 392, 440, 494, 523, 587, 659, 698, 784]

Song = [Tone[3], Tone[3], Tone[3], Tone[3], Tone[3], Tone[3],
        Tone[3], Tone[5], Tone[1], Tone[2], Tone[3],
        Tone[4], Tone[4], Tone[4], Tone[4], Tone[4], Tone[3], Tone[3], Tone[3],
        Tone[5], Tone[5], Tone[4], Tone[2], Tone[1], Tone[8]]

Beat = [1, 1, 2, 1, 1, 2,
        1, 1, 1.5, 0.5, 4,
        1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 2, 2]
pin = Pin(25, Pin.OUT)
speed = 1023
last_z = 0
last_x = 0
last_y = 0
x_max = 200
z_max = 200
y_max = 200
count_limit = 10
count = 0
z_target = 220
z_dis = 0
x_dis = 0
y_dis = 0

labels = ['left', 'stop', 'right']


def motor(A1, A2, B1, B2):
    motor1.duty(A1)
    motor2.duty(A2)
    motor3.duty(B1)
    motor4.duty(B2)


class Car:
    def left(self, speed=800):
        for _ in range(10):
            motor(speed, 0, 0, 0)
            time.sleep(0.1)
            motor(0, 0, 0, 0)

    def right(self, speed=800):
        for _ in range(10):
            motor(0, 0, speed, 0)
            time.sleep(0.1)
            motor(0, 0, 0, 0)

    def stop(self):
        motor(0, 0, 0, 0)

    def forward(self, speed=800):
        for _ in range(10):
            motor(0, speed, 0, speed)
            time.sleep(0.2)
            motor(0, 0, 0, 0)

    def turnRed(self):
        # pass
        np = neopixel.NeoPixel(pin, n=4, bpp=3, timing=1)

        for i in range(0, 4):
            np[i] = (255, 0, 0)
        np.write()

    def music(self):
        pass
        global buzzer
        for i in range(0, len(Song)):
            buzzer.duty_u16(2000)
            buzzer.freq(Song[i])
            for j in range(1, Beat[i] / 0.1):
                time.sleep_ms(25)
            buzzer.duty_u16(0)
            time.sleep(0.01)


def parse_data(data):
    values_list = []
    lines = data.split('\n')

    for line in lines:
        if line.strip():  # Check if the line is not just whitespace
            values = {}
            data_items = line.split(',')
            for item in data_items:
                key, value = item.strip().split(':')
                try:
                    values[key] = float(value) if '.' in value else int(value)
                except ValueError:
                    values[key] = value
            values_list.append(values)

    return values_list


def moveSpeed2(tz, tx, last_direction):
    margin = 20
    z_limit = 220
    speedpct1 = 800  # 700 without load
    speedpct2 = 1022  # 800
    current_direction = last_direction
    print(f'**last_direction:{last_direction}**')
    # last_direction 0, move left, 1, move right, 2, straight, 3 stop

    if tz < z_limit:
        ratio = tz / z_limit
        speedpct1 = int(float(speedpct1) * ratio)
        speedpct2 = int(float(speedpct2) * ratio)

    if tz < z_limit:  # and last_direction !=3:
        motor(0, 0, 0, 0)
        current_direction = 3
        print(f' ==========stop===============')

    elif tx < -margin:  # and last_direction !=0 :
        # move to left
        motor(speedpct1, 0, 0, 0)
        time.sleep(0.1)
        motor(0, 0, 0, 0)
        current_direction = 0
        print(f'move left ------------{speedpct1}')
    elif tx > margin:  # and last_direction !=1 :

        # move to right
        motor(0, 0, speedpct1, 0)
        time.sleep(0.1)
        motor(0, 0, 0, 0)
        print(f'{speedpct1} +++++++++++++++  move right')
        current_direction = 1
        # m.MotorRunInstant('MD', 'backward', speedpct)
    elif tx <= margin and tx >= -margin:  # and last_direction !=2:
        # move straight
        motor(0, speedpct2, 0, speedpct2)
        time.sleep(0.2)
        motor(0, 0, 0, 0)
        print(f' =========={speedpct2}===============')
        current_direction = 2

    return current_direction


def log(message, level="INFO"):
    timestamp = utime.localtime(utime.time())
    formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        *timestamp)
    print("[{}] [{}] {}".format(formatted_time, level, message))


def is_json(msg_byte):
    msg_str = msg_byte.decode('utf-8')
    try:
        json.loads(msg_str)
    except ValueError as e:
        return False
    return True


# task_list = [
#     {
#         "mode": "mqtt",
#         "action": "forward",
#     },{
#         "mode": "k210",
#         "action": "run"
#     },{
#         "mode": "k210",
#         "action": "fun_action"
#     }
#
# ]

task = {
    "mode": "mqtt",
    "action": "forward"
}

device_mode = "k210"
device_action = "fun_action"

fun_action_actions = {
    "86": "turnRed",
    "2": "left",
    "3": "right",
    "4": "forward",
    "5": "music",
    "6": "turnRed"
}


def do_fun_action(tag_id):
    global car
    action = fun_action_actions.get(str(tag_id), "stop")
    if action == "stop":
        car.stop()
    elif action == "left":
        car.left()
    elif action == "right":
        car.right()
    elif action == "forward":
        car.forward()
    elif action == "music":
        car.music()
    elif action == "turnRed":
        car.turnRed()



def MsgOK(topic, msg):
    log("Received message: {} on topic: {}".format(msg, topic), 'INFO')
    # global mqtt_client
    global mode, firstLoop
    global task
    global device_mode
    global device_action
    global car
    global state_value
    print("topic:", topic)
    print("msg:", msg)
    print("myTopic:", myTopic.encode())
    print(topic == myTopic.encode())
    if topic == myTopic.encode():
        # if is_json(msg):  # when receive auto, it will reject all others
        #     task = json.loads(msg.decode('utf-8'))
        #     device_mode = task.get('mode', 'k210')
        #     device_action = task.get('action', 'run')
        if msg == b'fun_action':
            device_mode = "k210"
            device_action = "fun_action"
        elif msg == b'run_action':
            device_mode = "k210"
            device_action = "run_action"

        if msg == b'forward':
            car.forward()
        elif msg == b'left':
            car.left()
        elif msg == b'right':
            car.right()
        elif msg == b'stop':
            car.stop()



# main
# "mqtt_mode"
device_mode = "k210_mode"

wifiName = "WOW10086"
wifiPassword = "chenkeyan"
clientID = "craw"
serverIP = "192.168.31.92"
port = 80
myTopic = "craw"
machineId = "craw"
first_run_mqtt = True

# set up WIFI and MQTT functions
wifiConnection = wifiConnect(wifiName, wifiPassword, clientID, serverIP, port, myTopic, machineId, MsgOK)
wifiConnection.setup()
car = Car()
while True:
    print(device_action)
    # Write data
    #     uart.write('Hello from ESP32!\n')
    # start to connect to Wifi
    if wifiConnection.wifi_connect == False:
        wifiConnection.do_connect()
        wifiConnection.monitor_wifi_connection()

    if wifiConnection.run:  # when run=True, mqtt connection established
        first_run_web = True
        if wifiConnection.mqtt_client:  # turn off light after mqtt connection established
            first_run_mqtt = False
            try:
                wifiConnection.mqtt_client.check_msg()
            except OSError as e:  # if error, restart
                wifiConnection.run = False
                print('Failed to connect to MQTT broker. waiting...')
    else:
        first_run_mqtt = True
        # green light is on waiting for mqtt connection
        if wifiConnection.wifi_connect:
            first_run_web = False

    wifiConnection.loop()

    # Check if data is available
    count += 1
    if uart.any():
        data = uart.read().decode('utf-8').strip()  # 读取一个字节
        print(data)
        # Parse data
        index = 0
        index2 = 0
        obj_id = None
        received_id1 = None
        received_id = None
        try:
            parsed_values_list = parse_data(data)
            print("parsed_values_list:", parsed_values_list)
            length1 = len(parsed_values_list)
            if length1 > 0:
                for i in range(length1):

                    # assume the first value is the targeted id
                    obj_id = parsed_values_list[index].get('objId', None)
                    if obj_id is None:
                        received_id1 = int(parsed_values_list[i].get('id', 9999))
                    else:
                        obj_id = int(obj_id)

                    if received_id1 == target_id:
                        index = i
                        received_id = received_id1
                        print(f"received id:{received_id}")
                        z_dis = int(-zoomfactor * float(parsed_values_list[index].get('Tz', 'N/A')))
                        y_dis = int(-zoomfactor * float(parsed_values_list[index].get('Tx', 'N/A')))
                        x_dis = int(zoomfactor * float(parsed_values_list[index].get('Ty', 'N/A')))
                        print(f"x={x_dis},y={y_dis},z={z_dis}")
                        print(f"------------count={count}")
                        count = 0


        except Exception as e:
            print("Error parsing data:", e)

        x_diff = abs(x_dis - last_x)
        z_diff = abs(z_dis - last_z)
        y_diff = abs(y_dis - last_y)
        if device_action == "fun_action" and received_id is not None:
            print("in fun mode")
            do_fun_action(received_id)
        elif device_action == "run_action" and ((z_dis != last_z or x_dis != last_x or y_dis != last_y)
                                            and z_diff < z_max and x_diff < x_max and y_diff < y_max):
            print("in run mode")
            print(f"in loop, x={x_dis},y={y_dis},z={z_dis}")
            if z_dis > z_target:
                current_direction = moveSpeed2(z_dis, x_dis, last_direction)
                last_direction = current_direction
                # moveForwardSpd(30)
                time.sleep(0.1)

            else:  # reach to the area of target
                got_there = True
                count2 = 0  # restart for finding the grabbed target
        elif device_action == "run_action" and obj_id is not None:
            obj_id = labels[obj_id]
            if obj_id is "stop":
                motor(0, 0, 0, 0)
                print('car stopped')
                time.sleep(0.1)
            elif obj_id is "left":
                for _ in range(10):
                    motor(800, 0, 0, 0)
                    time.sleep(0.1)
                    motor(0, 0, 0, 0)
            elif obj_id is "right":
                for _ in range(10):
                    motor(0, 0, 800, 0)
                    time.sleep(0.1)
                    motor(0, 0, 0, 0)

        last_x = x_dis
        last_z = z_dis
        last_y = y_dis

    # print(f"count={count}")
    if count > count_limit:
        motor(0, 0, 0, 0)
        # print('car stopped')
        time.sleep(0.1)
