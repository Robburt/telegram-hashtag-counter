import os
import json
import xlsxwriter
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from resources import custom


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

        self.tag_box = ttk.Treeview(self.contents, height=20, columns="uses")
        self.tag_box.column("uses", width=30)
        self.tag_box.heading("uses", text='Usages')
        self.tag_box.grid(row=2, column=0, columnspan=3, sticky=tk.W + tk.E, pady=10)
        self.tag_box_scrollbar = tk.Scrollbar(self.contents, orient=tk.VERTICAL, command=self.tag_box.yview)
        self.tag_box.configure(yscrollcommand=self.tag_box_scrollbar.set)
        self.tag_box_scrollbar.grid(row=2, column=3, sticky=tk.N + tk.S, pady=10)

        self.export_button = tk.Button(self.contents, text="Export to Excel", command=self.export_to_xlsx, width=20)
        self.export_button.grid(row=3, column=0, sticky=tk.W)

        self.sort_mode = "Usages"
        self.sort_mode_frame = tk.Frame(self.contents)
        self.sort_mode_text = tk.Label(self.sort_mode_frame, text="Sorting mode: ", font=("Arial", 10))
        self.sort_mode_button = tk.Button(self.sort_mode_frame, text=self.sort_mode, command=self.switch_sorting_mode, width=20)
        self.sort_mode_button['state'] = 'disabled'
        self.sort_mode_frame.grid(row=3, column=2, sticky=tk.E)
        self.sort_mode_text.grid(row=0, column=0, sticky=tk.E)
        self.sort_mode_button.grid(row=0, column=1, sticky=tk.E)

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

        for tag in self.counter.tags_table.values():
            table_id = self.tag_box.insert('', 'end', text=tag.name, values=tag.uses_amount)
            tag.table_id = table_id

        self.tag_box.bind("<<TreeviewSelect>>", lambda e: self.on_selection_change(self.tag_box.selection()))
        self.tag_box.selection_set("I001")
        self.on_selection_change(self.tag_box.selection())

        self.sort_mode_button['state'] = 'normal'

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
        if not tag.has_defined_neighbours:
            tag.set_neighbours(self.counter.messages)
        displayed_neighbours = 5
        for n, key in zip(range(displayed_neighbours), tag.neighbours.keys()):
            line(f"{n + 1} - {key}: {tag.neighbours[key].uses_amount}")
        blank_lines_amount = displayed_neighbours - len(tag.neighbours.keys())
        if blank_lines_amount > 0:
            for _ in range(blank_lines_amount):
                line("")

        # Links to last posts
        displayed_posts = 1
        current_post = 0
        tag_info_labels.append(tk.Label(self.tag_info, text=f"Most recent posts:", width=50, anchor=tk.W))
        tag_info_labels[-1].grid(row=len(tag_info_labels)-1, column=0, sticky=tk.W)
        for message in reversed(tag.messages):
            current_post += 1
            link = f"https://t.me/c/{self.counter.channel_id}/{message.id}"
            text = message.text[:30].replace('\n', ' ')
            if not text:
                text = link
            #tk.Label(self.tag_info, text=' '*70).grid(row=len(tag_info_labels), column=0, sticky=tk.W)
            #tag_info_labels.append(tk.Label(self.tag_info, text=text, fg='blue', cursor='hand2'))
            #tag_info_labels[-1].pack()
            #tag_info_labels[-1].bind("<Button-1>", lambda e: webbrowser.open(link))
            custom.Linkbutton(self.tag_info, text=' '*70).grid(row=len(tag_info_labels), column=0, sticky=tk.W)
            tag_info_labels.append(custom.Linkbutton(self.tag_info, text=text, command=lambda: webbrowser.open(link)))
            tag_info_labels[-1].grid(row=len(tag_info_labels)-1, column=0, sticky=tk.W)
            if current_post == displayed_posts:
                break
        if current_post < displayed_posts:
            for i in range(displayed_posts - current_post):
                #tag_info_labels.append(tk.Label(self.tag_info, text=" "*70, fg='blue', cursor='hand2'))
                #tag_info_labels[-1].pack()
                #tag_info_labels[-1].bind("<Button-1>", lambda e: webbrowser.open(link))
                tag_info_labels.append(custom.Linkbutton(self.tag_info, text=' '*30))
                tag_info_labels[-1].grid(row=len(tag_info_labels)-1, column=0, sticky=tk.W)

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

        if self.sort_mode == 'Usages':
            self.sort_mode = 'Alphabetically'
            switch_sorting(self.counter.tags_table, self.counter.tags_table_alphabetically)
        else:
            self.sort_mode = 'Usages'
            switch_sorting(self.counter.tags_table_alphabetically, self.counter.tags_table)
        self.sort_mode_button.configure(text=self.sort_mode)


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
                uses_per_tag[appended_tag] = Tag(appended_tag)
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

                message = Message(msg_json['id'], msg_json['date'])
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

    def find_by_id(self, table_id):
        for tag in self.tags_table.values():
            if tag.table_id == table_id:
                return tag

    class NotCountedException(Exception):
        pass

class Message:
    def __init__(self, msg_id, date):
        self.id = msg_id
        self.date = date
        self.text = ''
        self.author = None
        self.tags = None
        self.source = None

    def add_source(self, source):
        self.source = source

    def add_artist(self, artist):
        self.author = artist

    def add_tags(self, tags):
        self.tags = tags

    def add_text(self, text):
        self.text += text

class Tag:
    def __init__(self, name):
        self.name = name
        self.messages = []
        self.neighbours = {}
        self.table_id = ''

    @property
    def uses_amount(self):
        return len(self.messages)

    @property
    def dictionary(self):
        return {
            'ID': self.table_id,
            'name': self.name,
            'uses': self.uses_amount,
            'first use': self.messages[0].date,
            'last use': self.messages[-1].date
        }

    @property
    def has_defined_neighbours(self):
        return len(self.neighbours) > 0

    def add_message(self, message):
        self.messages.append(message)

    def set_neighbours(self, messages):
        def add_to_upt(appended_tag, message):
            if appended_tag not in uses_per_tag.keys():
                uses_per_tag[appended_tag] = Tag(appended_tag)
            uses_per_tag[appended_tag].add_message(message)

        uses_per_tag = {}
        for message in messages:
            if self.name in message.tags:
                for tag in message.tags:
                    if tag != self.name:
                        add_to_upt(tag, message)

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