from timeit import default_timer as timer
from tkinter import Tk, Canvas

from engine.entities.basic import RootScene
from engine.models import FrameContext
from engine.assets import AssetManader


class Renderer:
    def __init__(
        self,
        window_width: float,
        window_height: float,
        scene: RootScene,
        asset_folder: str,
    ):
        self.root = Tk()
        self.root.geometry(f"{window_width}x{window_height}")
        self.canvas = Canvas(self.root, highlightthickness=0, background="white")
        self.canvas.pack(fill="both", expand=True)
        self.scene = scene
        self.last_frame = timer()
        self.asset_manager = AssetManader(asset_folder)
        scene.create(self.canvas)

    def frame(self):
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