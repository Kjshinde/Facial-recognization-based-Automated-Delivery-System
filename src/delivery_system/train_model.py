"""Train an LBPH recognizer from captured face samples."""

import argparse
import re
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from .config import DEFAULT_DATASET_DIR, DEFAULT_MODEL_PATH
from .vision import create_lbph_recognizer, import_cv2


DATASET_FILE_RE = re.compile(r"^User\.(\d+)\.\d+\.(?:jpg|jpeg|png)$", re.IGNORECASE)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train the face recognition model.")
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET_DIR)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
    return parser


def load_training_samples(dataset_dir: Path) -> Tuple[List[object], List[int]]:
    try:
        import numpy as np
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("Training requires numpy and Pillow. Install dependencies with `pip install -e .`.") from exc

    if not dataset_dir.exists():
        raise SystemExit(f"Dataset directory not found: {dataset_dir}")

    faces = []
    ids = []

    for image_path in sorted(dataset_dir.iterdir()):
        if not image_path.is_file():
            continue

        match = DATASET_FILE_RE.match(image_path.name)
        if match is None:
            continue

        image = Image.open(image_path).convert("L")
        faces.append(np.array(image, "uint8"))
        ids.append(int(match.group(1)))

    return faces, ids


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    cv2 = import_cv2()
    recognizer = create_lbph_recognizer(cv2)
    faces, ids = load_training_samples(args.dataset_dir)

    if not faces:
        raise SystemExit(f"No training samples found in {args.dataset_dir}")

    import numpy as np

    args.model_path.parent.mkdir(parents=True, exist_ok=True)
    recognizer.train(faces, np.array(ids))
    recognizer.write(str(args.model_path))

    print(
        f"[INFO] Trained {len(set(ids))} user(s) from {len(faces)} sample(s). "
        f"Model saved to {args.model_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
