# pyminimap
pyminimap is just some cool stuff I came up with while messing with some games.

The basic concept is to read pixels/templates from a minimap and putting it into relation to the player
position to direct movements or attacks towards enemies. This is mainly achieved by using modules such as
numpy, cv2 and pyautogui.

It works best for isometric games.

# Usage

Create a minimap object given the boundaries of the in-game minimap and the player position:
```py
minimap = IsometricMinimap(x1=1661, y1=67, x2=184, y2=181, player=(1753, 160))
```
ㅤ

Now, for example, you can find your closest target by rgb value:
```py
possible_targets = minimap.get_target_pixels(rbg=(90, 10, 40), variance=5)
target_pos, target_dist = minimap.get_closest_target(possible_targets, min_dist=4)
```
ㅤ

Thus we have found the position of the closest target to our player on the minimap.

We can proceed by converting that point into a direction for our player to walk:
```py
direction = minimap.position_to_direction(target_pos, multiplier=6)
```
ㅤ

If we now move to the returned position, our player will walk the same direction as the target on the minimap is relative to the player.


# I do not encourage any sort of botting

Please use this like a grown man, I will not take responsibility if you get banned for breaching games ToS (*which you will eventually!*)

The purpose of this is to see how close to a proper injected or packet-rading bot I can get by just reading pixels, not to ruin anyones fun!



