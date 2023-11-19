from tkinter import Tk, Canvas
from timeit import default_timer as timer
from enum import StrEnum
import json
import copy

import engine.renderer

print(engine)

w_width = 800
w_height = 600

tk = Tk()
tk.geometry(f'{w_width}x{w_height}')
tk.configure(bg='#ff0000')
canvas = Canvas(tk, highlightthickness=0, bg='white')
canvas.pack(expand=True, fill='both')


tk.mainloop()
