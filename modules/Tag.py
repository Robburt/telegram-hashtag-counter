class Tag:
    def __init__(self, name):
        self.name = name
        self.messages = []
        self.neighbours = {}
        self.table_id = ''

    def __repr__(self):
        return f"Tag object '{self.name}'"

    @property
    def uses_amount(self):
        return len(self.messages)

    @property
    def dictionary(self):
        return {
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
                if len(message.tags) == 1:
                    add_to_upt("/Used alone/", message)
                else:
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
