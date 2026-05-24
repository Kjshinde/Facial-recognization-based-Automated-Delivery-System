"""OpenCV helpers shared by the CLI commands."""

from pathlib import Path
from typing import Optional


def import_cv2():
    try:
        import cv2
    except ImportError as exc:
        raise SystemExit(
            "OpenCV is required. Install dependencies with `pip install -e .` "
            "or install OpenCV on the Raspberry Pi through apt."
        ) from exc

    return cv2


def create_lbph_recognizer(cv2):
    if not hasattr(cv2, "face") or not hasattr(cv2.face, "LBPHFaceRecognizer_create"):
        raise SystemExit(
            "LBPH face recognition requires opencv-contrib-python. "
            "Install it with `pip install opencv-contrib-python`."
        )

    return cv2.face.LBPHFaceRecognizer_create()


def load_face_cascade(cv2, cascade_path: Optional[Path] = None):
    candidates = []

    if cascade_path is not None:
        candidates.append(cascade_path)

    haarcascade_dir = getattr(getattr(cv2, "data", None), "haarcascades", None)
    if haarcascade_dir:
        candidates.append(Path(haarcascade_dir) / "haarcascade_frontalface_default.xml")

    candidates.append(Path("haarcascade_frontalface_default.xml"))

    for candidate in candidates:
        if not candidate.exists():
            continue

        cascade = cv2.CascadeClassifier(str(candidate))
        if not cascade.empty():
            return cascade

    searched = ", ".join(str(path) for path in candidates)
    raise SystemExit(f"Could not load Haar cascade. Checked: {searched}")


def open_camera(cv2, camera_index: int, width: int, height: int):
    camera = cv2.VideoCapture(camera_index)

    if not camera.isOpened():
        raise SystemExit(f"Could not open camera index {camera_index}")

    camera.set(3, width)
    camera.set(4, height)
    return camera
