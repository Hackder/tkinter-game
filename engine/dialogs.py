from tkinter import Tk, filedialog
from typing import Callable


class Dialogs:
    @staticmethod
    def open_file_dialog(cb: Callable):
        root = Tk()
        root.withdraw()
        filename = ""
        try:
            filename = filedialog.askopenfilename()
        finally:
            cb(filename)
