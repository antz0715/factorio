

from time import time
import pygame as pg


# Import various modules and variables from other scripts in the same folder.
# These imports create a structured game project with separate concerns like
# constants, image handling, item management, music playback, structures, UI,
# utility functions, and world handling.

# The game loop runs continuously during the game, performing key actions
# such as processing inputs (keyboard and mouse), updating game objects, 
#and rendering graphics to the screen. It keeps the game moving and responsive to player actions.


from constants import consts as c
from id_mapping import id_map
from images import img as i
from items import item_manager as im
from music_player import music_player as mp
from structures.structure import structure_manager as sm
from ui.game_ui import ui
from utils import *
from world import world as w


def game_loop():
    title = c.orbitron.render("PyFactory", True, pg.Color("white"))
    # starting with rendering the game's title using a font defined in constants.py 
    # (c.orbitron). This is just setting up the text that says "PyFactory".

    while True:
        # loop, the game continuously updates
        start = time()
        c.clock.tick(c.fps) # It records the start time for each frame to control the game's speed (fps)

        keys_pressed = pg.key.get_pressed()
        move_player(keys_pressed)
        cell_row, cell_col, cell_x, cell_y = get_pointer_params()

#  The game checks what keys the player is pressing and whether the mouse is clicked 
# to move the player or interact with the game world. 
# For example, placing or removing conveyors.
        if c.const_state == 1:
            left, _, right = pg.mouse.get_pressed()
            if left:
                sm.add(cell_row, cell_col, id_map["conveyor"], c.rot_state)
            if right:
                sm.remove(cell_row, cell_col)
# The game checks what keys the player is pressing and whether the mouse is clicked to move the player
# or interact with the game world. For example, placing or removing conveyors.
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
# Based on player actions (like keyboard presses and mouse clicks), the game updates various elements,
# such as toggling gridlines, rotating structures, and more.     
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return
                if pg.K_0 < event.key < pg.K_8:
                    c.const_state = event.key - pg.K_0
                    ui.update_selection
                if event.key == pg.K_g:
                    c.toggle_gridlines()
                if event.key == pg.K_r or event.key == pg.K_l:
                    rotation = 1 if event.key == pg.K_r else -1
                    if sm.grid[cell_row][cell_col] != 0:
                        sm.rotate(cell_row, cell_col, rotation)
                    else:
                        c.cycle_rot_state(rotation)
                if event.key == pg.K_LSHIFT or event.key == pg.K_RSHIFT:
                    c.cycle_ug_state(1)
                if event.key == pg.K_LCTRL or event.key == pg.K_RCTRL:
                    c.cycle_ug_state(-1)
                if event.key == pg.K_m or event.key == pg.K_n:
                    if event.key == pg.K_m:
                        c.cell_length += 5
                    else:
                        c.cell_length -= 5

                    i.reload_images()
                    sm.apply_zoom()
                    im.apply_zoom()

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    sm.add(cell_row, cell_col, c.const_state - 1, c.rot_state)
                if event.button == 3:
                    if im.grid[cell_row][cell_col] != 0:
                        im.remove(cell_row, cell_col, True)
                    elif sm.grid[cell_row][cell_col] != 0:
                        sm.remove(cell_row, cell_col)

            if event.type == pg.MOUSEWHEEL:
                if event.y > 0:
                    c.cell_length += 2
                elif event.y < 0:
                    c.cell_length -= 2

                i.reload_images()
                sm.apply_zoom()
                im.apply_zoom()

        c.screen.fill(c.bg_color)
        if c.show_gridlines:
            draw_gridlines()

        sm.update()
        im.update(sm)
        mp.check_next_music()
# The game draws everything on the screen, 
# including the background, gridlines (if enabled), structures, items,
# and UI elements like tooltips.
        w.render()
        sm.render()
        im.render()
        ui.render()

        if sm.grid[cell_row][cell_col] == 0:
            draw_action(cell_x, cell_y)
        else:
            sm.grid[cell_row][cell_col].render_tooltip()

        if im.grid[cell_row][cell_col] != 0:
            im.grid[cell_row][cell_col].render_tooltip()

        if w.grid[cell_row][cell_col] != 0:
            w.render_tooltip(cell_row, cell_col)

        pg.draw.rect(c.screen, pg.Color("black"), (0, 0, c.sw, c.title_font_size * 2))
        c.screen.blit(title, ((c.sw - title.get_width()) / 2, c.title_font_size / 2))

        fps_text = c.merriweather.render(f"FPS: {round(c.clock.get_fps())}", True, pg.Color("white"))
        c.screen.blit(fps_text, (c.sw - fps_text.get_width() - 10, 10))

        pg.display.flip()

        end = time()
        c.set_dt(end - start)


if __name__ == '__main__':
    # this should directly lead to a game
    pg.init()
    screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    clock = pg.time.Clock()
    c.set_screen(screen)
    c.set_clock(clock)
    game_loop()