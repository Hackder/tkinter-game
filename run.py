import sys

from cli import CliOptions
from game.state import State


if sys.version_info < (3, 12):
    print("Please use Python 3.12 or above")
    sys.exit(1)

import os
import gc
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


if __name__ == "__main__":
    options = CliOptions(sys.argv)
    logging.basicConfig(level=options.global_log_level)
    logging.getLogger("Engine").setLevel(options.engine_log_level)
    logging.getLogger("Game").setLevel(options.log_level)
    State.metrics = options.metrics
    if options.metrics:
        gc.set_debug(gc.DEBUG_STATS)

    asset_folder = os.path.join(os.path.dirname(__file__), "game/assets")
    renderer = Renderer(
        options.width, options.height, asset_folder, ThemeColors.bg(), options.metrics
    )

    from game.game import scene

    renderer.assign_scene(scene)

    renderer.asset_manager.register(
        "small", Asset(AssetType.Still, "small.png", Resampling.NEAREST)
    )
    for i, idx in enumerate([1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12]):
        register_character(renderer.asset_manager, idx, i + 1)

    renderer.asset_manager.start()

    renderer.start()
