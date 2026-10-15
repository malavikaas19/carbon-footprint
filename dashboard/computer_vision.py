
from functools import lru_cache
from pathlib import Path

import cv2
from ultralytics import YOLO


@lru_cache(maxsize=1)
def get_model():
    """Load the model once and reuse it."""
    return YOLO("yolo11n.pt")


def detect_objects(image_path, annotated_image_path=None):
    """
    Detect supported objects in an image.

    Returns:
        detections: list of detected objects
        object_counts: count per category
        total_objects: total detections
    """
    model = get_model()

    results = model.predict(
        source=str(image_path),
        conf=0.25,
        iou=0.45,
        verbose=False,
    )

    detections = []
    object_counts = {}

    for result in results:

        # Save image with YOLO bounding boxes and labels
        if annotated_image_path:
            output_path = Path(annotated_image_path)
            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            annotated_image = result.plot()

            if not cv2.imwrite(
                str(output_path),
                annotated_image,
            ):
                raise OSError(
                    f"Unable to save annotated image: {output_path}"
                )

        # Collect all detections
        for box in result.boxes:
            class_id = int(box.cls[0].item())
            confidence = float(box.conf[0].item())
            name = result.names[class_id]

            x1, y1, x2, y2 = [
                round(value)
                for value in box.xyxy[0].tolist()
            ]

            detections.append({
                "name": name,
                "confidence": round(confidence * 100, 1),
                "box": [x1, y1, x2, y2],
            })

            object_counts[name] = (
                object_counts.get(name, 0) + 1
            )

    return {
        "detections": detections,
        "object_counts": object_counts,
        "total_objects": len(detections),
    }
