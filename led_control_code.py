import cv2
import mediapipe as mp
import serial
import time

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

def count_fingers(hand_landmarks):
    """Count the number of fingers extended."""
    if not hand_landmarks:
        return 0

    landmarks = hand_landmarks[0].landmark
    finger_tips = [4, 8, 12, 16, 20]  # Tip landmarks for fingers

    # Count extended fingers
    count = 0
    for i in range(1, 5):
        if landmarks[finger_tips[i]].y < landmarks[finger_tips[i] - 2].y:
            count += 1
    return count

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        # Draw landmarks and connections
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        # Count fingers and send to Arduino
        num_fingers = count_fingers(results.multi_hand_landmarks)
        print(f'Number of fingers: {num_fingers}')  # Debugging output
        ser.write(f"{num_fingers}\n".encode())  # Send number of fingers to Arduino

    # Display FPS
    new_time = time.time()
    fps = int(1 / (new_time - prev_time))
    frame = cv2.putText(frame, f'FPS: {fps}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    
    # Show frame
    cv2.imshow('Hand Detection', frame)
    
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key to exit
        break

    prev_time = new_time

cap.release()
cv2.destroyAllWindows()
ser.close()
