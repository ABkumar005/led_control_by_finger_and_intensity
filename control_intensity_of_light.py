import cv2
import mediapipe as mp
import serial
import time
import math

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Initialize Serial Communication
ser = serial.Serial('COM7', 9600)  # Replace 'COM7' with your Arduino's COM port
time.sleep(2)  # Allow time for the serial connection to initialize

# Initialize Camera
cap = cv2.VideoCapture(0)

prev_time = 0

def calculate_distance(landmark1, landmark2):
    """Calculate the Euclidean distance between two landmarks."""
    x1, y1 = landmark1.x, landmark1.y
    x2, y2 = landmark2.x, landmark2.y
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Get the landmarks for the index and middle fingers
            landmarks = hand_landmarks.landmark
            index_finger_tip = landmarks[8]  # Tip of the index finger
            middle_finger_tip = landmarks[12]  # Tip of the middle finger
            
            # Calculate the distance between the index and middle finger tips
            distance = calculate_distance(index_finger_tip, middle_finger_tip)
            
            # Print the distance for debugging
            print(f'Distance: {distance:.2f}')
            
            # Adjust scaling factor as needed
            min_distance = 0.05  # Minimum expected distance
            max_distance = 0.2   # Maximum expected distance
            if distance < min_distance:
                distance = min_distance
            elif distance > max_distance:
                distance = max_distance
            
            # Map the distance to a value between 0 and 255
            intensity = int((distance - min_distance) / (max_distance - min_distance) * 255)
            
            # Map the intensity to four LEDs
            # This can be split into four segments, each controlling one LED
            led1_intensity = min(max(intensity - 192, 0), 255)   # For LED 1 (Pin 2)
            led2_intensity = min(max(intensity - 128, 0), 255)   # For LED 2 (Pin 3)
            led3_intensity = min(max(intensity - 64, 0), 255)    # For LED 3 (Pin 4)
            led4_intensity = min(intensity, 255)                  # For LED 4 (Pin 5)
            
            # Send the LED intensities to Arduino
            ser.write(f"{led1_intensity},{led2_intensity},{led3_intensity},{led4_intensity}\n".encode())
            
            # Draw intensity on the frame for debugging
            frame = cv2.putText(frame, f'LED1: {led1_intensity} LED2: {led2_intensity} LED3: {led3_intensity} LED4: {led4_intensity}', 
                                (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

    # Display FPS
    new_time = time.time()
    fps = int(1 / (new_time - prev_time))
    frame = cv2.putText(frame, f'FPS: {fps}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    
    # Show frame
    cv2.imshow('Hand Detection', frame)
    
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key to exit
        break

    prev_time = new_time

cap.release()
cv2.destroyAllWindows()
ser.close()
