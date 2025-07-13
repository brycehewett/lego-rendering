import cv2
from ultralytics import YOLO

# Load your trained model
model = YOLO("./runs/detect/lego_yolov8n/weights/best.onnx")  # or "best.onnx" if exported

# Open webcam (0 = default camera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Cannot open webcam")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Inference on the frame (returns Results object)
    results = model(frame, imgsz=640, conf=0.5)

    # Annotate detections on the frame
    annotated_frame = results[0].plot()

    # Show it
    cv2.imshow("YOLOv8 Webcam Inference", annotated_frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
