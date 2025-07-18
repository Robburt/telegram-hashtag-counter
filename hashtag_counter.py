import os
import sys
import json
import xlsxwriter


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


class Interface:
    def __init__(self):
        self.commands = {
            'load': self.load,
            'count': self.count,
            'dump': self.dump,
            'exit': self.exit
        }
        self.running = False
        self.json = None
        self.tags_table = {}

    def load(self, json_dir=''):
        directory = os.path.join(json_dir[0], 'result.json')
        try:
            with open(directory, encoding='utf-8') as file:
                self.json = json.load(file)
            print("Loaded.")
        except FileNotFoundError:
            print(f"No 'result.json' file in {directory}")

    def count(self):
        if self.json is None:
            print("JSON not loaded!")
            return

        uses_per_tag = {}
        for message in self.json['messages']:
            for text_entity in message['text_entities']:
                if text_entity['type'] == 'hashtag':
                    tag = text_entity['text'][1:]
                    if tag not in uses_per_tag.keys():
                        uses_per_tag[tag] = 0
                    uses_per_tag[tag] += 1

        # sort by amount
        uses_per_tag = dict(sorted(uses_per_tag.items(), key=lambda x: x[1], reverse=True))

        # sort each amount alphabetically
        tags_per_uses = {}  # { N : [list of tags used N times] }
        self.tags_table = {}
        for tag, uses in uses_per_tag.items():
            uses_str = str(uses)
            if uses_str not in tags_per_uses.keys():
                tags_per_uses[uses_str] = []
            tags_per_uses[uses_str].append(tag)
        for uses, tags in tags_per_uses.items():
            tags_sorted = sorted(tags)
            for tag in tags_sorted:
                self.tags_table[tag] = uses

    def tag_info(self, tag):
        print(f"{tag} - {self.tags_table[tag]}")

    def dump(self):
        if len(self.tags_table.keys()) < 1:
            print("Tags not counted!")
            return

        additional_information = {
            "Tags total": len(self.tags_table.keys()),
            "Tag uses total": sum(list(map(int, self.tags_table.values())))
        }

        table = Table()
        table.print_dict(self.tags_table, 'Tag', 'Tag uses')
        table.print_dict(additional_information, '', '')
        table.print_groups(self.tags_table)
        table.close_workbook()

    def exit(self):
        self.running = False

    def run(self):
        print("Telegram Hashtag Counter tool running.")
        self.running = True
        while self.running:
            input_command = input(">")
            input_command = input_command.split()
            try:
                cmd, args = input_command[0], input_command[1:]
                if args:
                    self.commands[cmd](args)
                else:
                    self.commands[cmd]()
            except KeyError:
                print("Invalid command.")


if __name__ == "__main__":
    Counter = Interface()
    Counter.run()