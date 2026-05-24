"""Control the robot base with a BlueDot Bluetooth controller."""

import argparse
from typing import Optional, Sequence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Control the delivery robot with BlueDot.")
    parser.add_argument("--left-forward", type=int, default=17)
    parser.add_argument("--left-backward", type=int, default=20)
    parser.add_argument("--right-forward", type=int, default=22)
    parser.add_argument("--right-backward", type=int, default=21)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        from bluedot import BlueDot
        from gpiozero import Robot
        from signal import pause
    except ImportError as exc:
        raise SystemExit(
            "BlueDot robot control requires Raspberry Pi dependencies. "
            "Install them with `pip install -e .[raspberry-pi]`."
        ) from exc

    robot = Robot(
        left=(args.left_forward, args.left_backward),
        right=(args.right_forward, args.right_backward),
    )
    blue_dot = BlueDot()

    def move(position):
        if position.top:
            robot.forward()
        elif position.bottom:
            robot.backward()
        elif position.left:
            robot.left()
        elif position.right:
            robot.right()

    def stop():
        robot.stop()

    blue_dot.when_pressed = move
    blue_dot.when_moved = move
    blue_dot.when_released = stop

    print("[INFO] BlueDot robot control is running. Press Ctrl+C to exit.")
    try:
        pause()
    finally:
        robot.stop()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
