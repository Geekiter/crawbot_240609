import time

from machine import UART, Pin, PWM

# Initialize UART
# UART 2, baud rate: 115200, TX pin number: 23, RX pin number: 4
uart = UART(2, 115200, tx=23, rx=4)
target_id = 86
zoomfactor = 40
# 0, left, 1, right, 2, go, 3, stop
last_direction = 3

motor1 = PWM(Pin(12))
motor2 = PWM(Pin(13))
motor3 = PWM(Pin(14))
motor4 = PWM(Pin(15))
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


while True:
    # Write data
    #     uart.write('Hello from ESP32!\n')

    # Check if data is available
    count += 1
    if uart.any():
        data = uart.read().decode('utf-8').strip()  # 读取一个字节
        print(data)
        # Parse data
        indx = 0
        indx2 = 0
        obj_id = None
        received_id1 = None
        try:
            parsed_values_list = parse_data(data)
            length1 = len(parsed_values_list)
            if length1 > 0:
                for i in range(length1):

                    # assume the first value is the targeted id
                    obj_id = int(parsed_values_list[indx].get('objId', None))
                    if obj_id is None:

                        received_id1 = int(parsed_values_list[i].get('id', 'N/A'))


                    if received_id1 == target_id:
                        indx = i
                        received_id = received_id1
                        print(f"received id:{received_id}")
                        z_dis = int(-zoomfactor * float(parsed_values_list[indx].get('Tz', 'N/A')))
                        y_dis = int(-zoomfactor * float(parsed_values_list[indx].get('Tx', 'N/A')))
                        x_dis = int(zoomfactor * float(parsed_values_list[indx].get('Ty', 'N/A')))
                        print(f"x={x_dis},y={y_dis},z={z_dis}")
                        print(f"------------count={count}")
                        count = 0


        except Exception as e:
            print("Error parsing data:", e)
        x_diff = abs(x_dis - last_x)
        z_diff = abs(z_dis - last_z)
        y_diff = abs(y_dis - last_y)

        if ((z_dis != last_z or x_dis != last_x or y_dis != last_y)
                and z_diff < z_max and x_diff < x_max and y_diff < y_max):
            print(f"in loop, x={x_dis},y={y_dis},z={z_dis}")
            if z_dis > z_target:
                current_direction = moveSpeed2(z_dis, x_dis, last_direction)
                last_direction = current_direction
                # moveForwardSpd(30)
                time.sleep(0.1)

            else:  # reach to the area of target
                got_there = True
                count2 = 0  # restart for finding the grabbed target
        elif obj_id is not None:
            obj_id = labels[obj_id]
            if obj_id is "stop" or obj_id is "park":
                motor(0, 0, 0, 0)
                print('car stopped')
                time.sleep(0.1)
            elif obj_id is "left":
                for _ in range(10):
                    motor(0, 0, 800, 0)
                    time.sleep(0.1)
                    motor(0, 0, 0, 0)
            elif obj_id is "right":
                for _ in range(10):
                    motor(800, 0, 0, 0)
                    time.sleep(0.1)
                    motor(0, 0, 0, 0)
            elif obj_id is "turning":
                for _ in range(5 * 10):
                    motor(800, 0, 0, 0)
                    time.sleep(0.1)
                    motor(0, 0, 0, 0)

        last_x = x_dis
        last_z = z_dis
        last_y = y_dis

    print(f"count={count}")
    if count > count_limit:
        motor(0, 0, 0, 0)
        print('car stopped')
        time.sleep(0.1)
