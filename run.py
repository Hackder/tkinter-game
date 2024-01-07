import sys


if sys.version_info < (3, 11):
    print("Please use Python 3.11 or above")
    sys.exit(1)

import os
from PIL.Image import Resampling
from engine.renderer import Renderer
from engine.assets import Asset, AssetManager, AssetType, TiledAnimation
from game.theme_colors import ThemeColors


def register_character(mgr: AssetManager, i: int):
    mgr.register(
        f"character{i}-walk",
        Asset(
            AssetType.AnimatedTileset,
            f"characters/{i}/Walk.png",
            Resampling.NEAREST,
            TiledAnimation(48, 48, 5),
        ),
    )
    mgr.register(
        f"character{i}-idle",
        Asset(
            AssetType.AnimatedTileset,
            f"characters/{i}/Idle.png",
            Resampling.NEAREST,
            TiledAnimation(48, 48, 5),
        ),
    )


if __name__ == "__main__":
    asset_folder = os.path.join(os.path.dirname(__file__), "game/assets")
    renderer = Renderer(800, 600, asset_folder, ThemeColors.bg())

    from game.game import scene

    renderer.assign_scene(scene)

    renderer.asset_manager.register(
        "small", Asset(AssetType.Still, "small.png", Resampling.NEAREST)
    )
    for i in [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12]:
        register_character(renderer.asset_manager, i)
    renderer.asset_manager.start()

    renderer.start()
