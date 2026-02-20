class Message:
    def __init__(self, msg_id, date):
        self.id = msg_id
        self.date = date
        self.text = ''
        self.author = None
        self.tags = None
        self.source = None

    def __repr__(self):
        return f"Message {self.date} '{self.text[:70]}...'"

    def add_source(self, source):
        self.source = source

    def add_artist(self, artist):
        self.author = artist

    def add_tags(self, tags):
        self.tags = tags

    def add_text(self, text):
        self.text += text
