import numpy as np
import cv2
import mediapipe as mp
import serial
from threading import Thread
import time
import events

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

horizontal_vector = np.array([1, 0])
received_data = ""
thread_list = []
ser = serial.Serial("COM11", 9600)


### MATH FUNCTIONS ###
def angle(v1, v2):
    v1_u = v1 / np.linalg.norm(v1)
    v2_u = v2 / np.linalg.norm(v2)
    sc_product = np.dot(v1_u, v2_u)

    if sc_product < 0:
        if v2[1] > 0:
            return -1
        else:
            return sc_product
    else:
        if v2[1] > 0:
            return 1
        else:
            return sc_product


def speed_to_rotation(speed, rotation):
    if abs(speed) < 0.2:
        speed = 0
    if abs(rotation) < 0.2:
        rotation = 0

    rotation *= 0.8
    L = (speed + rotation) * 100
    R = (speed - rotation) * 100
    return np.clip([L, R], -100, 100)


######################


### CONTROL FUNCTIONS ###
def receive_data():
    global received_data
    while True:
        data = ser.readline().decode("utf-8").rstrip()
        if data != "":
            received_data = data


def event():
    global thread_list, received_data
    if received_data == "metal detected":
        events.sound_event()
    else:
        print('Event "other"')
        time.sleep(1)

    received_data = ""
    thread_list.pop()


def main():
    global horizontal_vector, ser, received_data, thread_list
    # For webcam input:
    cap = cv2.VideoCapture(0)
    with mp_hands.Hands(
        model_complexity=1, min_detection_confidence=0.8, min_tracking_confidence=0.5
    ) as hands:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.flip(image, 1)
            results = hands.process(image)

            # Draw the hand annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.multi_hand_landmarks:
                vector_left, vector_right = np.array([0, 0]), np.array([0, 0])
                angles = [0, 0]
                for hand_landmarks in results.multi_hand_landmarks:
                    handIndex = results.multi_hand_landmarks.index(hand_landmarks)
                    handLabel = (
                        results.multi_handedness[handIndex].classification[0].label
                    )
                    if handLabel == "Left":
                        vector_left = np.array(
                            [
                                hand_landmarks.landmark[5].x
                                - hand_landmarks.landmark[17].x,
                                hand_landmarks.landmark[5].y
                                - hand_landmarks.landmark[17].y,
                            ]
                        )
                        angles[1] = angle(horizontal_vector, vector_left)
                    elif handLabel == "Right":
                        vector_right = np.array(
                            [
                                hand_landmarks.landmark[5].x
                                - hand_landmarks.landmark[17].x,
                                hand_landmarks.landmark[5].y
                                - hand_landmarks.landmark[17].y,
                            ]
                        )
                        angles[0] = angle(horizontal_vector, vector_right)

                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style(),
                    )

                speeds = speed_to_rotation(angles[0], angles[1])
                data = str(round(speeds[0], 2)) + " " + str(round(speeds[1], 2)) + "\n"
                ser.write(data.encode("utf-8"))
            else:
                ser.write("0 0\n".encode("utf-8"))

            ######################
            ### EVENT ###

            if received_data != "" and thread_list == []:
                thread_list.append(Thread(target=event, daemon=True))
                thread_list[0].start()

            ######################
            ######################
            # Flip the image horizontally for a selfie-view display.
            cv2.imshow("MediaPipe Hands", image)
            if cv2.waitKey(5) & 0xFF == 27:
                ser.close()
                print("Program Stopped")
                break
        cap.release()


######################
receive_thread = Thread(target=receive_data, daemon=True)
receive_thread.start()

try:
    main()
except:
    ser.close()
    for thread in thread_list:
        thread.join()
    print("Program Stopped")
