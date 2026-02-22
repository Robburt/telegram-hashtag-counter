import tkinter as tk
from tkinter import ttk, filedialog

class Menubar(tk.Menu):
    def __init__(self, parent, *args, **kwargs):
        tk.Menu.__init__(self, parent, *args, **kwargs)

        self.add_command(label='Options')
        self.add_command(label='Open')
        self.add_command(label='New', command=self.create_new_profile)

    def create_new_profile(self):
        self.np = NewProfileMenu()

class NewProfileMenu(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)

        self.name = tk.StringVar()
        self.name_frame = tk.Frame(self)
        self.name_label = tk.Label(self.name_frame, text="Profile name: ", font=("Arial", 10))
        self.name_entry = tk.Entry(self.name_frame, textvariable=self.name)
        self.name_label.grid(row=0, column=0)
        self.name_entry.grid(row=0, column=1)

        self.results_dir = tk.StringVar()
        self.dir_frame = tk.Frame(self)
        self.dir_label = tk.Label(self.dir_frame, text="Results directory: ", font=("Arial", 10))
        self.dir_button = tk.Button(self.dir_frame, text="Open...", command=self.open_results_file)
        self.dir_label.grid(row=0, column=0)
        self.dir_button.grid(row=0, column=1)

        self.create_button = tk.Button(self, text='Create new profile', command=self.end)

        self.name_frame.pack(anchor='w', padx=40, pady=20)
        self.dir_frame.pack(anchor='w', padx=40, pady=20)
        self.create_button.pack(anchor='w', padx=40, pady=10)

    def open_results_file(self):
        results_dir = filedialog.askopenfile(filetypes=[('JSON', '.json')])
        if results_dir is not None:
            self.results_dir.set(results_dir.name)

    def end(self):
        self.destroy()

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

        self.query_string = tk.StringVar()
        self.searchbar = tk.Entry(self, textvariable=self.query_string)
        self.searchbar.grid(row=0, column=0, sticky=tk.E, padx=10)

    def bind_command(self, command):
        self.query_string.trace('w', command)

    @property
    def query(self):
        return self.query_string.get()

    def set_query(self, query):
        self.query_string.set(query)

class FlavouredTreeView(ttk.Treeview):
    def __init__(self, parent, *args, **kwargs):
        ttk.Treeview.__init__(self, parent, *args, **kwargs)

    def insert_tag(self, tag):
        return self.insert('', 'end', text=tag.name, values=tag.uses_amount)

    def clear(self):
        self.delete(*self.get_children())

    def reset_selection(self):
        self.selection_set(self.get_children()[0])