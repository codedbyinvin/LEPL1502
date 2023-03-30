import numpy as np
import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

horizontal_vector = np.array([1,0])

def angle(v1, v2):
    v1_u = v1 / np.linalg.norm(v1)
    v2_u = v2 / np.linalg.norm(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def d(x1, y1, x2, y2):
    return np.sqrt((x2-x1)**2 + (y2-y1)**2)

# For webcam input:
cap = cv2.VideoCapture(0)
with mp_hands.Hands(
    model_complexity=1,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.5) as hands:

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
            vector_left, vector_right = np.array([0,0]), np.array([0,0])
            angles = [0,0]
            for hand_landmarks in results.multi_hand_landmarks:
                handIndex = results.multi_hand_landmarks.index(hand_landmarks)
                handLabel = results.multi_handedness[handIndex].classification[0].label
                if handLabel == "Left":
                    vector_left = np.array([hand_landmarks.landmark[5].x - hand_landmarks.landmark[17].x, hand_landmarks.landmark[5].y - hand_landmarks.landmark[17].y])
                    angles[1] = np.degrees(angle(vector_left, horizontal_vector))
                elif handLabel == "Right":
                    vector_right = np.array([hand_landmarks.landmark[5].x - hand_landmarks.landmark[17].x, hand_landmarks.landmark[5].y - hand_landmarks.landmark[17].y])
                    angles[0] = np.degrees(angle(vector_right, horizontal_vector))


                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
                
            data = str("L:" + str(round(angles[1],2))+ "°" + "\t R:" + str(round(angles[0],2))+"°"  + "\n")
            print(data)
        # Flip the image horizontally for a selfie-view display.
        cv2.imshow('MediaPipe Hands', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break
    cap.release()