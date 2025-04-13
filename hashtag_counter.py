import os
import sys
import time
import xlsxwriter
from bs4 import BeautifulSoup

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
            self.print_dict(print_query, group_name, '')


    def close_workbook(self):
        self.workbook.close()

def progress_bar(current, total, bar_length=20):
    fraction = current / total
    arrow = int(fraction * bar_length - 1) * '-' + '>'
    padding = int(bar_length - len(arrow)) * ' '
    ending = '\n' if current == total else '\r'
    print(f'Progress: [{arrow}{padding}] {int(fraction * 100)}%', end=ending)


def counter(history_dir, scan_amount):
    print(f"Counting hashtags at {history_dir if history_dir is not None else 'current directory'}...")

    uses_per_tag = {}
    file_names = [i for i in os.listdir(history_dir if history_dir is not None else None) if i[-5:] == '.html']
    progress_bar(0, len(file_names[:scan_amount]))
    for n, file_name in enumerate(file_names[:scan_amount]):
        if history_dir is None:
            directory = file_name
        else:
            directory = os.path.join(history_dir, file_name)
        with open(directory, encoding='utf-8') as file:
            contents = file.read()
        soup = BeautifulSoup(contents, 'html.parser')
        for i in soup("a"):
            if i.string is not None:
                if i.string[0] == '#':
                    tag = str.lower(i.string[1:])
                    if tag not in uses_per_tag.keys():
                        uses_per_tag[tag] = 0
                    uses_per_tag[tag] += 1
        progress_bar(n, len(file_names))

    #sort by amount
    uses_per_tag = dict(sorted(uses_per_tag.items(), key=lambda x: x[1], reverse=True))

    #sort each amount alphabetically
    tags_per_uses = {} # { N : [list of tags used N times] }
    uses_per_tag_sorted = {}
    for tag, uses in uses_per_tag.items():
        uses_str = str(uses)
        if uses_str not in tags_per_uses.keys():
            tags_per_uses[uses_str] = []
        tags_per_uses[uses_str].append(tag)
    for uses, tags in tags_per_uses.items():
        tags_sorted = sorted(tags)
        for tag in tags_sorted:
            uses_per_tag_sorted[tag] = uses

    additional_information = {
        "Tags total": len(uses_per_tag_sorted.keys()),
        "Tag uses total": sum(list(map(int, uses_per_tag_sorted.values())))
    }

    table = Table()
    table.print_dict(uses_per_tag_sorted, 'Tag', 'Tag uses')
    table.print_dict(additional_information, '', '')
    table.print_groups(uses_per_tag_sorted)
    table.close_workbook()


if __name__ == "__main__":
    history_directory = sys.argv[1] if len(sys.argv) > 1 else None
    amount_to_scan = int(sys.argv[2]) if len(sys.argv) > 2 else None

    start_time = time.time()

    counter(history_directory, amount_to_scan)

    print(f"Counting completed in {round(time.time() - start_time, 2)} seconds")
