from timeit import default_timer as timer
from tkinter import Tk, Canvas

from engine.entities.basic import RootScene
from engine.models import Color, FrameContext
from engine.assets import AssetManader


class Renderer:
    def __init__(
        self,
        window_width: float,
        window_height: float,
        asset_folder: str,
        bg: Color = Color.white(),
    ):
        self.scene: RootScene | None = None
        self.root = Tk()
        self.root.geometry(f"{window_width}x{window_height}")
        self.canvas = Canvas(self.root, highlightthickness=0, background=bg.to_hex())
        self.canvas.pack(fill="both", expand=True)
        self.last_frame = timer()
        self.asset_manager = AssetManader(asset_folder)

    def assign_scene(self, scene: RootScene):
        if self.scene is not None:
            self.scene.destroy()
        self.scene = scene
        self.scene.create(self.canvas)

    def frame(self):
        if self.scene is None:
            raise Exception("No scene assigned")

        now = timer()
        delta_time = now - self.last_frame
        self.last_frame = now

        ctx = FrameContext(
            delta_time=delta_time,
            width=self.canvas.winfo_width(),
            height=self.canvas.winfo_height(),
            asset_manager=self.asset_manager,
        )
        self.scene.layout(ctx)
        self.scene.paint(ctx)
        self.root.after(8, self.frame)

    def start(self):
        self.last_frame = timer()

        def on_visible(e):
            self.root.after_idle(self.frame)

        self.root.bind("<Visibility>", on_visible)
        self.root.mainloop()
