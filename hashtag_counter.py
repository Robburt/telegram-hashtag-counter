import os
import tkinter as tk
from tkinter import filedialog, messagebox
from modules import UI, Counter

class WindowInterface:
    def __init__(self):

        self.counter = Counter.Counter()

        self.root = tk.Tk()
        self.root.title("Telegram Hashtag Counter")

        self.menubar = UI.Menubar(self.root)
        self.root.configure(menu=self.menubar)

        self.contents = tk.Frame(self.root, border=10)
        self.tag_info = tk.Frame(self.root, border=20)

        self.welcome_label = tk.Label(self.contents, text="Welcome to Telegram Hashtag Counter.\nPlease select a path to the result.json file below.", font=("Arial", 15))
        self.welcome_label.grid(row=0, columnspan=3, pady=20)

        self.results_dir = ''
        self.open_dir = tk.Button(self.contents, text="Open...", command=self.open_file_command, width=20)
        self.open_dir.grid(row=1, column=0, sticky=tk.W, padx=5)

        self.searchbar = UI.SearchBar(self.contents)
        self.searchbar.bind_command(self.search)
        self.searchbar.grid(row=1, column=2, sticky=tk.E)

        self.tag_box = UI.FlavouredTreeView(self.contents, height=20, columns="uses")
        self.tag_box.column("uses", width=30)
        self.tag_box.heading("uses", text='Usages')
        self.tag_box.grid(row=2, column=0, columnspan=3, sticky=tk.W + tk.E, pady=10)
        self.tag_box_scrollbar = tk.Scrollbar(self.contents, orient=tk.VERTICAL, command=self.tag_box.yview)
        self.tag_box.configure(yscrollcommand=self.tag_box_scrollbar.set)
        self.tag_box_scrollbar.grid(row=2, column=3, sticky=tk.N + tk.S, pady=10)
        self.tag_box.bind("<<TreeviewSelect>>", lambda e: self.on_selection_change(self.tag_box.selection()))

        self.treeview_neighbours = UI.FlavouredTreeView(self.tag_info, columns="uses", height=20)
        self.treeview_neighbours.column("uses", width=10)
        self.treeview_neighbours.heading("uses", text='Usages')
        self.treeview_neighbours_scrollbar = tk.Scrollbar(self.tag_info, orient=tk.VERTICAL, command=self.treeview_neighbours.yview)
        self.treeview_neighbours.configure(yscrollcommand=self.treeview_neighbours_scrollbar.set)
        self.neighbour_view_ids = {}

        self.popup_menu = tk.Menu(self.root, tearoff=0)
        self.popup_menu.add_command(label="Go to tag", command=self.go_to_tag)
        self.treeview_neighbours.bind("<Button-3>", self.popup)

        self.export_button = tk.Button(self.contents, text="Export to Excel", command=self.export_to_xlsx, width=20)
        self.export_button.grid(row=3, column=0, sticky=tk.W)

        self.sorting_switch = UI.SortingSwitch(self.contents)
        self.sorting_switch.bind_command(self.switch_sorting_mode)
        self.sorting_switch.grid(row=3, column=2, sticky=tk.E)

        self.contents.grid(row=0, column=0)
        self.tag_info.grid(row=0, column=1, sticky=tk.N)

        self.root.update_idletasks()
        self.root.minsize(self.root.winfo_reqwidth(), self.root.winfo_reqheight())

        try:
            with open("lastdir.txt", "r") as f:
                self.results_dir = f.read()
            self.launch_count()
        except FileNotFoundError:
            pass

        self.root.mainloop()

    def launch_count(self):
        try:
            self.counter = Counter.Counter()
            self.counter.count(self.results_dir)
        except FileNotFoundError:
            messagebox.showerror(title="File not found", message="Unable to find result.json file")
            return

        self.tag_box.clear()
        for tag in self.counter.tags_table.values():
            table_id = self.tag_box.insert_tag(tag)
            tag.table_id = table_id
        self.tag_box.reset_selection()

        self.sorting_switch.button_enable()

    def open_file_command(self):
        results_dir = filedialog.askopenfile(filetypes=[('JSON', '.json')])
        if results_dir is None:
            return
        self.results_dir = results_dir.name
        with open("lastdir.txt", "w") as f:
            f.write(results_dir.name)
        self.launch_count()

    def on_selection_change(self, selection):
        def line(text):
            tag_info_labels.append(tk.Label(self.tag_info, text=text, width=50, anchor=tk.W))
            tag_info_labels[-1].grid(row=len(tag_info_labels)-1, column=0, sticky=tk.W)

        tag = self.counter.find_by_id(selection[0])
        tag_info_labels = []
        for key, value in tag.dictionary.items():
            line(f"{key}: {value}")

        # Neighbouring tags
        line(f"Tags most commonly used with this tag:")
        self.treeview_neighbours.clear()
        self.treeview_neighbours.grid(row=len(tag_info_labels), column=0, sticky=tk.W + tk.E)
        self.treeview_neighbours_scrollbar.grid(row=len(tag_info_labels), column=1, sticky=tk.N + tk.S, pady=10)
        if not tag.has_defined_neighbours:
            tag.set_neighbours(self.counter.messages)
        self.neighbour_view_ids = {i : '' for i in tag.neighbours.keys()}
        for neighbour in tag.neighbours.values():
            neighbour_id = self.treeview_neighbours.insert_tag(neighbour)
            self.neighbour_view_ids[neighbour.name] = neighbour_id

    def search(self):
        if self.searchbar.same_query:
            return
        self.searchbar.save_query()
        self.tag_box.clear()
        for tag in self.counter.tags_table.values():
            if self.searchbar.query in tag.name:
                table_id = self.tag_box.insert_tag(tag)
                tag.table_id = table_id
        self.tag_box.reset_selection()

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()

    def go_to_tag(self):
        if len(self.treeview_neighbours.selection()) == 0:
            return
        table_id = self.treeview_neighbours.selection()[0]
        for tag, neighbour_id in self.neighbour_view_ids.items():
            if neighbour_id == table_id:
                self.searchbar.set_query(tag)
                self.search()

    def export_to_xlsx(self):
        try:
            self.counter.dump()
            os.startfile(os.path.join(os.getcwd(), 'results.xlsx'))
        except self.counter.NotCountedException:
            pass

    def switch_sorting_mode(self):
        def switch_sorting(table1, table2):
            for tag1, tag2 in zip(table1.values(), table2.values()):
                self.tag_box.item(tag1.table_id, text=tag2.name, values=tag2.uses_amount)
            for tag2, table_id in zip(table2.values(), self.tag_box.get_children()):
                tag2.table_id = table_id

        match self.sorting_switch.mode:
            case "Usages":
                switch_sorting(self.counter.tags_table, self.counter.tags_table_alphabetically)
            case "Alphabetically":
                switch_sorting(self.counter.tags_table_alphabetically, self.counter.tags_table)
        self.sorting_switch.switch_mode()
        self.tag_box.reset_selection()

if __name__ == "__main__":
    WindowInterface()