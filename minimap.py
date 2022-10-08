import math
from mss import mss, tools
import pyautogui as pg
import cv2 as cv
import numpy as np
import win32gui, win32api, win32con
from win32api import GetSystemMetrics
from threading import Thread


class Minimap:
    """Minimap handle for various minimaps in games
    -----------------------------------------------

    Contructs a minimap by passed boundaries, contains methods to
    grab targets, distances and relative positions off of an image.

    Depending on the nature of the game, the minimap may behave differently
    and some methods will not work as intended. Good examples of useful minimaps
    are Lost Ark and Black Desert Online.
    """

    def __init__(self, x1, y1, x2, y2, player, rotates=False, debug=False) -> None:
        self._boundaries = (x1, y1, x2, y2)
        self._player = player
        self._rotates = rotates
        self._debug = debug

    @property
    def boundaries(self):
        return self._boundaries

    @property
    def player(self):
        return self._player

    @boundaries.setter
    def boundaries(self, boundaries):
        self._boundaries = boundaries

    @player.setter
    def player(self, player):
        self._player = player

    def grab_minimap(self, path: str) -> str:
        """Grabs a screenshot of the minimap

        Parameters
        -----------
        path: `str`
            The path to save the image in

        Returns
        -----------
        path `str`
            The path the image was saved in, for convenience

        """
        with mss() as sct:
            # set region
            x, y, w, h = self._boundaries
            region_dict = {"left": x, "top": y, "width": w, "height": h}

            # grab img
            img = sct.grab(region_dict)
            # Save to the picture file
            tools.to_png(img.rgb, img.size, output=path)
        return path

    def get_target_pixels(self, rgb: tuple, variance=10, x1=None, y1=None, x2=None, y2=None) -> set | None:
        """Finds all matching targets on the minimap

        Parameters
        -----------
        rgb: `tuple`
            The rgb value to match for

        variance: `int`
            How much the rgb can vary

        Returns
        ----------
        A list of matching points, otherwise None
        """
        try:
            if not x1:
                x1, y1, x2, y2 = self._boundaries
            image = pg.screenshot(region=(x1, y1, x2, y2))
            image = cv.cvtColor(np.array(image), 0)
            cv.imwrite("images/temp/test.png", image)

        except Exception as e:
            print(f"Ran into an error trying to grab targets!\n{e}")
            return

        # convert to BGR
        image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
        # mask
        lower_bound = (
            max(0, rgb[2] - variance),
            max(0, rgb[1] - variance),
            max(0, rgb[0] - variance),
        )
        upper_bound = (
            min(255, rgb[2] + variance),
            min(255, rgb[1] + variance),
            min(255, rgb[0] + variance),
        )
        # image, lower_bound, upper_bound. BGR!
        mask = cv.inRange(image, lower_bound, upper_bound)
        matches = cv.findNonZero(mask)
        if matches is None:
            return

        # get all matching pixels
        return set(
            (self._boundaries[0] + x, self._boundaries[1] + y)
            for x, y in np.concatenate(matches, axis=0)
        )

    def get_closest_target(self, targets, min_dist=0, max_dist=100) -> tuple:
        """Takes a list of points and finds the point closest to the player
        and converts the point into the direction to face towards it.

        Parameters
        ----------
        targets: `set`
            A set of targets to check for the closest

        min_dist: `int`
            The minimum distance to the player

        max_dist: `int`
            The maximum distance to the player

        Returns
        ----------
        A tuple containing the position of the closest target and the distance
        or `None, None` if no target was found
        """
        if not targets:
            return None, None

        distances = []

        # create a list of tuples containing position and distance
        for position in targets:
            distance_to_player = math.dist(position, self._player)
            distances.append(tuple([*position, distance_to_player]))

        # create a sorted list of distances
        sorted_distances = sorted(
            list(set(val[2] for val in distances if max_dist > val[2] > min_dist))
        )

        try:
            closest_match = sorted_distances[0]
        except IndexError:
            print("No targets found in the given distance frame!")
            return None, None

        # search for the position of the distance
        for data in distances:
            if data[2] == closest_match:
                coords = (data[0], data[1])
                break

        if self._debug:
            self.show_target(coords)

        return coords, closest_match

    def filter_targets(self, targets: set, min_dist: int | float) -> set:
        """Filters points of a set where distance < min_dist

        Parameters
        ----------
        targets: `set`
            The set of points to filter

        min_dist: `int` | `float`
            The minimum distance between point A and B

        Returns
        ----------
        A set of filtered target points
        """
        filtered = set()
        while targets:
            eps = targets.pop()
            for point in targets:
                if all(abs(c2 - c1) < min_dist for c2, c1 in zip(eps, point)):
                    break
            else:
                filtered.add(eps)

        return filtered

    def show_target(self, pos: tuple, size=5, rgb=(0, 255, 0)) -> None:
        """For DEBUGGING / TESTING purposes only!
        ----------

        Flashes the position of the grabbed target by drawing a rectangle
        around it using win32gui API.

        Note that I have not found a method to clear the rectangles other than
        restarting the bot. They simply go hidden quickly, but are NOT gone!

        Parameters:
        ----------
        position: `tuple`
            The point to draw the rect around

        size: `int`
            The size of the rectangle where size^2 is the area

        rgb: `tuple`
            The rgb of the rectangle, default green
        """
        Thread(
            target=self.draw_rectangle,
            args=(
                pos,
                size,
                rgb,
            ),
            name="Showing enemy",
        ).start()

    def draw_rectangle(self, m: tuple, size: int, rgb: tuple) -> None:
        """Draws the rectangle using windows api, its actually drawn pixel by pixel
        but at a fast rate so its barely noticable. It needs to run in a seperate thread
        though as it pulls on performance and takes some miliseconds to properly display."""

        # get handles
        dc = win32gui.GetDC(0)
        hwnd = win32gui.WindowFromPoint((0, 0))
        monitor = (0, 0, GetSystemMetrics(0), GetSystemMetrics(1))
        red = win32api.RGB(*rgb)  # Red
        past_coordinates = monitor

        # create the rectangle with scuffed math
        x, y = m
        d1, d2 = size, size
        topleft = (x - d1, y - d2)  # top-left
        bottomleft = (x - d1, y + d2)  # bottom-left
        topright = (x + d1, y - d2)  # top-right
        bottomright = (x + d1, y + d2)  # bottom-right

        # increase iterations for a longer / shorter display
        for _ in range(60):
            rect = win32gui.CreateRoundRectRgn(*past_coordinates, 2, 2)
            win32gui.RedrawWindow(hwnd, past_coordinates, rect, win32con.RDW_INVALIDATE)

            for x in range(topleft[0], topright[0]):
                win32gui.SetPixel(dc, x, topleft[1], red)

            for y in range(topright[1], bottomright[1]):
                win32gui.SetPixel(dc, topright[0], y, red)

            for x in range(bottomleft[0], bottomright[0]):
                win32gui.SetPixel(dc, x, bottomleft[1], red)

            for y in range(topleft[1], bottomleft[1]):
                win32gui.SetPixel(dc, topleft[0], y, red)

            past_coordinates = (m[0] - 20, m[1] - 20, m[0] + 20, m[1] + 20)
