import sys

if sys.version_info < (3, 11):
    print("Please use Python 3.11 or above")
    sys.exit(1)

import os
from PIL.Image import Resampling
from engine.renderer import Renderer
from engine.models import Color
from engine.assets import Asset, AssetType

renderer = Renderer(800, 600, "assets", Color.from_hex("#1A1423"))

from game.game import scene
renderer.assign_scene(scene)

asset_folder = os.path.join(os.path.dirname(__file__), "assets")
renderer.asset_manager.register(
    "small", Asset(AssetType.Still, "small.png", Resampling.NEAREST)
)
renderer.asset_manager.start()

renderer.start()
