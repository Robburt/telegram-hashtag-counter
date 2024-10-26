import re
import os
import sys
import xlsxwriter
from bs4 import BeautifulSoup

save_dir = "results.xlsx"
hashtag_regex = "[\n>]#[^< ]+[<\n]"
if sys.argv[1] is not None:
    messages_dir = sys.argv[1]
else:
    messages_dir = ''

tag_rates = {}
file_names = [messages_dir + "\\" + i for i in os.listdir(messages_dir) if i[-5:] == '.html']
for file_name in file_names:
    with open(file_name, encoding='utf-8') as file:
        contents = file.read()
    soup = BeautifulSoup(contents, 'html.parser')
    soup = str(soup)
    tags = re.findall(hashtag_regex, soup)
    for i in tags:
        tag = str.lower(i[2:-1])
        if tag not in tag_rates.keys():
            tag_rates[tag] = 0
        tag_rates[tag] += 1
    print(f'{file_name} completed')

tag_rates = sorted(tag_rates.items(), key=lambda x:x[1], reverse=True)
tag_rates = dict(tag_rates)

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