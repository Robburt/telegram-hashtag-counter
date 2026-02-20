import tkinter as tk

class Menubar(tk.Menu):
    def __init__(self, parent, *args, **kwargs):
        tk.Menu.__init__(self, parent, *args, **kwargs)

        menu_options = tk.Menu(self)
        menu_open = tk.Menu(self)
        menu_new = tk.Menu(self)
        self.add_cascade(menu=menu_options, label='Options')
        self.add_cascade(menu=menu_open, label='Open')
        self.add_cascade(menu=menu_new, label='New')

class SortingSwitch(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.mode = "Usages"
        self.label = tk.Label(self, text="Sorting mode: ", font=("Arial", 10))
        self.button = tk.Button(self, text=self.mode, width=20, state='disabled')
        self.label.grid(row=0, column=0, sticky=tk.E)
        self.button.grid(row=0, column=1, sticky=tk.E)

    def bind_command(self, command):
        self.button.configure(command=command)

    def button_enable(self):
        self.button.configure(state='normal')

    def switch_mode(self):
        if self.mode == "Usages":
            self.mode = "Alphabetically"
        else:
            self.mode = "Usages"
        self.button.configure(text=self.mode)