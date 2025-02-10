import os
import sys
import time
import xlsxwriter
from bs4 import BeautifulSoup

class Table:
    def __init__(self, save_dir):
        self.workbook = xlsxwriter.Workbook(save_dir)
        self.worksheet = self.workbook.add_worksheet()
        self.next_free_column = 0

    def print_dict(self, dictionary):
        title_column_width = max([len(key) for key in dictionary.keys()])
        self.worksheet.set_column(self.next_free_column, self.next_free_column, title_column_width)
        for row, key, value in zip(range(len(dictionary.keys())), dictionary.keys(), dictionary.values()):
            self.worksheet.write(row, self.next_free_column, key)
            self.worksheet.write(row, self.next_free_column + 1, value)
        self.next_free_column += 2

    def close_workbook(self):
        self.workbook.close()

def progress_bar(current, total, bar_length=20):
    fraction = current / total
    arrow = int(fraction * bar_length - 1) * '-' + '>'
    padding = int(bar_length - len(arrow)) * ' '
    ending = '\n' if current == total else '\r'
    print(f'Progress: [{arrow}{padding}] {int(fraction * 100)}%', end=ending)


def counter(messages_dir, scan_amount):
    save_dir = "results.xlsx"
    print(f"Counting hashtags at {messages_dir if messages_dir is not None else 'here'}")
    start_time = time.time()

    tag_rates = {}
    file_names = [i for i in os.listdir(messages_dir if messages_dir is not None else None) if i[-5:] == '.html']
    progress_bar(0, len(file_names[:scan_amount]))
    for n, file_name in enumerate(file_names[:scan_amount]):
        if messages_dir is None:
            directory = file_name
        else:
            directory = os.path.join(messages_dir, file_name)
        with open(directory, encoding='utf-8') as file:
            contents = file.read()
        soup = BeautifulSoup(contents, 'html.parser')
        for i in soup("a"):
            if i.string is not None:
                if i.string[0] == '#':
                    tag = str.lower(i.string[1:])
                    if tag not in tag_rates.keys():
                        tag_rates[tag] = 0
                    tag_rates[tag] += 1
        progress_bar(n, len(file_names))

    #sort by amount
    tag_rates = dict(sorted(tag_rates.items(), key=lambda x: x[1], reverse=True))

    #result = { "amount_of_tag" : [tags with this amount] }
    result = {}
    tag_list = {}
    for tag_name, tag_amount in tag_rates.items():
        ta = str(tag_amount)
        if ta not in result.keys():
            result[ta] = []
        result[ta].append(tag_name)
    for tag_amount, tag_name_list in result.items():
        tag_name_list_sorted = sorted(tag_name_list)
        for tag_name in tag_name_list_sorted:
            tag_list[tag_name] = tag_amount

    additional_information = {
        "Tags total": len(tag_list.keys()),
        "Tag uses total": sum(list(map(int, tag_list.values())))
    }

    table = Table(save_dir)
    table.print_dict(tag_list)
    table.print_dict(additional_information)
    table.close_workbook()

    print(f"Counting completed in {round(time.time() - start_time, 2)} seconds, data saved at {save_dir}")


if __name__ == "__main__":
    history_directory = sys.argv[1] if len(sys.argv) > 1 else None
    files_to_scan = int(sys.argv[2]) if len(sys.argv) > 2 else None

    counter(history_directory, files_to_scan)
