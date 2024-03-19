from os.path import join

import pygameextra as pe
from client import Client
from hook_manager import HookManager

pe.init()


class GameContext(pe.GameContext):
    AREA = (500, 500)
    FPS = 60

    def __init__(self):
        # Initialize other things first
        super().__init__()

        self.client = Client()
        self.client.thread_receive()
        self.hooks = HookManager()

        # Load the base mod
        self.hooks.load_mod(join('mods', 'base'))
        self.hooks.register_mod_hooks('com.redttg.p2p_base')

        # Initialize the game
        self.screen = 'loading_screen'
        self.screen_map = {
            'loading_screen': self.hooks.loading_screen
        }

    def handle_event(self, e: pe.pygame.event.Event):
        if pe.event.quitCheck():
            self.client.receiving = False
            self.client.socket.close()
            pe.Pquit()

    def loop(self):
        try:
            self.screen_map[self.screen]()
        except KeyError:
            raise NotImplementedError(f"Screen {self.screen} not implemented")


game_context = GameContext()

while True:
    game_context()
