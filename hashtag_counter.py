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
            if type(value) is Tag:
                value = value.uses_amount
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
        self.tag_info = tk.Frame(self.root, border=20)

        self.welcome_label = tk.Label(self.contents, text="Welcome to Telegram Hashtag Counter.\nPlease select a path to the result.json file below.", font=("Arial", 15))
        self.welcome_label.grid(row=0, columnspan=3, pady=20)

        self.results_dir = tk.StringVar()
        self.directory_entry = tk.Entry(self.contents, textvariable=self.results_dir, width=70)
        self.directory_entry.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S)

        self.directory_browse = tk.Button(self.contents, text="Browse...", command=self.show_browse_window)
        self.directory_browse.grid(row=1, column=1, sticky=tk.W, padx=5)

        self.start = tk.Button(self.contents, text="Count", command=self.count, width=20)
        self.start.grid(row=1, column=2, sticky=tk.E)

        self.tag_box = tk.Listbox(self.contents, height=20)
        self.tag_box.grid(row=2, column=0, columnspan=3, sticky=tk.W + tk.E, pady=10)
        self.tag_box_scrollbar = tk.Scrollbar(self.contents, orient=tk.VERTICAL, command=self.tag_box.yview)
        self.tag_box.configure(yscrollcommand=self.tag_box_scrollbar.set)
        self.tag_box_scrollbar.grid(row=2, column=3, sticky=tk.N + tk.S, pady=10)

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
            self.counter = Counter()
            self.counter.count(self.results_dir.get())
        except FileNotFoundError:
            messagebox.showerror(title="File not found", message="Unable to find result.json file")
            return
        self.export_button.grid(row=3, column=0, sticky=tk.W)
        tags = [*self.counter.tags_table.keys()]
        tags_var = tk.StringVar(value=tags)
        self.tag_box['listvariable'] = tags_var
        self.tag_box.bind("<<ListboxSelect>>", lambda e: self.on_selection_change(self.tag_box.curselection()))
        self.tag_box.selection_set(0)
        self.on_selection_change(self.tag_box.curselection())

    def on_selection_change(self, selection):
        tag = self.counter.tags_table[self.tag_box.get(selection)]
        tag_info_dict = tag.dictionary
        tag.set_neighbours(self.counter.messages)
        tag_neighbours_dict = tag.neighbours
        tag_info_labels = []
        for key, value in tag_info_dict.items():
            tag_info_labels.append(tk.Label(self.tag_info, text=f"{key}: {value}", width=50, anchor=tk.W))
            tag_info_labels[-1].grid(row=len(tag_info_labels)-1, column=0, sticky=tk.W)
        tag_info_labels.append(tk.Label(self.tag_info, text=f"Tags most commonly used with this tag:", width=50, anchor=tk.W))
        tag_info_labels[-1].grid(row=len(tag_info_labels)-1, column=0, sticky=tk.W)
        top10 = 15
        for key, value in tag_neighbours_dict.items():
            tag_info_labels.append(tk.Label(self.tag_info, text=f"{key}: {value.uses_amount}", width=50, anchor=tk.W))
            tag_info_labels[-1].grid(row=len(tag_info_labels)-1, column=0, sticky=tk.W)
            top10 -= 1
            if not top10:
                break
        if top10 > 0:
            for i in range(top10):
                tag_info_labels.append(tk.Label(self.tag_info, text="", width=50, anchor=tk.W))
                tag_info_labels[-1].grid(row=len(tag_info_labels)-1, column=0, sticky=tk.W)

    def export_to_xlsx(self):
        try:
            self.counter.dump()
            os.startfile(os.path.join(os.getcwd(), 'results.xlsx'))
        except self.counter.NotCountedException:
            pass


class Counter:
    def __init__(self):
        self.messages = []
        self.tags_table = {}
        self.artists_table = {}
        self.forwards_table = {}

    def count(self, directory):
        def add_to_upt(appended_tag, current_message):
            use_date = current_message['date']
            if appended_tag not in uses_per_tag.keys():
                uses_per_tag[appended_tag] = Tag(appended_tag)
            uses_per_tag[appended_tag].increment(use_date)

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
                    add_to_upt(source, message)
                    forwards.append(source)
                else:
                    artist = None
                    tags = []
                    for text_entity in message['text_entities']:
                        if text_entity['type'] == 'plain':
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
                    self.messages.append(Message(message['id'], message['date'], artist, tags))

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

        table = Table()
        table.print_dict(self.tags_table, 'Tag', 'Tag uses')
        table.print_dict(additional_information, '', '')
        table.print_groups(self.tags_table)
        if self.artists_table:
            table.print_dict(self.artists_table, 'Author', 'Works')
            table.print_dict(additional_information_authors, '', '')
        if self.forwards_table:
            table.print_dict(self.forwards_table, 'Reposted from', 'Reposts amount')
        table.close_workbook()

    class NotCountedException(Exception):
        pass

class Message:
    def __init__(self, msg_id, date, author, tags):
        self.id = msg_id
        self.date = date
        self.author = author
        self.tags = tags

class Tag:
    def __init__(self, name):
        self.name = name
        self.uses = []
        self.neighbours = {}

    @property
    def uses_amount(self):
        return len(self.uses)

    @property
    def dictionary(self):
        return {
            'name': self.name,
            'uses': self.uses_amount,
            'first use': self.uses[0],
            'last use': self.uses[-1]
        }

    def increment(self, use_date):
        self.uses.append(use_date)

    def set_neighbours(self, messages):
        def add_to_upt(appended_tag, message_date):
            if appended_tag not in uses_per_tag.keys():
                uses_per_tag[appended_tag] = Tag(appended_tag)
            uses_per_tag[appended_tag].increment(message_date)

        uses_per_tag = {}
        for message in messages:
            if self.name in message.tags:
                for tag in message.tags:
                    if tag != self.name:
                        add_to_upt(tag, message.date)

        if not uses_per_tag:
            return

        max_uses = max(list(i.uses_amount for i in uses_per_tag.values()))
        tags_per_uses = {str(i): [] for i in range(max_uses, 0, -1)}
        for tag in uses_per_tag.values():
            tags_per_uses[str(tag.uses_amount)].append(tag)

        for uses, tag_list in tags_per_uses.items():
            if not tag_list:
                continue
            tags_alphabetically = sorted(tag_list, key=lambda x: x.name)
            for tag in tags_alphabetically:
                self.neighbours[tag.name] = tag

if __name__ == "__main__":
    WindowInterface()