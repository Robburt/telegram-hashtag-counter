import tkinter as tk
from tkinter import ttk

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

class SearchBar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.displaying_full_table = True
        self.searchbar = tk.Entry(self)
        self.button = tk.Button(self, text="Search", width=10)
        self.searchbar.grid(row=0, column=0, sticky=tk.E, padx=10)
        self.button.grid(row=0, column=1, sticky=tk.E)

    def bind_command(self, command):
        self.button.configure(command=command)

    @property
    def query(self):
        return self.searchbar.get()

    def resolve_displaying_full_table(self):
        self.displaying_full_table = self.query == ''

    def set_query(self, query):
        self.searchbar.delete(0, tk.END)
        self.searchbar.insert(0, query)

class FlavouredTreeView(ttk.Treeview):
    def __init__(self, parent, *args, **kwargs):
        ttk.Treeview.__init__(self, parent, *args, **kwargs)

    def insert_tag(self, tag):
        return self.insert('', 'end', text=tag.name, values=tag.uses_amount)

    def clear(self):
        self.delete(*self.get_children())

    def reset_selection(self):
        self.selection_set(self.get_children()[0])