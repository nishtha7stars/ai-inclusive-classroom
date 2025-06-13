import cv2
from fer import FER

detector = FER(mtcnn=True)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    result = detector.detect_emotions(frame)
    for face in result:
        (x, y, w, h) = face["box"]
        emotion, score = max(face["emotions"].items(), key=lambda item: item[1])
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(frame, f"{emotion}: {score:.2f}", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
    cv2.imshow("Live Emotion Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()