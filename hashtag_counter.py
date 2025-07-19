import os
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
        self.author_tags = {}
        self.forwards = {}

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
        authors = []
        forwards = []
        for message in self.json['messages']:
            if message['type'] == "message":
                next_is_author = False

                if 'forwarded_from' in message.keys():
                    source = message['forwarded_from']
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
        self.tags_table = {}
        for tag, uses in uses_per_tag.items():
            uses_str = str(uses)
            if uses_str not in tags_per_uses.keys():
                tags_per_uses[uses_str] = []
            tags_per_uses[uses_str].append(tag)
        for uses, tags in tags_per_uses.items():
            tags_sorted = sorted(tags)
            for tag in tags_sorted:
                if tag in forwards:
                    self.forwards[tag] = uses
                elif tag in authors:
                    self.author_tags[tag] = uses
                else:
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

        additional_information_authors = {
            "Authors total": len(self.author_tags.keys()),
            "Credited posts": sum(list(map(int, self.author_tags.values())))
        }

        table = Table()
        table.print_dict(self.tags_table, 'Tag', 'Tag uses')
        table.print_dict(additional_information, '', '')
        table.print_groups(self.tags_table)
        table.print_dict(self.author_tags, 'Author', 'Works')
        table.print_dict(additional_information_authors, '', '')
        table.print_dict(self.forwards, 'Reposted from', 'Reposts ammount')
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