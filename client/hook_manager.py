import inspect
import os.path
import json
import pygameextra as pe
from lupa.lua54 import LuaRuntime, unpacks_lua_table


class MalformedModError(Exception):
    pass


class Mod:
    package: str
    name: str
    author: str
    description: str
    mod_version: str

    def __init__(self, directory: str, version: int):
        self.directory = directory
        self.version = version
        try:
            self.load()
        except FileNotFoundError as e:
            raise MalformedModError(f"Mod at {directory} is missing {e.filename}")

    def load(self):
        with open(os.path.join(self.directory, 'mod.json'), 'r') as f:
            self.mod_info = json.load(f)
        if (mod_version := self.mod_info.get('version')) != self.version:
            if mod_version is None:
                raise MalformedModError(f"Mod at {self.directory} is missing a version key")
            elif mod_version < self.version:
                raise MalformedModError(f"Mod at {self.directory} is outdated")
            else:
                raise MalformedModError(f"Your game is outdated for mod at {self.directory}")
        if (mod_package := self.mod_info.get('package')) is None:
            raise MalformedModError(f"Mod at {self.directory} is missing a package key")
        else:
            self.package = mod_package
        self.name = self.mod_info.get('name', self.package)
        self.author = self.mod_info.get('author', '<tr>no_author</tr>')
        self.description = self.mod_info.get('description', '<tr>no_description</tr>')
        self.mod_version = self.mod_info.get('mod_version', '-')

    @property
    def hooks_dir(self):
        return os.path.join(self.directory, 'hooks')


class Hook:
    def __init__(self, hook_name: str, hook_code: str, lua: LuaRuntime):
        self.function = lua.eval(hook_code)

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)


class LuaGenerator:
    def __init__(self, generator):
        self.generator = generator

    def __call__(self, *args):
        try:
            return next(self.generator)
        except StopIteration:
            return None


class HookManager:
    SUPPORT_VERSION = 0
    GLOBAL_LUA = """LOADING_SCREEN_BG = {255, 255, 255}"""

    def __init__(self):
        self.hooks = {}
        self.mods = {}
        self.game_context: pe.GameContext = pe.settings.game_context

        # Setup lua context
        self.lua = LuaRuntime()
        self.lua.execute(self.GLOBAL_LUA)
        self.load_global_hooks()

        for hook_name, hook_function in self.hooks.items():
            self.lua.globals()[hook_name] = hook_function

    def register(self, hook_name, hook_code, special: str = None):
        if special is None:
            self.hooks[hook_name] = Hook(hook_name, hook_code, self.lua)
        elif hook_name == f'__{special}__':
            if False:
                pass
            else:
                self.lua.execute(hook_code)

    def register_mod_hooks(self, package: str, special: str = None):
        mod = self.mods[package]
        self.register_hooks_folder(mod.hooks_dir, special)

    def register_hooks_folder(self, folder: str, special: str = None):
        for hook in os.listdir(folder):
            item = os.path.join(folder, hook)
            if special is None and hook.endswith('__.lua'):
                continue
            if os.path.isfile(item):
                with open(item, 'r') as f:
                    self.register(hook.rsplit('.', 1)[0], f.read(), special)
            elif os.path.isdir(item):
                self.register_hooks_folder(item, special)

    def load_mod(self, mod: str):
        if os.path.isdir(mod):
            mod = Mod(mod, self.SUPPORT_VERSION)
            if mod.package in self.mods:
                return
            self.mods[mod.package] = mod
            self.register_mod_hooks(mod.package, 'pre_initialize')
            print(f"Loaded mod {mod.name} by {mod.author} ({mod.package})")

    def __getattr__(self, item):
        if item in self.hooks:
            return self.hooks[item]
        else:
            return super().__getattribute__(item)

    def lua_wrap(self, function):
        return unpacks_lua_table(function)

    def load_global_hooks(self):
        self.hooks['fill_screen'] = lambda r, g, b: pe.fill.full((r, g, b))

        for hook_name, hook_function in self.hooks.items():
            self.hooks[hook_name] = self.lua_wrap(hook_function)

        self.hooks['load_mod'] = self.load_mod
        self.hooks['print'] = print

        self.hooks['get_all_mods'] = lambda: LuaGenerator(
            (os.path.join('mods', mod) for mod in os.listdir('mods')))
        self.hooks['get_current_screen'] = lambda: self.game_context.screen
        self.hooks['set_screen'] = lambda screen: setattr(self.game_context, 'screen', screen)
