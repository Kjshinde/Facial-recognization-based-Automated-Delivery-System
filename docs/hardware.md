# Hardware Notes

## Relay Lock

The recognition command defaults to GPIO 23 and an active-low relay:

```bash
recognize-lock --relay-pin 23 --unlock-state 0 --locked-state 1
```

Many relay modules unlock when the GPIO output is low. If your relay unlocks when the output is high, swap the states:

```bash
recognize-lock --unlock-state 1 --locked-state 0
```

Use `--dry-run` before connecting the lock so you can verify recognition behavior without changing GPIO output.

## Robot Motors

The robot controller uses gpiozero's `Robot` abstraction. Defaults:

- left motor: GPIO 17 and GPIO 20
- right motor: GPIO 22 and GPIO 21

Override pins when your motor driver wiring differs:

```bash
robot-remote --left-forward 17 --left-backward 20 --right-forward 22 --right-backward 21
```

## Camera Orientation

The original prototype flipped the camera image vertically because of the physical camera mount. The cleaned commands keep that behavior by default. Add `--no-flip` if your camera is mounted normally.
