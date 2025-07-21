import os
import json
import xlsxwriter
import tkinter as tk
from tkinter import filedialog


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
        self.root = tk.Tk()
        self.root.title("Telegram Hashtag Counter - Alpha")

        self.welcome_label = tk.Label(self.root, text="Welcome to Telegram Hashtag Counter.\nPlease select a path to the result.json file below.")
        self.welcome_label.pack(pady=20)

        self.entry_frame = tk.Frame(self.root, border=20)

        self.results_dir = tk.StringVar()

        self.directory_entry = tk.Entry(self.entry_frame, textvariable=self.results_dir, width=100)
        self.directory_entry.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)

        self.directory_browse = tk.Button(self.entry_frame, text="Browse...", command=self.show_browse_window)
        self.directory_browse.grid(row=0, column=1, sticky=tk.W+tk.E)

        self.entry_frame.pack()

        self.start = tk.Button(self.root, text="Count", command=self.count)
        self.start.pack(pady=20)

        self.root.mainloop()

    def show_browse_window(self):
        results_dir = filedialog.askopenfile(filetypes=[('JSON', '.json')])
        self.results_dir.set(results_dir.name)

    def count(self):
        count_all_tags(self.results_dir.get())
        os.startfile(os.path.join(os.getcwd(), 'results.xlsx'))


def count_all_tags(directory):
    with open(directory, encoding='utf-8') as file:
        results = json.load(file)

    tags_table = {}
    author_tags = {}
    forwards_dict = {}

    uses_per_tag = {}
    authors = []
    forwards = []
    for message in results['messages']:
        if message['type'] == "message":
            next_is_author = False

            if 'forwarded_from' in message.keys():
                source = message['forwarded_from']
                if source is None:
                    source = 'Deleted account'
                forwards.append(source)
                if source not in uses_per_tag.keys():
                    uses_per_tag[source] = 0
                uses_per_tag[source] += 1
            else:
                for text_entity in message['text_entities']:
                    if text_entity['type'] == 'plain':
                        if text_entity['text'][-3:] == "by ":
                            next_is_author = True

                    if text_entity['type'] == 'mention' and next_is_author:
                        tag = text_entity['text'][1:].lower()
                        if tag not in uses_per_tag.keys():
                            uses_per_tag[tag] = 0
                        uses_per_tag[tag] += 1
                        authors.append(tag)
                        next_is_author = False

                    if text_entity['type'] == 'hashtag':
                        tag = text_entity['text'][1:].lower()
                        if tag not in uses_per_tag.keys():
                            uses_per_tag[tag] = 0
                        uses_per_tag[tag] += 1
                        if next_is_author:
                            authors.append(tag)
                            next_is_author = False

    # sort by amount
    uses_per_tag = dict(sorted(uses_per_tag.items(), key=lambda x: x[1], reverse=True))

    # sort each amount alphabetically
    tags_per_uses = {}  # { N : [list of tags used N times] }
    tags_table = {}
    for tag, uses in uses_per_tag.items():
        uses_str = str(uses)
        if uses_str not in tags_per_uses.keys():
            tags_per_uses[uses_str] = []
        tags_per_uses[uses_str].append(tag)
    for uses, tags in tags_per_uses.items():
        tags_sorted = sorted(tags)
        for tag in tags_sorted:
            if tag in forwards:
                forwards_dict[tag] = uses
            elif tag in authors:
                author_tags[tag] = uses
            else:
                tags_table[tag] = uses

    additional_information = {
        "Tags total": len(tags_table.keys()),
        "Tag uses total": sum(list(map(int, tags_table.values())))
    }

    additional_information_authors = {
        "Authors total": len(author_tags.keys()),
        "Credited posts": sum(list(map(int, author_tags.values())))
    }

    table = Table()
    table.print_dict(tags_table, 'Tag', 'Tag uses')
    table.print_dict(additional_information, '', '')
    table.print_groups(tags_table)
    table.print_dict(author_tags, 'Author', 'Works')
    table.print_dict(additional_information_authors, '', '')
    table.print_dict(forwards_dict, 'Reposted from', 'Reposts ammount')
    table.close_workbook()


if __name__ == "__main__":
    WindowInterface()