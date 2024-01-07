from engine.models import Color


class ThemeColors:
    @staticmethod
    def fg() -> Color:
        return Color.from_hex("#DFF8EB")

    @staticmethod
    def fg_inverse() -> Color:
        return Color.black()

    @staticmethod
    def fg_muted() -> Color:
        return Color.from_hex("#5B4276")

    @staticmethod
    def muted() -> Color:
        return Color.from_hex("#DFD8E9")

    @staticmethod
    def bg() -> Color:
        return Color.from_hex("#1A1423")

    @staticmethod
    def bg_secondary() -> Color:
        return Color.from_hex("#312541")

    @staticmethod
    def primary() -> Color:
        return Color.from_hex("#45335A")
