from engine.entities.basic import Rect, Text
from engine.entities.layout import (
    Padding,
    Flex,
    FlexDirection,
    Scene,
    SizeBox,
)
from engine.models import Color, EdgeInset
from engine.entities.components.debug import FpsCounter, AssetLoaderStats
from game.theme_colors import ThemeColors


class Metrics:
    @staticmethod
    def build():
        return Padding(
            padding=EdgeInset.all(20),
            child=Scene(
                children=[
                    SizeBox(
                        width=200,
                        child=Rect(
                            fill=ThemeColors.fg_inverse(),
                            outline=Color.gray(),
                            child=Padding(
                                padding=EdgeInset.symmetric(10, 10),
                                child=Flex(
                                    direction=FlexDirection.Column,
                                    gap=5,
                                    children=[
                                        Text(
                                            fill=ThemeColors.fg(),
                                            components=[FpsCounter()],
                                            text=lambda: "",
                                        ),
                                        Text(
                                            fill=ThemeColors.fg(),
                                            components=[
                                                AssetLoaderStats(),
                                            ],
                                            text=lambda: "",
                                        ),
                                    ],
                                ),
                            ),
                        ),
                    ),
                ]
            ),
        )
