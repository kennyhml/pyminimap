from minimap import Minimap
import math

class IsometricMinimap(Minimap):
    """Minimap handler for isometric game minimaps
    -----------------------------------------------

    Contructs a minimap by passed boundaries, contains methods to
    grab targets, distances and relative positions off of an image.

    This class assumes an isometric, top-down view game.
    """

    def position_to_direction(self, target: tuple, multiplier=6) -> tuple:
        """Takes a target found on the minimap and returns the direction to walk
        assuming an isometric game where the player is in the middle of the screen.

        The multiplier gets more important the smaller the distance to the target is.

        Parameters
        ----------
        target: `tuple`
            The target or point on the minimap to direct towards

        multiplier `int`
            The multiplier for the length of the direction outgoing from the center

        Returns
        ----------
        A tuple containing the point to move to and the distance to the enemy
        """
        if not target:
            return None, None

        center = 960, 540
        m = multiplier
        dist = math.dist(target, self._player)
        return (
            (
                (center[0] + (target[0] - self._player[0]) * m),
                (center[1] + (target[1] - self._player[1]) * m),
            ),
            dist,
        )
