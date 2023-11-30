from engine.entities.basic import Rect, Text
from engine.entities.layout import ScreenSizeLayout, Padding, Flex, FlexDirection, Scene, WidthBox
from engine.models import Color, EdgeInset
from engine.entities.components.debug import FpsCounter, AssetLoaderStats


metrics = ScreenSizeLayout(
            child=Padding(
                padding=EdgeInset.all(20),
                child=Scene(
                    children=[
                        WidthBox(
                            width=200,
                            child=Rect(
                                fill=Color.black(),
                                outline=Color.gray(),
                                child=Padding(
                                    padding=EdgeInset.symmetric(10, 10),
                                    child=Flex(
                                        direction=FlexDirection.Column,
                                        gap=5,
                                        children=[
                                            Text(
                                                fill=Color.white(),
                                                components=[FpsCounter()],
                                                text="",
                                            ),
                                            Text(
                                                fill=Color.white(),
                                                components=[
                                                    AssetLoaderStats(),
                                                ],
                                                text="",
                                            ),
                                        ],
                                    ),
                                ),
                            ),
                        ),
                    ]
                ),
            )
        )
