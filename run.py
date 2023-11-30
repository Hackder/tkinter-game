import os
from PIL.Image import Resampling
from engine.renderer import Renderer
from engine.models import Color
from engine.assets import Asset, AssetType

renderer = Renderer(800, 600, "assets", Color.from_hex("#1A1423"))

from game.game import scene
renderer.assign_scene(scene)

asset_folder = os.path.join(os.path.dirname(__file__), "assets")
# game.asset_manager.register('hero', Asset(AssetType.Still, 'assets/hero.png'), [(i, 100) for i in range(100, 201)])
renderer.asset_manager.register("hero2", Asset(AssetType.Still, "hero.jpg"))
renderer.asset_manager.register(
    "small", Asset(AssetType.Still, "small.png", Resampling.NEAREST)
)
renderer.asset_manager.start()

renderer.start()
