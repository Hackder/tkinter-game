import sys


if sys.version_info < (3, 12):
    print("Please use Python 3.12 or above")
    sys.exit(1)

import os
import logging
from PIL.Image import Resampling
from engine.renderer import Renderer
from engine.assets import Asset, AssetManager, AssetType, TiledAnimation
from game.theme_colors import ThemeColors


def register_character(mgr: AssetManager, idx: int, i: int):
    mgr.register(
        f"character{i}-walk",
        Asset(
            AssetType.AnimatedTileset,
            f"characters/{idx}/Walk.png",
            Resampling.NEAREST,
            TiledAnimation(48, 48, 5),
        ),
        [(200, 200)],
    )
    mgr.register(
        f"character{i}-idle",
        Asset(
            AssetType.AnimatedTileset,
            f"characters/{idx}/Idle.png",
            Resampling.NEAREST,
            TiledAnimation(48, 48, 5),
        ),
        [(200, 200)],
    )


class CliOptions:
    def _set_log_level(self, value: str):
        if value not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise Exception(f"Unknown log level: {value}")
        self.log_level = value

    def __init__(self, args: list[str]):
        self.log_level = "WARNING"
        self.width = 800
        self.height = 600

        methods = dir(self)

        for arg in args[1:]:
            if arg == "--help" or arg == "-h":
                self._print_help()
                sys.exit(0)

            for name, value in vars(self).items():
                arg_name = f"{self._cli_arg_name(name)}="
                if arg.startswith(arg_name):
                    provided_value = arg[len(arg_name) :]
                    if f"_set_{name}" in methods:
                        getattr(self, f"_set_{name}")(provided_value)
                    else:
                        t = type(value)
                        setattr(self, name, t(provided_value))
                    break
            else:
                print(f"Unknown argument: {arg}")
                self._print_help()
                sys.exit(1)

    def _cli_arg_name(self, name: str) -> str:
        return f"--{name.replace('_', '-')}"

    def _print_help(self):
        print("Usage: python run.py [options]")
        print("Options:")
        methods = dir(self)
        for name, value in vars(self).items():
            if f"_get_{name}" in methods:
                value = getattr(self, f"_get_{name}")()
            print(f"  {self._cli_arg_name(name)}={value}")


if __name__ == "__main__":
    options = CliOptions(sys.argv)
    logging.basicConfig(level=options.log_level)

    asset_folder = os.path.join(os.path.dirname(__file__), "game/assets")
    renderer = Renderer(options.width, options.height, asset_folder, ThemeColors.bg())

    from game.game import scene

    renderer.assign_scene(scene)

    renderer.asset_manager.register(
        "small", Asset(AssetType.Still, "small.png", Resampling.NEAREST)
    )
    for i, idx in enumerate([1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12]):
        register_character(renderer.asset_manager, idx, i + 1)

    renderer.asset_manager.start()

    renderer.start()
