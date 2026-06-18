import argparse
import csv
import json
import random
from pathlib import Path

import cv2
import mediapipe as mp

from app.core.config import settings

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


LABEL_MAP = {
    "fist": "fist",
    "palm": "palm",
    "stop": "palm",
    "like": "thumbs_up",
    "ok": "ok",
    "peace": "peace",
    "one": "number_1",
    "two_up": "number_2",
    "three": "number_3",
    "four": "number_4",
}


def normalize_landmark_list(landmarks) -> list[float]:
    raw_points = landmarks.landmark if hasattr(landmarks, "landmark") else landmarks
    points = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in raw_points]
    wrist = points[0]
    middle_base = points[9]
    base = (
        (middle_base["x"] - wrist["x"]) ** 2
        + (middle_base["y"] - wrist["y"]) ** 2
        + (middle_base["z"] - wrist["z"]) ** 2
    ) ** 0.5 or 1e-6

    out: list[float] = []
    for point in points:
        out.extend(
            [
                (point["x"] - wrist["x"]) / base,
                (point["y"] - wrist["y"]) / base,
                (point["z"] - wrist["z"]) / base,
            ]
        )
    return out


def load_image_items(annotation_path: Path, source_label: str) -> list[tuple[str, list[float] | None]]:
    with annotation_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        items: list[tuple[str, list[float] | None]] = []
        for image_name, meta in data.items():
            labels = meta.get("labels", [])
            bboxes = meta.get("bboxes", [])
            bbox = None
            if source_label in labels:
                idx = labels.index(source_label)
                if idx < len(bboxes):
                    bbox = bboxes[idx]
            items.append((image_name, bbox))
        return items
    if isinstance(data, list):
        return [(item["image_id"], item.get("bbox")) for item in data if "image_id" in item]
    raise ValueError(f"Unsupported annotation format: {annotation_path}")


def crop_bbox(image, bbox: list[float] | None, padding: float):
    if not bbox:
        return image
    height, width = image.shape[:2]
    x, y, w, h = bbox
    pad_x = w * padding
    pad_y = h * padding
    left = max(0, int((x - pad_x) * width))
    top = max(0, int((y - pad_y) * height))
    right = min(width, int((x + w + pad_x) * width))
    bottom = min(height, int((y + h + pad_y) * height))
    if right <= left or bottom <= top:
        return image
    return image[top:bottom, left:right]


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract MediaPipe 63D features from HaGRID images.")
    parser.add_argument("--dataset-root", type=Path, default=settings.dataset_root)
    parser.add_argument("--max-per-class", type=int, default=800)
    parser.add_argument("--classes", nargs="*", default=None, help="Optional source class names to process.")
    parser.add_argument("--bbox-padding", type=float, default=1.0)
    parser.add_argument(
        "--model",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "app" / "models" / "hand_landmarker.task",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    random.seed(args.seed)
    raw_root = args.dataset_root / "raw" / "hagrid" / "hagrid-sample-500k-384p"
    image_root = raw_root / "hagrid_500k"
    annotation_root = raw_root / "ann_train_val"
    out_path = args.dataset_root / "features" / "static" / "gesture_data.csv"

    if not image_root.exists() or not annotation_root.exists():
        raise SystemExit(f"HaGRID extract directory not found: {raw_root}")
    if out_path.exists() and not args.overwrite:
        raise SystemExit(f"Output already exists: {out_path}. Use --overwrite to replace it.")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    header = ["label"] + [f"{axis}{idx}" for idx in range(21) for axis in ("x", "y", "z")]

    written = 0
    failed = 0
    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(args.model)),
        running_mode=VisionRunningMode.IMAGE,
        num_hands=1,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    with HandLandmarker.create_from_options(options) as landmarker:
        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)

            selected_items = LABEL_MAP.items()
            if args.classes:
                selected = set(args.classes)
                selected_items = [(source, target) for source, target in LABEL_MAP.items() if source in selected]

            for source_label, target_label in selected_items:
                annotation_path = annotation_root / f"{source_label}.json"
                class_dir = image_root / f"train_val_{source_label}"
                if not annotation_path.exists() or not class_dir.exists():
                    print(f"skip missing class: {source_label}")
                    continue

                image_items = load_image_items(annotation_path, source_label)
                random.shuffle(image_items)
                image_items = image_items[: args.max_per_class]
                class_written = 0

                for image_name, bbox in image_items:
                    image_path = class_dir / image_name
                    if not image_path.suffix:
                        image_path = image_path.with_suffix(".jpg")
                    image = cv2.imread(str(image_path))
                    if image is None:
                        failed += 1
                        continue

                    image = crop_bbox(image, bbox, args.bbox_padding)
                    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                    result = landmarker.detect(mp_image)
                    if not result.hand_landmarks:
                        failed += 1
                        continue

                    feature = normalize_landmark_list(result.hand_landmarks[0])
                    writer.writerow([target_label, *feature])
                    written += 1
                    class_written += 1

                print(f"{source_label} -> {target_label}: {class_written}/{len(image_items)}")

    print(f"saved: {out_path}")
    print(f"written: {written}, failed: {failed}")


if __name__ == "__main__":
    main()
