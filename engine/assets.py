from dataclasses import dataclass
from enum import StrEnum
from PIL import Image, ImageTk

class AssetType(StrEnum):
    Still = 'still'

@dataclass(frozen=True)
class Asset:
    type: AssetType
    path: str
    resampling: Image.Resampling | None = None


class AssetManader:
    def __init__(self):
        self.raw_assets: dict[str, Asset] = dict()
        self.assets: dict[tuple[str, int, int], ImageTk.PhotoImage] = dict()
        self.queue = list()
        self.loaded = 0

    def register(self, key: str, asset: Asset):
        self.raw_assets[key] = asset

    def __load_still(self, key: str, asset: Asset, width: float, height: float):
        width = int(width)
        height = int(height)
        image = Image.open(asset.path)
        image = image.resize((width, height), resample=asset.resampling)
        tk_image =  ImageTk.PhotoImage(image, width=width, height=height)
        self.assets[(key, width, height)] = tk_image
        self.loaded += 1
        return tk_image

    def get(self, key: str, width: float, height: float) -> ImageTk.PhotoImage | None:
        width = int(width)
        height = int(height)
        if (key, width, height) in self.assets:
            return self.assets[(key, width, height)]

        asset = self.raw_assets.get(key, None)
        if asset is None:
            return None

        if asset.type == AssetType.Still:
            return self.__load_still(key, asset, width, height)



