from timeit import default_timer as timer
from tkinter import Tk, Canvas

from engine.entities.basic import RootScene
from engine.models import Color, FrameContext
from engine.assets import AssetManager
from game.theme_colors import ThemeColors
from engine.logger import logger


class Renderer:
    def __init__(
        self,
        window_width: float,
        window_height: float,
        asset_folder: str,
        bg: Color = ThemeColors.fg(),
    ):
        self.log = logger.getChild("Renderer")
        self.scene: RootScene | None = None
        self.root = Tk()
        self.root.geometry(f"{window_width}x{window_height}")
        self.canvas = Canvas(self.root, highlightthickness=0, background=bg.to_hex())
        self.canvas.pack(fill="both", expand=True)
        self.last_frame = timer()
        self.asset_manager = AssetManager(asset_folder)

        self.engine_time = 0
        self.frames = 0
        self.last_metrics = timer()

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
        if delta_time > 1 / 3:
            delta_time = 0
        self.last_frame = now

        ctx = FrameContext(
            delta_time=delta_time,
            width=self.canvas.winfo_width(),
            height=self.canvas.winfo_height(),
            asset_manager=self.asset_manager,
        )
        self.scene.layout(ctx)
        self.scene.paint(ctx)

        new_now = timer()
        self.engine_time += new_now - now
        self.frames += 1

        if new_now - self.last_metrics > 1:
            self.log.info(
                f"Frames renderred: {self.frames}, Engine time: {self.engine_time * 1000}ms, Engine frame time: {self.engine_time * 1000 / self.frames}ms"
            )
            self.frames = 0
            self.engine_time = 0
            self.last_metrics = new_now

        self.root.after(8, self.frame)

    def start(self):
        self.last_frame = timer()

        def on_visible(e):
            self.root.after_idle(self.frame)

        self.root.bind("<Visibility>", on_visible)
        self.root.mainloop()
