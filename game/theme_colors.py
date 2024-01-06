from engine.models import Color


class ThemeColors:
    @staticmethod
    def foreground() -> Color:
        return Color.from_hex("#DFF8EB")

    @staticmethod
    def foreground_inverse() -> Color:
        return Color.black()

    @staticmethod
    def background() -> Color:
        return Color.from_hex("#1A1423")

    @staticmethod
    def background_secondary() -> Color:
        return Color.from_hex("#312541")

    @staticmethod
    def primary() -> Color:
        return Color.from_hex("#45335A")
