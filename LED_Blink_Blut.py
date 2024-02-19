"""from bluedot import BlueDot 
from gpiozero import LED

bd = BlueDot()
led = LED(17)
led_2 = LED(18)

while True:
    bd.wait_for_press()
    led.on()
    led_2.on()
    bd.wait_for_release()
    led.off()
    led_2.off()"""

from bluedot import BlueDot
from gpiozero import Robot
from signal import pause

bd = BlueDot()
robot = Robot(left=(17, 18), right=(22, 23))

def move(pos):
    if pos.top:
        robot.forward()
    elif pos.bottom:
        robot.backward()
    elif pos.left:
        robot.left()
    elif pos.right:
        robot.right()

def stop():
    robot.stop()

bd.when_pressed = move
bd.when_moved = move
bd.when_released = stop

pause()