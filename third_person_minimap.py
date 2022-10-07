from minimap import Minimap
import pydirectinput as input
import time


class Movement:
    """Handle movement using coordinates relative to current cursor pos"""

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


class ThirdPersonMinimap(Minimap):
    """Minimap handler for third-person game minimaps
    -----------------------------------------------

    Contructs a minimap by passed boundaries, contains methods to
    grab targets, distances and relative positions off of an image.

    This class assumes a third person game.
    """

    def __init__(self, x1, y1, x2, y2, player, front_view, rotates=False, debug=False):
        super().__init__(x1, y1, x2, y2, player, rotates, debug)
        self.front_view = front_view

    def get_target_side(self, target):
        """Takes the position of an enemy and determines if we need to turn left or right"""
        if target[0] < 1747:
            return "left"
        if target[0] > 1755:
            return "right"
        return "front"

    def get_focus_on_target(self, expected_dist, expected_rgb, direction: str):
        print(f"Looking for mob at distance {expected_dist} on the {direction} side!")
        x, y, w, h = self.front_view

        for _ in range(200):
            front_targets = self.get_target_pixels(
                rgb=expected_rgb, x1=x, y1=y, x2=w, y2=h
            )

            closest, dist = self.get_closest_target(
                front_targets, min_dist=expected_dist - 6, max_dist=expected_dist + 6
            )

            if closest:
                print(f"Target found at {closest}, {dist}m away!")
                return True

            if direction == "left":
                Movement.turn_left()
            else:
                Movement.turn_right()
