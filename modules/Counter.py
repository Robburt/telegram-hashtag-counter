import json
from modules import Table, Message, Tag

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
                uses_per_tag[appended_tag] = Tag.Tag(appended_tag)
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

                message = Message.Message(msg_json['id'], msg_json['date'])
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

        table = Table.Table()
        table.print_dict(self.tags_table, 'Tag', 'Tag uses')
        table.print_dict({key: value for key, value in sorted(self.tags_table.items())}, 'Alphabetic tags', 'Tag uses')
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