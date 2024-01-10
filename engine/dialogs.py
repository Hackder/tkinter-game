from tkinter import Tk, filedialog


class Dialogs:
    @staticmethod
    def open_file_dialog():
        root = Tk()
        root.withdraw()
        filename = ""
        try:
            filename = filedialog.askopenfilename()
        finally:
            return filename

    @staticmethod
    def save_file_dialog():
        root = Tk()
        root.withdraw()
        filename = ""
        try:
            filename = filedialog.asksaveasfilename()
        finally:
            return filename
