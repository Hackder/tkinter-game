import os
from dataclasses import dataclass
from enum import StrEnum
from threading import Thread
from PIL import Image, ImageTk


class AssetType(StrEnum):
    Still = "still"


@dataclass(frozen=True)
class Asset:
    type: AssetType
    path: str
    resampling: Image.Resampling | None = None


class AssetManader:
    def __init__(self, asset_folder: str):
        self.asset_folder = asset_folder
        self.raw_assets: dict[str, Asset] = dict()
        self.assets: dict[tuple[str, int, int], ImageTk.PhotoImage] = dict()
        self.queue = list()
        self.thread = Thread(target=self.__load_thread, daemon=True)
        self.loading = False

    def __load_thread(self):
        self.loading = True
        while len(self.queue) > 0:
            (key, width, height) = self.queue.pop(0)
            asset = self.raw_assets.get(key, None)
            if asset is None:
                raise Exception(f"Asset {key} not found")

            if asset.type == AssetType.Still:
                self.__load_still(key, asset, width, height)
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
        return len(self.assets)

    def total(self) -> int:
        return self.loaded() + len(self.queue)

    def __load_still(self, key: str, asset: Asset, width: int, height: int):
        image = Image.open(os.path.join(self.asset_folder, asset.path))
        image = image.resize((width, height), resample=asset.resampling)
        tk_image = ImageTk.PhotoImage(image, width=width, height=height)
        self.assets[(key, width, height)] = tk_image
        return tk_image

    def get(self, key: str, width: int, height: int) -> ImageTk.PhotoImage | None:
        cache = self.assets.get((key, width, height), None)
        if cache is not None:
            return cache

        asset = self.raw_assets.get(key, None)
        if asset is None:
            print(f"WARN: Asset {key} not found")
            return None

        if asset.type == AssetType.Still:
            return self.__load_still(key, asset, width, height)
