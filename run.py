import sys


if sys.version_info < (3, 11):
    print("Please use Python 3.11 or above")
    sys.exit(1)

import os
from PIL.Image import Resampling
from engine.renderer import Renderer
from engine.assets import Asset, AssetType
from game.theme_colors import ThemeColors

if __name__ == "__main__":
    renderer = Renderer(800, 600, "assets", ThemeColors.background())

    from game.game import scene

    renderer.assign_scene(scene)

    asset_folder = os.path.join(os.path.dirname(__file__), "assets")
    renderer.asset_manager.register(
        "small", Asset(AssetType.Still, "small.png", Resampling.NEAREST)
    )
    renderer.asset_manager.register(
        "character01",
        Asset(AssetType.AnimatedTileset, "characters/1/Walk.png", Resampling.NEAREST),
    )
    renderer.asset_manager.start()

    renderer.start()
