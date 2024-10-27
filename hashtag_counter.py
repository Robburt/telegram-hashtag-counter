import re
import os
import sys
import time
import xlsxwriter
from bs4 import BeautifulSoup


def progress_bar(current, total, bar_length=20):
    fraction = current / total
    arrow = int(fraction * bar_length - 1) * '-' + '>'
    padding = int(bar_length - len(arrow)) * ' '
    ending = '\n' if current == total else '\r'
    print(f'Progress: [{arrow}{padding}] {int(fraction * 100)}%', end=ending)


def counter(messages_dir, scan_amount):
    save_dir = "results.xlsx"
    hashtag_regex = "[\n>]#[^< ]+[<\n]"

    print(f"Counting hashtags at {messages_dir}")
    start_time = time.time()

    tag_rates = {}
    file_names = [messages_dir + "\\" + i for i in os.listdir(messages_dir) if i[-5:] == '.html']
    progress_bar(0, len(file_names))
    for n, file_name in enumerate(file_names[:scan_amount]):
        with open(file_name, encoding='utf-8') as file:
            for raw_tag in re.finditer(hashtag_regex, str(BeautifulSoup(file.read(), 'html.parser'))):
                tag = str.lower(raw_tag[0][2:-1])
                if tag not in tag_rates.keys():
                    tag_rates[tag] = 0
                tag_rates[tag] += 1
        progress_bar(n, len(file_names))

    tag_rates = dict(sorted(tag_rates.items(), key=lambda x: x[1], reverse=True))

    result = {}
    for tag_name, tag_amount in tag_rates.items():
        ta = str(tag_amount)
        if ta not in result.keys():
            result[ta] = []
        result[ta].append(tag_name)
    for tag_amount, tag_name_list in result.items():
        result[tag_amount] = sorted(tag_name_list)

    workbook = xlsxwriter.Workbook(save_dir)
    worksheet = workbook.add_worksheet()
    biggest_tag_length = 0
    for tag_name_list in result.values():
        for tag_name in tag_name_list:
            if len(tag_name) > biggest_tag_length:
                biggest_tag_length = len(tag_name)
    worksheet.set_column(0, 0, biggest_tag_length)
    row = 0
    for tag_amount, tag_name_list in result.items():
        for tag_name in tag_name_list:
            worksheet.write(row, 0, tag_name)
            worksheet.write(row, 1, tag_amount)
            row += 1

    additional_information = {
        "Tags total": sum([len(i) for i in result.values()]),
        "Tag uses total": sum(list(map(int, result.keys())))
    }
    worksheet.set_column(3, 3, len(max(additional_information.keys())))
    row = 0
    for key, value in additional_information.items():
        worksheet.write(row, 2, key)
        worksheet.write(row, 3, value)
        row += 1
    workbook.close()

    print(f"Counting completed in {round(time.time() - start_time, 2)} seconds, data saved at {save_dir}")


if __name__ == "__main__":
    history_directory = sys.argv[1] if len(sys.argv) > 1 else ''
    files_to_scan = int(sys.argv[2]) if len(sys.argv) > 2 else None

    counter(history_directory, files_to_scan)
