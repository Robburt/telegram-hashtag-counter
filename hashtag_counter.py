import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from modules import Table, Message, Tag, UI

class WindowInterface:
    def __init__(self):

        self.counter = Counter()

        self.root = tk.Tk()
        self.root.title("Telegram Hashtag Counter")

        self.menubar = UI.Menubar(self.root)
        self.root['menu'] = self.menubar

        self.contents = tk.Frame(self.root, border=10)
        self.tag_info = tk.Frame(self.root, border=20)

        self.welcome_label = tk.Label(self.contents, text="Welcome to Telegram Hashtag Counter.\nPlease select a path to the result.json file below.", font=("Arial", 15))
        self.welcome_label.grid(row=0, columnspan=3, pady=20)

        self.results_dir = ''
        self.open_dir = tk.Button(self.contents, text="Open...", command=self.open_file_command, width=20)
        self.open_dir.grid(row=1, column=0, sticky=tk.W, padx=5)

        self.displaying_full_table = True
        self.search_frame = tk.Frame(self.contents)
        self.search_bar = tk.Entry(self.search_frame)
        self.search_button = tk.Button(self.search_frame, text="Search", command=self.search, width=10)
        self.search_frame.grid(row=1, column=2, sticky=tk.E)
        self.search_bar.grid(row=0, column=0, sticky=tk.E, padx=10)
        self.search_button.grid(row=0, column=1, sticky=tk.E)

        self.tag_box = ttk.Treeview(self.contents, height=20, columns="uses")
        self.tag_box.column("uses", width=30)
        self.tag_box.heading("uses", text='Usages')
        self.tag_box.grid(row=2, column=0, columnspan=3, sticky=tk.W + tk.E, pady=10)
        self.tag_box_scrollbar = tk.Scrollbar(self.contents, orient=tk.VERTICAL, command=self.tag_box.yview)
        self.tag_box.configure(yscrollcommand=self.tag_box_scrollbar.set)
        self.tag_box_scrollbar.grid(row=2, column=3, sticky=tk.N + tk.S, pady=10)
        self.tag_box.bind("<<TreeviewSelect>>", lambda e: self.on_selection_change(self.tag_box.selection()))

        self.treeview_neighbours = ttk.Treeview(self.tag_info, columns="uses", height=20)
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
            self.counter = Counter()
            self.counter.count(self.results_dir)
        except FileNotFoundError:
            messagebox.showerror(title="File not found", message="Unable to find result.json file")
            return

        self.tag_box.delete(*self.tag_box.get_children())
        for tag in self.counter.tags_table.values():
            table_id = self.tag_box.insert('', 'end', text=tag.name, values=tag.uses_amount)
            tag.table_id = table_id
        self.tag_box.selection_set(self.tag_box.get_children()[0])

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
        self.treeview_neighbours.delete(*self.treeview_neighbours.get_children())
        self.treeview_neighbours.grid(row=len(tag_info_labels), column=0, sticky=tk.W + tk.E)
        self.treeview_neighbours_scrollbar.grid(row=len(tag_info_labels), column=1, sticky=tk.N + tk.S, pady=10)
        if not tag.has_defined_neighbours:
            tag.set_neighbours(self.counter.messages)
        self.neighbour_view_ids = {i : '' for i in tag.neighbours.keys()}
        for neighbour in tag.neighbours.values():
            neighbour_id = self.treeview_neighbours.insert('', 'end', text=neighbour.name, values=neighbour.uses_amount)
            self.neighbour_view_ids[neighbour.name] = neighbour_id

    def search(self):
        if self.search_bar.get() == '' and self.displaying_full_table:
            return
        self.displaying_full_table = self.search_bar.get() == ''
        found_anything = False
        for tag in self.counter.tags_table.values():
            if self.search_bar.get() in tag.name:
                if not found_anything:
                    self.tag_box.delete(*self.tag_box.get_children())
                found_anything = True
                table_id = self.tag_box.insert('', 'end', text=tag.name, values=tag.uses_amount)
                tag.table_id = table_id
        self.tag_box.selection_set(self.tag_box.get_children()[0])

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
                self.search_bar.delete(0, tk.END)
                self.search_bar.insert(0, tag)
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
        self.tag_box.selection_set(self.tag_box.get_children()[0])

