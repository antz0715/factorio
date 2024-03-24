import pygame as pg
from numpy import zeros

from constants import consts as c
from id_mapping import id_map, reverse_id_map

#2d array
# Sets up the game world when the game starts. It creates a grid representing the game area 
# and places some initial resources on it.
# Imagine laying out a giant board game on the floor. This board is made up of lots of little squares (the grid).
# When you first set up the game, you place some special squares that represent coal, iron, and copper in specific spots. 
# These are like treasure spots where players can find resources.
class World:
    def __init__(self):
        self.grid = zeros((c.num_cells, c.num_cells), dtype=int)
        self.ore_locations = []

        self.grid[10:13, 10:12] = id_map["coal"]
        self.grid[15:17, 15:17] = id_map["iron_ore"]
        self.grid[15:17, 20:23] = id_map["copper_ore"]
        self.populate_ore_locations()
#  Goes through the entire grid and remembers where all the resources are placed.
# After setting up the game board, you take a notebook and write down where all the treasures are hidden.
# This way, you won't forget where you put the coal, iron, and copper.
    def populate_ore_locations(self):
        for row in range(c.num_cells):
            for col in range(c.num_cells):
                if self.grid[row, col] > 0:
                    self.ore_locations.append((row, col))
# draws the resources on the screen, so the player can see where they are
# Now that the game is set up and you know where the treasures are, you use colored markers to draw them on the board.
# Each type of resource (coal, iron, copper) has its own color, so it's easy to see what's what.
    def render(self):
        for loc in self.ore_locations:
            row, col = loc
            x = col * c.cell_length - c.player_x
            y = row * c.cell_length - c.player_y
            pg.draw.rect(c.screen, c.ore_colors[self.grid[loc]], (x, y, c.cell_length, c.cell_length))
# When the player moves the mouse over a resource, this shows a little box with the resource's name.
# If you hover a magnifying glass over a treasure spot, a small note pops up telling you what kind of treasure is there.
# This helps you remember whether it's coal, iron, or copper.
    def render_tooltip(self, row, col):
        x, y = pg.mouse.get_pos()
        ore = reverse_id_map[self.grid[row, col]].replace("_", " ").title()
        ore_text = c.merriweather.render(ore, True, pg.Color("white"))
        pg.draw.rect(c.screen, pg.Color("black"), (x + 10, y + 10, ore_text.get_width() + 20, ore_text.get_height() + 20))
        c.screen.blit(ore_text, (x + 20, y + 20))


world = World()