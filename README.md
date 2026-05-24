# Facial Recognition Based Automated Delivery System

A Raspberry Pi delivery prototype that combines:

- face enrollment and LBPH face recognition with OpenCV
- relay-based lock control for a delivery compartment
- optional Bluetooth robot movement through BlueDot and gpiozero

This was originally built as a bachelor's project. The repository has been cleaned up so it can be shared as a project portfolio piece without committing private face images or generated model files.

## Project Flow

1. Capture face samples for each authorized user.
2. Train an OpenCV LBPH recognizer from those samples.
3. Run the recognition loop on the Raspberry Pi camera.
4. Unlock the delivery compartment when a recognized user is detected.
5. Optionally control the robot base with a BlueDot Bluetooth controller.

## Hardware

- Raspberry Pi with camera support
- Pi Camera or USB camera
- Relay module connected to an electronic lock
- Motor driver connected to two DC motors
- Android phone with BlueDot for Bluetooth control

The default relay pin is GPIO 23. Robot motor defaults are left `(17, 20)` and right `(22, 21)`. All pins can be changed from the command line.

## Setup

Create a virtual environment and install the project:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

On Raspberry Pi hardware, install the hardware extras as well:

```bash
pip install -e ".[raspberry-pi]"
```

OpenCV's LBPH recognizer lives in the contrib package. If `opencv-contrib-python` does not install cleanly on your Raspberry Pi, install OpenCV from the Raspberry Pi package manager and then install the remaining Python packages with `pip`.

## Usage

Copy the names example and edit it for your own user IDs:

```bash
cp examples/names.example.json names.json
```

Capture 30 samples for user ID `1`:

```bash
capture-faces 1 --samples 30
```

Train the face recognizer:

```bash
train-faces
```

Test recognition without touching GPIO:

```bash
recognize-lock --names-file names.json --dry-run
```

Run recognition with the relay connected:

```bash
recognize-lock --names-file names.json --relay-pin 23 --unlock-state 0 --locked-state 1
```

If your relay is active-high instead of active-low, swap the relay states:

```bash
recognize-lock --names-file names.json --unlock-state 1 --locked-state 0
```

Start Bluetooth robot control:

```bash
robot-remote
```

## Repository Layout

```text
src/delivery_system/
  bluetooth_robot.py   BlueDot robot controller
  capture_faces.py     Camera-based face enrollment
  recognize_lock.py    Face recognition and relay lock loop
  train_model.py       LBPH model training
  vision.py            Shared OpenCV helpers

data/dataset/          Local face samples, ignored by git
models/                Local trained recognizer files, ignored by git
examples/              Example local configuration
docs/                  Project notes and hardware guidance
```

## Privacy and Safety

Face images and trained recognizer files are biometric data. They are intentionally ignored by git in this cleaned version of the repository. Keep real datasets local, get consent from participants, and do not publish face samples in a public project repo.

This project controls physical hardware. Test with `--dry-run` first, verify relay polarity, and keep the lock mechanism powered safely during development.

## License

This project is licensed under GPL-3.0. See [LICENSE](LICENSE).