class Counter:
    def __init__(self):
        self.channel_id = 0
        self.messages = []
        self.tags_table = {}
        self.tags_table_alphabetically = {}
        self.artists_table = {}
        self.forwards_table = {}

    def count(self, directory):
        def add_to_upt(appended_tag, message):
            if appended_tag not in uses_per_tag.keys():
                uses_per_tag[appended_tag] = Tag.Tag(appended_tag)
            uses_per_tag[appended_tag].add_message(message)

        with open(directory, encoding='utf-8') as file:
            results = json.load(file)
        self.channel_id = results['id']

        uses_per_tag = {}
        artists = []
        forwards = []
        for msg_json in results['messages']:
            if msg_json['type'] == "message":
                next_is_artist = False

                message = Message.Message(msg_json['id'], msg_json['date'])
                if 'forwarded_from' in msg_json.keys():
                    source = msg_json['forwarded_from']
                    if source is None:
                        source = 'Deleted account'
                    message.add_source(source)
                    add_to_upt(source, message)
                    forwards.append(source)
                else:
                    artist = None
                    tags = []
                    for text_entity in msg_json['text_entities']:

                        if text_entity['type'] == 'plain':
                            message.add_text(text_entity['text'])
                            if text_entity['text'][-3:] == "by ":
                                next_is_artist = True

                        if text_entity['type'] == 'mention' and next_is_artist:
                            tag = text_entity['text'][1:].lower()
                            add_to_upt(tag, message)
                            artist = tag
                            next_is_artist = False

                        if text_entity['type'] == 'hashtag':
                            tag = text_entity['text'][1:].lower()
                            add_to_upt(tag, message)
                            if next_is_artist:
                                artist = tag
                                next_is_artist = False
                            else:
                                tags.append(tag)

                    if artist is not None:
                        artists.append(artist)
                    message.add_artist(artist)
                    message.add_tags(tags)
                    self.messages.append(message)


        max_uses = max(list(i.uses_amount for i in uses_per_tag.values()))
        tags_per_uses = {str(i): [] for i in range(max_uses, 0, -1)}
        for tag in uses_per_tag.values():
            tags_per_uses[str(tag.uses_amount)].append(tag)

        # assembling final lists
        for uses, tag_list in tags_per_uses.items():
            if not tag_list:
                continue
            tags_alphabetically = sorted(tag_list, key=lambda x: x.name)
            for tag in tags_alphabetically:
                if tag.name in forwards:
                    self.forwards_table[tag.name] = tag
                elif tag.name in artists:
                    self.artists_table[tag.name] = tag
                else:
                    self.tags_table[tag.name] = tag

        # alphabetically sort tags table
        self.tags_table_alphabetically = {key: value for key, value in sorted(self.tags_table.items())}


    def dump(self):
        if not self.tags_table:
            raise self.NotCountedException

        additional_information = {
            "Tags total": len(self.tags_table.keys()),
            "Tag uses total": sum(i.uses_amount for i in self.tags_table.values())
        }

        additional_information_authors = {
            "Authors total": len(self.artists_table.keys()),
            "Tag uses total": sum(i.uses_amount for i in self.artists_table.values())
        }

        table = Table.Table()
        table.print_dict(self.tags_table, 'Tag', 'Tag uses')
        table.print_dict({key: value for key, value in sorted(self.tags_table.items())}, 'Alphabetic tags', 'Tag uses')
        table.print_dict(additional_information, '', '')
        table.print_groups(self.tags_table)
        if self.artists_table:
            table.print_dict(self.artists_table, 'Author', 'Works')
            table.print_dict(additional_information_authors, '', '')
        if self.forwards_table:
            table.print_dict(self.forwards_table, 'Reposted from', 'Reposts amount')
        table.close_workbook()

    def find_by_id(self, table_id):
        for tag in self.tags_table.values():
            if tag.table_id == table_id:
                return tag

    class NotCountedException(Exception):
        pass

if __name__ == "__main__":
    WindowInterface()