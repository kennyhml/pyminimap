import pydirectinput as input
import time


class Mouse:
    """Handle movement using coordinates relative to current cursor pos"""

    @staticmethod
    def turn_to(pos):
        input.moveRel(pos, 0, None, False, False, True)

    @staticmethod
    def turn_right():
        input.moveRel(40, 0, 0, None, False, False, True)

    @staticmethod
    def turn_left():
        input.moveRel(-40, 0, 0, None, False, False, True)

    @staticmethod
    def turn_around():
        for _ in range(3):
            input.moveRel(420, 0, 0, None, False, False, True)
            time.sleep(0.07)
