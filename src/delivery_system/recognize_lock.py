"""Recognize authorized faces and control a relay lock."""

import argparse
import time
from pathlib import Path
from typing import Optional, Sequence

from .config import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_LOCKED_STATE,
    DEFAULT_MODEL_PATH,
    DEFAULT_RELAY_PIN,
    DEFAULT_UNLOCK_STATE,
    display_name,
    load_names,
)
from .vision import create_lbph_recognizer, import_cv2, load_face_cascade, open_camera


class RelayLock:
    """Small wrapper around RPi.GPIO with a dry-run mode for development."""

    def __init__(self, pin: int, unlock_state: int, locked_state: int, dry_run: bool) -> None:
        self.pin = pin
        self.unlock_state = unlock_state
        self.locked_state = locked_state
        self.dry_run = dry_run
        self._gpio = None
        self._current_state = None

        if self.dry_run:
            print("[INFO] Dry run enabled. GPIO output will be logged but not changed.")
            return

        try:
            import RPi.GPIO as GPIO
        except ImportError as exc:
            raise SystemExit("RPi.GPIO is required on Raspberry Pi. Use --dry-run on other machines.") from exc

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self._gpio = GPIO
        self.lock()

    def unlock(self) -> None:
        self._set_state("unlocked", self.unlock_state)

    def lock(self) -> None:
        self._set_state("locked", self.locked_state)

    def cleanup(self) -> None:
        if self._gpio is not None:
            self._gpio.cleanup(self.pin)

    def _set_state(self, label: str, gpio_state: int) -> None:
        if self._current_state == label:
            return

        self._current_state = label
        if self.dry_run:
            print(f"[GPIO] Relay pin {self.pin}: {label} ({gpio_state})")
            return

        self._gpio.output(self.pin, gpio_state)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run face recognition and control the relay lock.")
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--names-file", type=Path, help="JSON map of face IDs to display names.")
    parser.add_argument("--confidence-threshold", type=float, default=DEFAULT_CONFIDENCE_THRESHOLD)
    parser.add_argument("--relay-pin", type=int, default=DEFAULT_RELAY_PIN)
    parser.add_argument("--unlock-state", type=int, choices=(0, 1), default=DEFAULT_UNLOCK_STATE)
    parser.add_argument("--locked-state", type=int, choices=(0, 1), default=DEFAULT_LOCKED_STATE)
    parser.add_argument("--camera-index", type=int, default=0)
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--cascade", type=Path, help="Optional Haar cascade XML path.")
    parser.add_argument("--dry-run", action="store_true", help="Log lock actions without using GPIO.")
    parser.add_argument("--headless", action="store_true", help="Do not open an OpenCV preview window.")
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

    if not args.model_path.exists():
        raise SystemExit(f"Model file not found: {args.model_path}. Run `train-faces` first.")

    cv2 = import_cv2()
    names = load_names(args.names_file)
    recognizer = create_lbph_recognizer(cv2)
    recognizer.read(str(args.model_path))
    face_cascade = load_face_cascade(cv2, args.cascade)
    camera = None
    lock = None

    try:
        lock = RelayLock(args.relay_pin, args.unlock_state, args.locked_state, args.dry_run)
        camera = open_camera(cv2, args.camera_index, args.width, args.height)
        min_width = int(0.1 * camera.get(3))
        min_height = int(0.1 * camera.get(4))
        font = cv2.FONT_HERSHEY_SIMPLEX

        while True:
            ok, frame = camera.read()
            if not ok:
                raise SystemExit("Could not read a frame from the camera.")

            if args.flip:
                frame = cv2.flip(frame, -1)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(min_width, min_height),
            )

            authorized_face_seen = False

            for (x, y, width, height) in faces:
                face_id, confidence = recognizer.predict(gray[y : y + height, x : x + width])
                recognized = confidence <= args.confidence_threshold
                authorized_face_seen = authorized_face_seen or recognized

                label = display_name(names, face_id) if recognized else "Unknown"
                confidence_text = f"{max(0, round(100 - confidence))}%"
                color = (0, 255, 0) if recognized else (0, 0, 255)

                cv2.rectangle(frame, (x, y), (x + width, y + height), color, 2)
                cv2.putText(frame, label, (x + 5, y - 5), font, 1, (255, 255, 255), 2)
                cv2.putText(frame, confidence_text, (x + 5, y + height - 5), font, 1, (255, 255, 0), 1)

            if authorized_face_seen:
                lock.unlock()
            else:
                lock.lock()

            if args.headless:
                time.sleep(0.05)
                continue

            cv2.imshow("recognize-lock", frame)
            key = cv2.waitKey(10) & 0xFF
            if key == 27:
                break
    finally:
        if lock is not None:
            lock.lock()
            lock.cleanup()
        if camera is not None:
            camera.release()
        if not args.headless:
            cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
