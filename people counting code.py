from ultralytics import YOLO
import cv2
import requests
import time

# YOLO model
MODEL_PATH = "Final1/CrowdDetection/best.pt"
model = YOLO(MODEL_PATH)

# ESP32 IP from Serial Monitor
ESP32_IP = "192.168.128.6" 

# External webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("External webcam Not open!")
    exit()

print("Webcam ON - Press Q to close")

last_send_time = 0
send_interval = 1  # Send count every 1 second

while True:
    ret, frame = cap.read()

    if not ret:
        print("video not come from Webcam!")
        break

    # Detect persons using best.pt
    results = model.predict(
    frame,
    classes=[0],
    imgsz=320,
    verbose=False
     )

    result = results[0]
    person_count = len(result.boxes)

    # Send ONLY crowdG1 to ESP32
    current_time = time.time()

    if current_time - last_send_time >= send_interval:
        try:
            url = f"http://{ESP32_IP}/count?g2={person_count}"

            response = requests.get(url, timeout=2)

            print(f"Sent crowdG2 = {person_count}")
            print("ESP32:", response.text)

        except requests.exceptions.RequestException as e:
            print("ESP32 not reachable:", e)

        last_send_time = current_time

    # Display detection
    display_frame = result.plot()

    cv2.putText(
        display_frame,
        f"G2 Crowd: {person_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("G2 LIVE WEBCAM - PERSON DETECTION", display_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()