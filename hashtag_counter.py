import os
import json
import xlsxwriter
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


class Table:
    def __init__(self):
        self.save_dir = "results.xlsx"
        self.workbook = xlsxwriter.Workbook(self.save_dir)
        self.worksheet = self.workbook.add_worksheet()
        self.next_free_column = 0
        self.offset = 1

    def print_dict(self, dictionary, title1, title2):
        title_column_width = max([len(key) for key in dictionary.keys()])
        self.worksheet.set_column(self.next_free_column, self.next_free_column, title_column_width)
        self.worksheet.write(0, self.next_free_column, title1)
        self.worksheet.write(0, self.next_free_column + 1, title2)
        for row, key, value in zip(range(len(dictionary.keys())), dictionary.keys(), dictionary.values()):
            self.worksheet.write(row + self.offset, self.next_free_column, key)
            self.worksheet.write(row + self.offset, self.next_free_column + 1, value)
        self.next_free_column += 2

    def print_groups(self, dictionary):
        groups = {}
        with open("groups.txt") as f:
            for line in f:
                group_name, tags_in_group = line.split(": ")
                groups[group_name] = tags_in_group.split()
        for group_name, tag_list in groups.items():
            print_query = {}
            for tag, value in dictionary.items():
                if tag in tag_list:
                    print_query[tag] = value
            if len(print_query.keys()) > 0:
                self.print_dict(print_query, group_name, '')

    def close_workbook(self):
        self.workbook.close()


class WindowInterface:
    def __init__(self):

        self.counter = Counter()

        self.root = tk.Tk()
        self.root.title("Telegram Hashtag Counter - Alpha")

        self.contents = tk.Frame(self.root, border=10)
        self.tag_info = tk.Frame(self.root)

        self.welcome_label = tk.Label(self.contents, text="Welcome to Telegram Hashtag Counter.\nPlease select a path to the result.json file below.", font=("Arial", 15))
        self.welcome_label.grid(row=0, columnspan=3, pady=20)

        self.results_dir = tk.StringVar()
        self.directory_entry = tk.Entry(self.contents, textvariable=self.results_dir, width=70)
        self.directory_entry.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S)

        self.directory_browse = tk.Button(self.contents, text="Browse...", command=self.show_browse_window)
        self.directory_browse.grid(row=1, column=1, sticky=tk.W, padx=5)

        self.start = tk.Button(self.contents, text="Count", command=self.count, width=20)
        self.start.grid(row=1, column=2, sticky=tk.E)

        self.results_box = tk.Listbox(self.contents, height=20, width=100)
        self.results_box.grid(row=2, column=0, columnspan=3, sticky=tk.W+tk.E, pady=10)

        self.scrollbar = tk.Scrollbar(self.contents, orient=tk.VERTICAL, command=self.results_box.yview)
        self.results_box.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=2, column=3, sticky=tk.N+tk.S, pady=10)

        self.export_button = tk.Button(self.contents, text="Export to Excel", command=self.export_to_xlsx, width=20)

        self.contents.grid(row=0, column=0)
        self.tag_info.grid(row=0, column=1, sticky=tk.N)

        self.root.update_idletasks()
        self.root.minsize(self.root.winfo_reqwidth(), self.root.winfo_reqheight())

        self.root.mainloop()

    def show_browse_window(self):
        results_dir = filedialog.askopenfile(filetypes=[('JSON', '.json')])
        if results_dir is not None:
            self.results_dir.set(results_dir.name)

    def count(self):
        try:
            self.counter.count(self.results_dir.get())
        except FileNotFoundError:
            messagebox.showerror(title="File not found", message="Unable to find result.json file")
            return
        self.export_button.grid(row=3, column=0, sticky=tk.W)
        tags = [*self.counter.tags_table.keys()]
        tags_var = tk.StringVar(value=tags)
        self.results_box['listvariable'] = tags_var
        self.results_box.bind("<<ListboxSelect>>", lambda e: self.on_selection_change(self.results_box.curselection()))
        self.results_box.selection_set(0)
        self.on_selection_change(self.results_box.curselection())

    def on_selection_change(self, selection):
        tag_info_dict = {
            "Uses": self.counter.tags_table[self.results_box.get(selection)]
        }
        tag_info_labels = []
        for key, value in tag_info_dict.items():
            tag_info_labels.append(tk.Label(self.tag_info, text=f"{key}: {value}", width=100))
            tag_info_labels[-1].grid(row=len(tag_info_labels)-1, column=0, sticky=tk.W)

    def export_to_xlsx(self):
        try:
            self.counter.dump()
            os.startfile(os.path.join(os.getcwd(), 'results.xlsx'))
        except self.counter.NotCountedException:
            pass


class Counter:
    def __init__(self):
        self.tags_table = {}
        self.artists_table = {}
        self.forwards_table = {}

    def count(self, directory):
        def add_to_upt(appended_tag):
            if appended_tag not in uses_per_tag.keys():
                uses_per_tag[appended_tag] = 0
            uses_per_tag[appended_tag] += 1

        with open(directory, encoding='utf-8') as file:
            results = json.load(file)

        uses_per_tag = {}
        artists = []
        forwards = []
        for message in results['messages']:
            if message['type'] == "message":
                next_is_artist = False

                if 'forwarded_from' in message.keys():
                    source = message['forwarded_from']
                    if source is None:
                        source = 'Deleted account'
                    add_to_upt(source)
                    forwards.append(source)
                else:
                    for text_entity in message['text_entities']:
                        if text_entity['type'] == 'plain':
                            if text_entity['text'][-3:] == "by ":
                                next_is_artist = True

                        if text_entity['type'] == 'mention' and next_is_artist:
                            tag = text_entity['text'][1:].lower()
                            add_to_upt(tag)
                            artists.append(tag)
                            next_is_artist = False

                        if text_entity['type'] == 'hashtag':
                            tag = text_entity['text'][1:].lower()
                            add_to_upt(tag)
                            if next_is_artist:
                                artists.append(tag)
                                next_is_artist = False

        # sort by amount
        uses_per_tag = dict(sorted(uses_per_tag.items(), key=lambda x: x[1], reverse=True))

        # sort each amount alphabetically
        tags_per_uses = {}  # { N : [list of tags used N times] }
        for tag, uses in uses_per_tag.items():
            uses_str = str(uses)
            if uses_str not in tags_per_uses.keys():
                tags_per_uses[uses_str] = []
            tags_per_uses[uses_str].append(tag)
        for uses, tags in tags_per_uses.items():
            tags_sorted = sorted(tags)
            for tag in tags_sorted:
                if tag in forwards:
                    self.forwards_table[tag] = uses
                elif tag in artists:
                    self.artists_table[tag] = uses
                else:
                    self.tags_table[tag] = uses

    def dump(self):
        if not self.tags_table:
            raise self.NotCountedException

        additional_information = {
            "Tags total": len(self.tags_table.keys()),
            "Tag uses total": sum(list(map(int, self.tags_table.values())))
        }

        additional_information_authors = {
            "Authors total": len(self.artists_table.keys()),
            "Credited posts": sum(list(map(int, self.artists_table.values())))
        }

        table = Table()
        table.print_dict(self.tags_table, 'Tag', 'Tag uses')
        table.print_dict(additional_information, '', '')
        table.print_groups(self.tags_table)
        table.print_dict(self.artists_table, 'Author', 'Works')
        table.print_dict(additional_information_authors, '', '')
        table.print_dict(self.forwards_table, 'Reposted from', 'Reposts amount')
        table.close_workbook()

    class NotCountedException(Exception):
        pass


if __name__ == "__main__":
    WindowInterface()