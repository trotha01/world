How to make a map:
===

It is probably best to follow along while looking at an example .map file.

Create your file "someMapname.map"
----
Inside this file, create a [level] section

[level]
---
 - Add a tileset key linking to a image to use for this map
     tileset = myimage.png
 - Create a map with an ascii characters
 - Create a new section for each ascii character in this map
```txt
[level]
tileset = myimage.png
map =   ####222########
        #......#h...h.#
        #....@.#......#
        #......#......#
        #......#h...h.#
        #......#......#
        #......#......#
        #......#h..sh.#
        #......#......#
        3.............#
        #......########
        #.............#
        #.............#
        #.............#
        ###############
```

[Ascii Char]
---
 - Name this piece of the map using name = yourpiecename
 - If it is a wall, say so with 'wall = true'
 - If it is something that blocks a character, like a wall or a tree or something, say so with 'block=true'
 - Give the tile location in your image with 'tile=x, y' where x and y are the x and y block coordinates in your tileset image. So 0, 0 is the top left block, and 1, 0 is the block to the right of that.
 - Currently wall tiles coordinates from the image are determined dynamically in gameMap.py. Still trying to figure out a simple way to give the user control over this.

```txt
[#]
name = wall
wall = true
block = true

[.]
name = floor
tile = 0, 3
```

### If the piece is a sprite:
- Give the sprite image with 'sprite=spriteImage.png'
- If the piece is the main player, use 'player=true'

```txt
[s]
name = skeleton
tile = 0, 3
sprite = skeleton.png
block = true
```

### If the piece connects to another level:
 - If the piece wants the character transported to the new level right away, write 'connect=auto'
 - Else, if the piece wants the character transported when they use a meta-key, write 'connect=metakey'. And use pygame constantss to define the key, 'key=K\_UP' for the up key.
 - If the piece wants the character to change to that level while the character is, say, in front of that tile, write 'connectlocation=South'
 - Else write 'connectlocation=0'
 - We must also say the level the player will be transported to with 'level=newlevel.map'. Don't forget to have a 'newlevel.map' file.

```txt
[2]
name = floor
tile = 0, 3
connect = metakey
key = K_UP
connectlocation = 0
level = level2.map

[3]
name = floor
tile = 0, 3
connect = auto
connectlocation = 0
level = level3.map
```

### If the piece has audio:
 - Write 'audio=true'
 - Write where the player has to be standing to hear the audio, 'audiodirection = South'. The meta-key used to define audio (spacebar maybe) is defined in the game.
 - Write the audio says 'speech = thing\_to\_say'
 - When the game is initiated, we find the audio for 'thing\_to\_say' in the language file, for example 'spanish.py'.

```txt
[s]
name = skeleton
tile = 0, 3
sprite = skeleton.png
block = true
audio = true
audioDirection = South
speech = street_greeting
 ```
