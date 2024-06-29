class Note(object):
    def __init__(self, title, content, uuid, notes, state, data):
        self.title = title
        self.content = content
        self.uuid = uuid
        self.notes = notes
        self.state = state
        self.data = data