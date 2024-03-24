from constants import consts as c
from structures.conveyor import Conveyor, ConveyorUnderground
from id_mapping import id_map, reverse_id_map
from images import img as i
from structures.splitter import Splitter
from ui.game_ui import ui


#In your game, items are objects that can be resources, tools, 
#or anything the player can interact with. The Item class represents these items,
# and the ItemManager class manages all the items in the game world.

class Item: #Sets up a new item
    def __init__(self, row, col, item):
        self.item = item
        self.item_name = reverse_id_map[item].replace("_", " ").title()
        self.row = row
        self.col = col
        self.calc_position()
# Imagine every item in the game living on a giant grid, like a checkerboard. 
#Each item knows where it sits on this board (row and col), what it is (item), 
#and few other things like which way it last moved and if it should be seen.
# To add a new type of resource, like "wood" or "stone", we tell the game what it is here.
        self.last_dir = None
        self.caught = False
        self.display = True


# Moves the item in a specific direction.
# If an item is on a conveyor belt, this is like telling it, 
#"Hey, go left," or "Hey, go right," so it knows where to slide next on our checkerboard.
    def move(self, direction):
        if self.last_dir is not None and direction != self.last_dir:
            self.calc_position()

        if direction == "left":
            self.x -= c.conveyor_speed * c.dt
        elif direction == "right":
            self.x += c.conveyor_speed * c.dt
        elif direction == "up":
            self.y -= c.conveyor_speed * c.dt
        elif direction == "down":
            self.y += c.conveyor_speed * c.dt

        self.last_dir = direction

        self.row = int(self.y / c.cell_length)
        self.col = int(self.x / c.cell_length)

#Calculates the item's exact spot on the screen.
#This is a bit like using a map to find a treasure. 
#It figures out exactly where to show our item on the game screen.
    def calc_position(self):
        self.x = self.col * c.cell_length + c.cell_length // 2
        self.y = self.row * c.cell_length + c.cell_length // 2

# Draws the item on the screen.
# This is like painting our item onto the game. 
# If we want to see our item, this method takes care of showing it to us.
    def render(self):
        if self.display:
            c.screen.blit(i.images[self.item], (self.x - c.player_x - c.cell_length // 2, self.y - c.player_y - c.cell_length // 2))

    def render_tooltip(self):
        ui.render_desc(self.item_name)

# Creates a new manager to keep track of all the items.
# This is like having a librarian who knows where every book (in this case, item) is in the library.
class ItemManager:
    def __init__(self):
        self.grid = []
        for _ in range(c.num_cells):
            new_row = [0 for _ in range(c.num_cells)]
            self.grid.append(new_row)
        self.items = []
# Moves items along conveyors or through splitters
# Our librarian also helps make sure that items get to where they need to go on conveyors or through splitters, 
# kind of like sorting books into the right sections.
    def update(self, sm):
        for item in self.items:
            old_row, old_col = item.row, item.col

            if not item.caught and type(sm.grid[old_row][old_col]) in [Conveyor, ConveyorUnderground, Splitter]:
                conveyor_direction = sm.grid[old_row][old_col].direction
                can_move_ahead = True

                if type(sm.grid[old_row][old_col]) in [ConveyorUnderground, Splitter]:
                    conveyor_ug = sm.grid[old_row][old_col]
                    if not conveyor_ug.can_accept_item(old_row, old_col):
                        can_move_ahead = False

                if can_move_ahead:
                    if conveyor_direction == 0 and self.grid[old_row - 1][old_col] == 0 and sm.item_can_be_placed(old_row - 1, old_col):
                        item.move("up")
                    elif conveyor_direction == 1 and self.grid[old_row][old_col + 1] == 0 and sm.item_can_be_placed(old_row, old_col + 1):
                        item.move("right")
                    elif conveyor_direction == 2 and self.grid[old_row + 1][old_col] == 0 and sm.item_can_be_placed(old_row + 1, old_col):
                        item.move("down")
                    elif conveyor_direction == 3 and self.grid[old_row][old_col - 1] == 0 and sm.item_can_be_placed(old_row, old_col - 1):
                        item.move("left")

                new_row, new_col = item.row, item.col
                if old_row != new_row or old_col != new_col:
                    self.grid[old_row][old_col] = 0
                    self.grid[new_row][new_col] = item

# Tells each item to draw itself.
# This is like the librarian asking every book to show its cover.
    def render(self):
        for item in self.items:
            item.render()

#Places a new item in the game world.
#If we get a new book, this is how we tell our librarian where to put it.
    def add(self, row, col, item):
        new_item = Item(row, col, item)
        self.grid[row][col] = new_item
        self.items.append(new_item)

# Removes an item from the game world.
# If we need to take a book out of the library, this is how we do it.
    def remove(self, row, col, by_player = False):
        if self.grid[row][col] != 0:
            item = self.grid[row][col]
            self.grid[row][col] = 0

            try:
                self.items.remove(item)
            except ValueError:
                pass

            if by_player:
                c.item_pick_up.play()
# Various utilities for handling items like picking them up, checking
# if an item is a certain type, adjusting for zoom, and cleaning up lost items.
# These are all special tools our librarian has. For example, fetching a book, 
# checking if it's a storybook or an encyclopedia, adjusting the shelf heights, and making sure no books are left out where they shouldn't be.
    def fetch_item(self, row, col):
        if self.grid[row][col] != 0:
            item_to_be_fetched = self.grid[row][col]
            self.grid[row][col] = 0
            return item_to_be_fetched
        
    def drop_item(self, item, x, y):
        row = int(y / c.cell_length)
        col = int(x / c.cell_length)
        self.grid[row][col] = item
        
        item.row = row
        item.col = col

    def contains_ore(self, row, col):
        if self.grid[row][col] != 0 and self.grid[row][col].item in [id_map["iron_ore"], id_map["copper_ore"]]:
            return True
        else:
            return False
        
    def apply_zoom(self):
        for item in self.items:
            item.calc_position()

    def garbage_collection(self):
        for item in self.items:
            if not item.caught and self.grid[item.row][item.col] == 0:
                self.items.remove(item)

item_manager = ItemManager()