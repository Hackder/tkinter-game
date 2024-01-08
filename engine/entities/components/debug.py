from engine.logger import logger
from engine.entities.components.base import Component
from engine.entities.basic import Entity
from engine.models import FrameContext, Position, Size, Color
from typing import Any
from timeit import default_timer as timer


class FpsCounter(Component):
    def __init__(self, period: int = 10):
        self.period = period
        self.frames_passed = 0
        self.text = "Calculating..."

    def create(self, entity):
        self.start_time = timer()

    def before_layout(self, entity: Entity, ctx: FrameContext, state: Any | None):
        self.frames_passed += 1
        if self.frames_passed >= self.period:
            self.frames_passed = 0
            now = timer()
            self.text = f"{self.period / (now - self.start_time):.2f} fps"
            self.start_time = now

        if state is None or not hasattr(state, "text"):
            raise Exception(
                "FpsCounter component must be on an entity which supports text"
            )

        state.text = self.text


class FpsFlicker(Component):
    def __init__(self, a: Color = Color.white(), b: Color = Color.black()):
        self.a = a
        self.b = b
        self.color = a

    def before_paint(
        self,
        entity: Entity,
        ctx: FrameContext,
        position: Position,
        size: Size,
        state: Any | None,
    ):
        if not hasattr(state, "fill") or not state:
            raise Exception(
                "FpsFlicker component must be on an entity which supports fill"
            )

        state.fill = self.color


class DebugBounds(Component):
    def __init__(self, *, color: Color = Color.red()):
        self.color = color

    def create(self, entity):
        self.id = entity.canvas.create_rectangle(
            0, 0, 0, 0, outline=self.color.to_hex(), width=1
        )
        self.text_id = entity.canvas.create_text(
            0, 0, text="", fill=self.color.to_hex(), anchor="sw", font=("Arial", 10)
        )

    def destroy(self, entity: Entity):
        entity.canvas.delete(self.id)
        entity.canvas.delete(self.text_id)

    def before_paint(
        self,
        entity: Entity,
        ctx: FrameContext,
        position: Position,
        size: Size,
        state: Any | None,
    ):
        entity.canvas.tag_raise(self.id)
        entity.canvas.tag_raise(self.text_id)
        entity.canvas.coords(
            self.id,
            position.x - 1,
            position.y - 1,
            position.x + size.width + 2,
            position.y + size.height + 2,
        )
        entity.canvas.itemconfig(self.id, outline=self.color.to_hex())
        entity.canvas.coords(self.text_id, position.x, position.y)
        entity.canvas.itemconfig(
            self.text_id,
            text=f"{entity.__class__.__name__} (tag={entity.tag}) {size.width:.2f}x{size.height:.2f}",
            fill=self.color.to_hex(),
        )


class AssetLoaderStats(Component):
    def before_layout(self, entity: Entity, ctx: FrameContext, state: Any | None):
        if state is None or not hasattr(state, "text"):
            raise Exception(
                "AssetLoaderStats component must be on an entity which supports text"
            )

        state.text = (
            f"Assets: {ctx.asset_manager.loaded()} / {ctx.asset_manager.total()}"
        )


class PrintLifecycle(Component):
    def __init__(
        self,
        *,
        tag: str = "dbg",
        create: bool = False,
        destroy: bool = False,
        before_layout: bool = False,
        before_paint: bool = False,
    ):
        self.tag = tag
        self.log_create = create
        self.log_destroy = destroy
        self.log_before_layout = before_layout
        self.log_before_paint = before_paint
        self.log = logger.getChild(f"PrintLifecycle({tag})")

    def create(self, entity: Entity):
        if not self.log_create:
            return

        self.log.debug("Create: %s", entity)

    def destroy(self, entity: Entity):
        if not self.log_destroy:
            return

        self.log.debug("Destroy: %s", entity)

    def before_layout(self, entity: Entity, ctx: FrameContext, state: Any | None):
        if not self.log_before_layout:
            return

        self.log.debug("Before layout: %s, %s, %s", entity, ctx, state)

    def before_paint(
        self,
        entity: Entity,
        ctx: FrameContext,
        position: Position,
        size: Size,
        state: Any | None,
    ):
        if not self.log_before_paint:
            return

        self.log.debug(
            "Before paint: %s, %s, %s, %s, %s", entity, ctx, position, size, state
        )
