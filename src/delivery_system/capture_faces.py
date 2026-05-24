"""Capture face samples for a user ID."""

import argparse
from pathlib import Path
from typing import Optional, Sequence

from .config import DEFAULT_DATASET_DIR
from .vision import import_cv2, load_face_cascade, open_camera


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Capture face samples for training.")
    parser.add_argument("person_id", type=int, help="Numeric ID for the person being enrolled.")
    parser.add_argument("--samples", type=int, default=30, help="Number of face samples to capture.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_DATASET_DIR)
    parser.add_argument("--camera-index", type=int, default=0)
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--cascade", type=Path, help="Optional Haar cascade XML path.")
    parser.add_argument(
        "--no-flip",
        action="store_false",
        dest="flip",
        help="Do not vertically flip the camera image.",
    )
    parser.set_defaults(flip=True)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    cv2 = import_cv2()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    face_detector = load_face_cascade(cv2, args.cascade)
    camera = open_camera(cv2, args.camera_index, args.width, args.height)

    sample_count = 0
    print("[INFO] Starting face capture. Look at the camera and press ESC to stop.")

    try:
        while sample_count < args.samples:
            ok, frame = camera.read()
            if not ok:
                raise SystemExit("Could not read a frame from the camera.")

            if args.flip:
                frame = cv2.flip(frame, -1)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

            for (x, y, width, height) in faces:
                sample_count += 1
                output_path = args.output_dir / f"User.{args.person_id}.{sample_count}.jpg"
                cv2.imwrite(str(output_path), gray[y : y + height, x : x + width])
                cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 0, 0), 2)

                if sample_count >= args.samples:
                    break

            cv2.imshow("capture-faces", frame)
            key = cv2.waitKey(100) & 0xFF
            if key == 27:
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()

    print(f"[INFO] Captured {sample_count} sample(s) in {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
