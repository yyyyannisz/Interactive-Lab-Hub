import cv2
import numpy as np
from tflite_runtime.interpreter import Interpreter

# ---------------------------------------------------
# Config
# ---------------------------------------------------
MODEL_PATH = "models/phone_detection/model.tflite"
LABELS_PATH = "models/phone_detection/labels.txt"
CONFIDENCE_THRESHOLD = 0.85   # normalized (0?1)

# ---------------------------------------------------
# Load labels
# ---------------------------------------------------
labels = []
with open(LABELS_PATH, "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        # Expect format: "0 no_phone" or "1 phone"
        labels.append(line.split()[1].lower())

print("Loaded labels:", labels)

# ---------------------------------------------------
# Load TFLite model
# ---------------------------------------------------
interpreter = Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

H = input_details[0]["shape"][1]
W = input_details[0]["shape"][2]
print(f"Model input size: {W}x{H}")
print(f"Model input dtype: {input_details[0]['dtype']}")

# ---------------------------------------------------
# Open webcam
# ---------------------------------------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Could not open webcam")

print("Webcam opened. Phone detection test running.")
print("Press Ctrl+C to stop.")

# ---------------------------------------------------
# Main loop
# ---------------------------------------------------
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Resize to model input size
        img = cv2.resize(frame, (W, H))

        # Quantized model expects UINT8 input
        img = np.expand_dims(img, axis=0).astype(np.uint8)

        # Run inference
        interpreter.set_tensor(input_details[0]["index"], img)
        interpreter.invoke()

        preds = interpreter.get_tensor(output_details[0]["index"])[0]

        # Normalize UINT8 outputs to 0?1
        scores = preds / 255.0

        no_phone_score = scores[labels.index("no_phone")]
        phone_score = scores[labels.index("phone")]

        print(f"[scores] no_phone: {no_phone_score:.2f}, phone: {phone_score:.2f}")

        # Decision logic
        if phone_score >= CONFIDENCE_THRESHOLD:
            print(f"PHONE detected ({phone_score:.2f})\n")
        else:
            print(f"no_phone ({no_phone_score:.2f})\n")

except KeyboardInterrupt:
    print("\nStopping test...")

finally:
    cap.release()
    print("Webcam released.")

