import os
from engine.logger import logger
from dataclasses import dataclass
from enum import StrEnum
from threading import Thread
from PIL import Image, ImageTk


class AssetType(StrEnum):
    Still = "still"
    AnimatedTileset = "animated_tileset"


@dataclass()
class TiledAnimation:
    tile_width: int
    tile_height: int
    fps: float
    tile_count: int = -1


@dataclass()
class Asset:
    type: AssetType
    path: str
    resampling: Image.Resampling | None = None
    animation: TiledAnimation | None = None


class AssetManager:
    def __init__(self, asset_folder: str):
        self.asset_folder = asset_folder
        self.raw_assets: dict[str, Asset] = dict()
        self.assets: dict[tuple[str, int, int], ImageTk.PhotoImage] = dict()
        self.animated_assets: dict[
            tuple[str, int, int], list[ImageTk.PhotoImage]
        ] = dict()
        self.queue = list()
        self.thread = Thread(target=self.__load_thread, daemon=True)
        self.loading = False
        self.log = logger.getChild("AssetManager")

    def __load_thread(self):
        self.loading = True
        while len(self.queue) > 0:
            (key, width, height) = self.queue.pop(0)
            asset = self.raw_assets.get(key, None)
            if asset is None:
                raise Exception(f"Asset {key} not found")

            if asset.type == AssetType.Still:
                self.__load_still(key, asset, width, height)
            elif asset.type == AssetType.AnimatedTileset:
                self.__load_animated_tileset(key, asset, width, height)
        self.loading = False

    def start(self):
        if self.loading:
            return
        self.thread = Thread(target=self.__load_thread, daemon=True)
        self.thread.start()

    def register(
        self, key: str, asset: Asset, preload_sizes: list[tuple[int, int]] = []
    ):
        self.raw_assets[key] = asset
        for width, height in preload_sizes:
            self.queue.append((key, width, height))

    def loaded(self) -> int:
        return len(self.assets) + len(self.animated_assets)

    def total(self) -> int:
        return self.loaded() + len(self.queue)

    def __load_still(self, key: str, asset: Asset, width: int, height: int):
        self.log.info(
            f"Loading {key} at size ({width}, {height}) from {os.path.join(self.asset_folder, asset.path)}"
        )
        image = Image.open(os.path.join(self.asset_folder, asset.path))
        image = image.resize((width, height), resample=asset.resampling)
        tk_image = ImageTk.PhotoImage(image, width=width, height=height)
        self.assets[(key, width, height)] = tk_image

    def __load_animated_tileset(self, key: str, asset: Asset, width: int, height: int):
        animation = asset.animation
        if animation is None:
            raise Exception(f"Animation not specified for animated asset {key}")

        tile_count = animation.tile_count

        self.log.info(
            f"Loading {tile_count if tile_count > -1 else '?'} tiles for {key} at size ({width}, {height}) from {os.path.join(self.asset_folder, asset.path)}"
        )

        image = Image.open(os.path.join(self.asset_folder, asset.path))

        if tile_count == -1:
            tile_count = int(image.width / animation.tile_width)
            animation.tile_count = tile_count

        tk_images: list[ImageTk.PhotoImage] = []
        for i in range(tile_count):
            tile = image.crop(
                (
                    animation.tile_width * i,
                    0,
                    animation.tile_width * (i + 1),
                    animation.tile_height,
                )
            )
            tile = tile.resize((width, height), resample=asset.resampling)
            tk_image = ImageTk.PhotoImage(tile, width=width, height=height)
            tk_images.append(tk_image)

        self.animated_assets[(key, width, height)] = tk_images

    def get_raw(self, key: str) -> Asset | None:
        return self.raw_assets.get(key, None)

    def get(self, key: str, width: int, height: int) -> ImageTk.PhotoImage | None:
        cache = self.assets.get((key, width, height), None)
        if cache is not None:
            return cache

        asset = self.raw_assets.get(key, None)
        if asset is None:
            self.log.warn(f"Asset {key} not found")
            return None

        if asset.type == AssetType.Still:
            return self.__load_still(key, asset, width, height)

        self.log.warn(f"Asset {key} ({asset.type}) is not a still image")
        return None

    def get_animated(
        self, key: str, width: int, height: int
    ) -> list[ImageTk.PhotoImage] | None:
        cache = self.animated_assets.get((key, width, height), None)
        if cache is not None:
            return cache

        asset = self.raw_assets.get(key, None)
        if asset is None:
            self.log.warn(f"Asset {key} not found")
            return None

        if asset.type == AssetType.AnimatedTileset:
            return self.__load_animated_tileset(key, asset, width, height)

        self.log.warn(f"Asset {key} ({asset.type}) is not an animated tileset")
        return None
