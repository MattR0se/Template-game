import pygame as pg
import inspect
import os
import json

import states
import settings as st
from load_assets import Loader
import controls
import utilities


# TODO:
# - save system
# - sound loader



class Game():
    def __init__(self):
        pg.init()
        self.clock = pg.time.Clock()
        self.actual_screen = pg.display.set_mode((st.WINDOW_W, st.WINDOW_H))
        self.screen = pg.Surface((st.SCREEN_W, st.SCREEN_H))
        self.screen_rect = self.screen.get_rect()
        self.display_rect = self.actual_screen.get_rect()
        self.fps = st.FPS
        self.all_sprites = pg.sprite.Group()
        
        self.fonts = {
                'default': pg.font.SysFont(st.DEFAULT_FONT, 18)
                }
        
        self.base_dir = os.path.join(os.path.dirname( __file__ ), '..')
        
        self.map_files = ['sample_map.tmx']
        self.map_files = [os.path.join(self.base_dir, 'data', 'tilemaps', m) 
                          for m in self.map_files]
        self.save_dir = os.path.join(self.base_dir, 'data', 'saves')
        
        self.asset_loader = Loader(self)
        self.graphics = self.asset_loader.load_graphics()
        self.asset_loader.load_sounds()
        
        self.gamepad_controller = controls.GamepadController()
        self.key_getter = controls.KeyGetter(self)
        
        
        self.setup_states()
    
    
    def setup_states(self):
        # get a dictionary with all classes from the 'states' module
        self.state_dict = dict(inspect.getmembers(states, inspect.isclass))
        # define the state at the start of the program
        self.state_name = 'Title_screen'
        self.state = self.state_dict[self.state_name](self)
    
    
    def flip_state(self):
        '''set the state to the next if the current state is done'''
        self.state.done = False
        # set the current and next state to the previous and current state
        previous, self.state_name = self.state_name, self.state.next
        self.state.cleanup()
        if self.state_name == None:
            self.running = False
        else:
            self.state = self.state_dict[self.state_name](self)
            self.state.startup()
            self.state.previous = previous
        
    
    def save(self, filename):
        '''default save function. Saves all sprites' attributes
        Args:
            filename: 'example.json'
        '''
        save_data = {}
        for sprite in self.all_sprites.sprites():
            # check if attribute is serializable
            keys_ok = []
            for key, value in sprite.__dict__.items():
                if utilities.is_jsonable(value):
                    keys_ok.append(key)
            save_data['all_sprites'] = {key: sprite.__dict__[key] for key in keys_ok}
            
        with open(os.path.join(self.save_dir, filename), 'w') as f:
            json.dump(save_data, f)


    def events(self):
        '''empty the event queue and pass the events to the states'''
        self.events_list = pg.event.get()
        for event in self.events_list:
            if event.type == pg.QUIT:
                self.running = False
            self.state.get_event(event)


    def update(self, dt):
        # get input before state updates
        self.gamepad_controller.update()
        self.key_getter.get_input(self.gamepad_controller, self.events_list)

        if self.state.done:
            self.flip_state()
        self.state.update(dt)


    def draw(self):
        # reset drawing surface
        #self.screen = pg.Surface((st.SCREEN_W, st.SCREEN_H))
        self.state.draw(self.screen)
        # transform the drawing surface to the window size
        transformed_screen = pg.transform.scale(self.screen,(st.WINDOW_W, 
                                                      st.WINDOW_H))
        # blit the drawing surface to the application window
        self.actual_screen.blit(transformed_screen, (0, 0))
        pg.display.update()


    def run(self):
        self.running = True
        while self.running:
            delta_time = self.clock.tick(self.fps) / 1000 # "dt"
            self.events()
            self.update(delta_time)
            self.draw()

        pg.quit()