import tkinter as tk

class Menubar(tk.Menu):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(self, parent, *args, **kwargs)

        menu_options = tk.Menu(self)
        menu_open = tk.Menu(self)
        menu_new = tk.Menu(self)
        self.add_cascade(menu=menu_options, label='Options')
        self.add_cascade(menu=menu_open, label='Open')
        self.add_cascade(menu=menu_new, label='New')