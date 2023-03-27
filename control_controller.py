import pygame as pg
import time
import RPi.GPIO as GPIO

pg.init()
joysticks = [pg.joystick.Joystick(i) for i in range(pg.joystick.get_count())]
joy = joysticks[0]
joy.init()
running = True
joystick_axis = {"0":0,"4":0,"5":0}
forward_speed = 0

####GPIO PINS####
# Motor 1
MR_ENABLE = 38
MR_IN1 = 33
MR_IN2 = 31

# Motor 2
ML_ENABLE = 40
ML_IN3 = 37
ML_IN4 = 35

# Setup
try:
    # GPIO setup
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(MR_ENABLE, GPIO.OUT)
    GPIO.setup(MR_IN1, GPIO.OUT)
    GPIO.setup(MR_IN2, GPIO.OUT)
    GPIO.setup(ML_ENABLE, GPIO.OUT)
    GPIO.setup(ML_IN3, GPIO.OUT)
    GPIO.setup(ML_IN4, GPIO.OUT)


    # PWM setup
    MA_PWM = GPIO.PWM(MR_ENABLE, 1000)
    MB_PWM = GPIO.PWM(ML_ENABLE, 1000)
    MA_PWM.start(0)
    MB_PWM.start(0)
except:
    print("Veuillez vérifier les connexions")

def get_axis_values(event):
    global joystick_axis
    if event.axis == 0 and abs(event.value) > 0.1:
        joystick_axis[str(event.axis)] = event.value
    else:
        joystick_axis[str(event.axis)] = 0
    if event.axis in [4,5]:
        joystick_axis[str(event.axis)] = event.value - 1

def map_speed_to_pwm(speed):
    """
    speed is between -4 and 4
    """
    if abs(speed) > 0:
        return round(speed* 100/4,2)
    else:
        return 0.0

def control_motors(right_motors, left_motors):
    """Send a PWM signal to the motors

    Args:
        right_motors (_type_): speed of right motors 
        left_motors (_type_): speed of left motors
    """
    # Right motors
    if right_motors > 0:
        GPIO.output(MR_IN1, GPIO.HIGH)
        GPIO.output(MR_IN2, GPIO.LOW)
    else:
        GPIO.output(MR_IN1, GPIO.LOW)
        GPIO.output(MR_IN2, GPIO.HIGH)
    MA_PWM.ChangeDutyCycle(map_speed_to_pwm(abs(right_motors)))

    # Left motors
    if left_motors > 0:
        GPIO.output(ML_IN3, GPIO.HIGH)
        GPIO.output(ML_IN4, GPIO.LOW)
    else:
        GPIO.output(ML_IN3, GPIO.LOW)
        GPIO.output(ML_IN4, GPIO.HIGH)
    MB_PWM.ChangeDutyCycle(map_speed_to_pwm(abs(left_motors)))

while running:
    try:
        for event in pg.event.get():
            
            if event.type == pg.QUIT:
                running = False

            if event.type == pg.JOYAXISMOTION:
                get_axis_values(event)
            
            time.sleep(0.001)

            forward_speed = joystick_axis["5"]-joystick_axis["4"]
            turning_speed = joystick_axis["0"] * 2
            
            right_motors = forward_speed - turning_speed
            left_motors = forward_speed + turning_speed
            
            print("Left motors: ", map_speed_to_pwm(left_motors), "\tRight motors: ", map_speed_to_pwm(right_motors))
            
            control_motors(right_motors, left_motors)
    except KeyboardInterrupt:
        GPIO.cleanup()
    except IndexError:
        print("Veuillez connecter une manette")

        
        
