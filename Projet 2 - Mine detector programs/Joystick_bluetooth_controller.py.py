import pygame as pg
import serial
import threading
import time

pg.init()
running = True
j = pg.joystick.Joystick(0)
j.init()
speed_ratio = 0.5

received_data = ""
thread_list = []
ser = serial.Serial("COM11", 9600)


# Joystick buttons
"""
LEFT horizontal axis: 0
LEFT vertical axis: 1
LEFT trigger: 2
RIGHT horizontal axis: 3
RIGHT vertical axis: 4
RIGHT trigger: 5
"""

joystick = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

def receive_data():
    global received_data
    while True:
        data = ser.readline().decode("utf-8").rstrip()
        if data != "":
            received_data = data

def event():
    global thread_list, received_data
    if received_data == "metal detected":
        print('Event "metal detected"')
        time.sleep(1)
    else:
        print('Event "other"')
        time.sleep(1)

    received_data = ""
    thread_list.pop()

def get_joystick(event):
    global joystick
    if event.axis == 0 and abs(event.value) > 0.1:
        joystick[event.axis] = event.value
    elif event.axis == 0 and abs(event.value) < 0.1:
        joystick[event.axis] = 0

    if event.axis in [4, 5] and event.value > -0.9:
        joystick[event.axis] = event.value + 1
    elif event.axis in [4, 5] and event.value < -0.9:
        joystick[event.axis] = 0


def map_speed_to_pwm(speed):
    """Map the speed between -2 and 2 to a PWM signal between 0 and 100"""
    if abs(speed) > 0.1:
        return round(speed * 100 / 2, 2)
    else:
        return 0.0


forward_speed = 0
turn_speed = 0

right_speed = 0
left_speed = 0


### MAIN LOOP ###
def main():
    global running, forward_speed, turn_speed, right_speed, left_speed
    for event in pg.event.get():
        if event.type == pg.JOYAXISMOTION:
            get_joystick(event)
        elif event.type == pg.QUIT:
            running = False
            pg.quit()

    forward_speed = joystick[5] - joystick[4]
    turn_speed = joystick[0]

    # Motors speed between -2 and 2
    right_speed = forward_speed + turn_speed
    left_speed = forward_speed - turn_speed

    if right_speed > 2:
        right_speed = 2
    elif right_speed < -2:
        right_speed = -2
    if left_speed > 2:
        left_speed = 2
    elif left_speed < -2:
        left_speed = -2

    right_speed *= speed_ratio
    left_speed *= speed_ratio


if __name__ == "__main__":
    try:
        receive_thread = threading.Thread(target=receive_data, daemon=True)
        receive_thread.start()
        while running:
            main()
            data = str(map_speed_to_pwm(right_speed)) + " " + str(map_speed_to_pwm(left_speed)) + "\n"
            ser.write(data.encode("utf-8"))
            if received_data != "" and thread_list == []:
                thread_list.append(threading.Thread(target=event, daemon=True))
                thread_list[-1].start()
    except:
        ser.close()
        pg.quit()
        print("Program stopped")
